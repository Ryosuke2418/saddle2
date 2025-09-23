from flask import Flask, send_file, render_template_string
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import os

# ==============================
# matplotlib 日本語対応
# ==============================
matplotlib.use("Agg")
matplotlib.rcParams['font.family'] = 'Meiryo'

CSV_FILE = "saddle_data.csv"
GRAPH_FILE = "graph.png"

app = Flask(__name__)

# ==============================
# CSVからグラフ作成
# ==============================
def generate_graph():
    if not os.path.isfile(CSV_FILE):
        return False
    df = pd.read_csv(CSV_FILE, encoding="cp932")
    df["日時"] = pd.to_datetime(df["日時"], errors="coerce")
    df["曜日天気"] = df["曜日"] + " / " + df["天気"]

    plt.figure(figsize=(12, 6))
    for combo in df["曜日天気"].unique():
        subset = df[df["曜日天気"] == combo]
        plt.plot(subset["日時"], subset["自転車の数"], label=combo, marker="o")

    plt.xlabel("日時")
    plt.ylabel("自転車の数")
    plt.title("曜日＋天気ごとの自転車混雑状況")
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(GRAPH_FILE, dpi=300)
    plt.close()
    return True

# ==============================
# ルート
# ==============================
HTML_TEMPLATE = """
<!doctype html>
<title>CSVの自転車混雑状況</title>
<h1>CSVの現状グラフ</h1>
{% if graph_exists %}
<img src="/graph.png" alt="graph">
{% else %}
<p>まだCSVが存在しません</p>
{% endif %}
"""

@app.route("/")
def index():
    graph_exists = generate_graph()
    return render_template_string(HTML_TEMPLATE, graph_exists=graph_exists)

@app.route("/graph.png")
def graph_png():
    return send_file(GRAPH_FILE, mimetype="image/png")

# ==============================
# サーバー起動
# ==============================
if __name__ == "__main__":
    app.run(debug=True)