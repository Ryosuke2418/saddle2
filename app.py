from flask import Flask, render_template
import pandas as pd
import matplotlib.pyplot as plt
import io, base64, requests, os, logging

app = Flask(__name__)

# GitHub RAW の URL（そのまま使ってOK）
CSV_URL = "https://raw.githubusercontent.com/Ryosuke2418/saddle2/main/uploads/saddle_data.csv"

# ログ出力を見やすく
logging.basicConfig(level=logging.INFO)

@app.route("/")
def index():
    try:
        # GitHubから確実に取得（キャッシュ防止ヘッダ付け）
        resp = requests.get(CSV_URL, headers={"Cache-Control": "no-cache"})
        resp.encoding = "utf-8"
        csv_text = resp.text

        # CSV取得失敗
        if resp.status_code != 200 or not csv_text.strip():
            app.logger.warning("CSV取得失敗または内容が空: status=%s, length=%d", resp.status_code, len(csv_text))
            return render_template("index.html", table="<p>データがありません（CSV取得失敗）</p>", graph_url=None)

        # pandasで読み込み
        df = pd.read_csv(io.StringIO(csv_text))

        # デバッグ用: 今のカラムをログに出す（必要ならRenderログで確認）
        app.logger.info("CSV columns: %s", list(df.columns))

        # 必要な列が無ければ補完（安全策）
        required_cols = ["日時", "自転車の数", "天気", "気温", "曜日"]
        for c in required_cols:
            if c not in df.columns:
                df[c] = ""

        # 日時をdatetime化（失敗してもNaTになる）
        df["日時"] = pd.to_datetime(df["日時"], errors="coerce")

        # 解析用列を作成
        df["曜日"] = df["曜日"].fillna("")
        df["天気"] = df["天気"].fillna("")
        df["自転車の数"] = pd.to_numeric(df["自転車の数"], errors="coerce").fillna(0)
        df["曜日天気"] = df["曜日"] + " / " + df["天気"]

        # データが無ければ表だけ返す
        if df.empty or df["日時"].isna().all():
            app.logger.info("CSV に有効な日時データがありません")
            return render_template("index.html", table=df.to_html(classes="table table-striped", index=False), graph_url=None)

        # グラフ作成
        plt.figure(figsize=(12, 6))
        for combo in df["曜日天気"].unique():
            subset = df[df["曜日天気"] == combo]
            if subset.empty: 
                continue
            plt.plot(subset["日時"], subset["自転車の数"], label=str(combo), marker="o")

        plt.xlabel("日時")
        plt.ylabel("自転車の数")
        plt.title("曜日＋天気ごとの自転車混雑状況")
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()

        img = io.BytesIO()
        plt.savefig(img, format="png", bbox_inches="tight")
        img.seek(0)
        graph_url = base64.b64encode(img.getvalue()).decode()
        plt.close()

        return render_template("index.html",
                               table=df.to_html(classes="table table-striped", index=False),
                               graph_url=graph_url)

    except Exception as e:
        # 例外はログに出して、ユーザーにはエラーメッセージをやさしく出す
        app.logger.exception("アプリ内部で例外が発生しました")
        return render_template("index.html", table=f"<p>サーバーエラーが発生しました: {str(e)}</p>", graph_url=None)

if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=PORT)