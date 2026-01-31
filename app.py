from flask import Flask, render_template
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import io, base64, requests, os, logging
from matplotlib import font_manager, rcParams
# ---- 日本語フォント設定（Windows用・確実版）----
font_path = "C:/Windows/Fonts/meiryo.ttc"

if os.path.exists(font_path):
    font_prop = font_manager.FontProperties(fname=font_path)
    rcParams["font.family"] = font_prop.get_name()
else:
    print("⚠ 日本語フォントが見つかりません")

app = Flask(__name__)

CSV_URL = "https://raw.githubusercontent.com/Ryosuke2418/saddle2/main/saddle_data.csv"

logging.basicConfig(level=logging.INFO)

# ---- 時間帯を 10 / 15 / 20 時に丸める ----
def round_to_time(dt):
    if pd.isna(dt):
        return None
    target_hours = [10, 15, 20]
    hour = dt.hour
    closest = min(target_hours, key=lambda x: abs(x - hour))
    return f"{closest:02d}:00"

@app.route("/table")
def table_page():
    resp = requests.get(CSV_URL, headers={"Cache-Control": "no-cache"})
    resp.encoding = "utf-8"
    df = pd.read_csv(io.StringIO(resp.text))

    return render_template(
        "table.html",
        table=df.to_html(classes="table table-striped", index=False)
    )


@app.route("/")
def index():
    try:
        resp = requests.get(CSV_URL, headers={"Cache-Control": "no-cache"})
        resp.encoding = "utf-8"
        csv_text = resp.text

        if resp.status_code != 200 or not csv_text.strip():
            return render_template("index.html", table="<p>データがありません</p>", graph_url=None)

        df = pd.read_csv(io.StringIO(csv_text))
        app.logger.info("CSV columns: %s", list(df.columns))
        app.logger.info(df[["日時", "自転車の数", "天気", "曜日"]].head())

        df["日時"] = pd.to_datetime(df["日時"], errors="coerce")
        df["自転車の数"] = pd.to_numeric(df["自転車の数"], errors="coerce").fillna(0)
        df["日付"] = df["日時"].dt.date

        # ---- ▼ ここから平均化の処理 ▼ ----

        df["時間帯"] = df["日時"].apply(round_to_time)

        df_mean = (
            df.groupby(["日付", "曜日", "天気", "時間帯"], as_index=False)
            .agg({"自転車の数": "mean"})
        )

        df_mean["曜日天気"] = df_mean["曜日"] + " / " + df_mean["天気"]

        # ---- ▼ グラフ作成 ▼ ----
        plt.figure(figsize=(12, 6))

        for combo in df_mean["曜日天気"].unique():
            subset = df_mean[df_mean["曜日天気"] == combo]
            plt.plot(subset["時間帯"], subset["自転車の数"], label=combo, marker="o")

        plt.xlabel("時間帯（10時 / 15時 / 20時）")
        plt.ylabel("平均自転車数")
        plt.title("曜日 × 天気 × 時間帯の平均自転車数")
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()

        img = io.BytesIO()
        plt.savefig(img, format="png", bbox_inches="tight")
        img.seek(0)
        graph_url = base64.b64encode(img.getvalue()).decode()
        plt.close()

        return render_template(
    "index.html",
    graph_url=graph_url
)

    except Exception as e:
        app.logger.exception("エラー発生")
        return render_template("index.html",
                               table=f"<p>サーバーエラー: {str(e)}</p>",
                               graph_url=None)


if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=PORT)
