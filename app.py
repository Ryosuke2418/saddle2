from flask import Flask, render_template
import pandas as pd
import matplotlib.pyplot as plt
import io, base64, requests

app = Flask(__name__)

CSV_URL = "https://raw.githubusercontent.com/Ryosuke2418/saddle2/main/uploads/saddle_data.csv"

@app.route("/")
def index():
    # GitHubからCSVを強制的に最新で取得
    response = requests.get(CSV_URL, headers={"Cache-Control": "no-cache"})
    response.encoding = "utf-8"
    csv_data = response.text

    df = pd.read_csv(io.StringIO(csv_data))

    # 欠損対応とラベル作成
    df["曜日"] = df["曜日"].fillna("")
    df["天気"] = df["天気"].fillna("")
    df["曜日天気"] = df["曜日"] + " / " + df["天気"]

    # グラフ生成
    plt.figure(figsize=(12, 6))
    for combo in df["曜日天気"].unique():
        subset = df[df["曜日天気"] == combo]
        if not subset.empty:
            plt.plot(subset["日時"], subset["自転車の数"], label=combo, marker="o")

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

if __name__ == "__main__":
    import os
    PORT = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=PORT)