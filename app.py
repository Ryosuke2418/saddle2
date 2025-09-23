# app.py
from flask import Flask, render_template, redirect, url_for, request, flash
from werkzeug.utils import secure_filename
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "uploads"
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2MB limit
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret')  # 本番は環境変数で

CSV_FILE = os.path.join(app.config['UPLOAD_FOLDER'], "saddle_data.csv")
GRAPH_FILE = os.path.join("static", "graph.png")

# サーバ環境では Meiryo が無いことが多いのでデフォルトフォントにするか
# 日本語必要なら後段でフォント導入方法を載せる
matplotlib.rcParams['font.family'] = 'DejaVu Sans'

ALLOWED_EXT = {'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXT

def generate_graph():
    if not os.path.isfile(CSV_FILE):
        return False
    df = pd.read_csv(CSV_FILE, encoding="cp932")
    df["日時"] = pd.to_datetime(df["日時"], errors="coerce")
    df["曜日天気"] = df["曜日"] + " / " + df["天気"]

    plt.figure(figsize=(12,6))
    for combo in df["曜日天気"].unique():
        subset = df[df["曜日天気"] == combo]
        plt.plot(subset["日時"], subset["自転車の数"], label=combo, marker="o")

    plt.xlabel("日時")
    plt.ylabel("自転車の数")
    plt.title("曜日＋天気ごとの自転車混雑状況")
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    os.makedirs(os.path.dirname(GRAPH_FILE), exist_ok=True)
    plt.savefig(GRAPH_FILE, dpi=300)
    plt.close()
    return True

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/graph")
def show_graph():
    graph_exists = generate_graph()
    return render_template("graph.html", graph_exists=graph_exists)

@app.route("/upload", methods=["GET","POST"])
def upload():
    if request.method == "POST":
        if "file" not in request.files:
            flash("ファイルがありません")
            return redirect(request.url)
        file = request.files["file"]
        if file.filename == "":
            flash("ファイルが選択されていません")
            return redirect(request.url)
        if file and allowed_file(file.filename):
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            filename = secure_filename("saddle_data.csv")  # 常に同名で上書き
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            generate_graph()
            flash("CSVアップロード完了・グラフ更新しました")
            return redirect(url_for("show_graph"))
    return render_template("upload.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",5000)), debug=False)