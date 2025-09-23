from flask import Flask, render_template
import pandas as pd
import matplotlib.pyplot as plt
import os

app = Flask(__name__)

# CSV は GitHub URL から取得
CSV_URL = "https://raw.githubusercontent.com/Ryosuke2418/saddle/main/uploads/saddle_data.csv"

@app.route("/")
def index():
    # CSV 読み込み
    df = pd.read_csv(CSV_URL, encoding="cp932")
    
    # 日付をdatetime型に変換
    df["日時"] = pd.to_datetime(df["日時"])
    
    # 「曜日+天気」を組み合わせた列を作る
    df["曜日天気"] = df["曜日"] + " / " + df["天気"]

    # ==============================
    # グラフ作成
    # ==============================
    plt.figure(figsize=(10, 5))
    for combo in df["曜日天気"].unique():
        subset = df[df["曜日天気"] == combo]
        plt.plot(subset["日時"], subset["自転車の数"], label=combo)
    plt.xlabel("日時")
    plt.ylabel("自転車の数")
    plt.title("曜日＋天気ごとの自転車混雑状況")
    plt.legend()
    plt.tight_layout()
    
    # staticフォルダに保存
    graph_path = os.path.join("static", "graph.png")
    plt.savefig(graph_path, dpi=150)
    plt.close()

    # CSV 表を HTML に変換
    table_html = df.to_html(classes="data", index=False)

    return render_template("index.html", table=table_html, graph_file="graph.png")

if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=PORT)