import os
import datetime
import pandas as pd
import csv

# CSVはアプリフォルダ内のuploadsに置く
CSV_PATH = "uploads/saddle_data.csv"

# デフォルトの天気・気温（ここをAPIで自動取得も可能）
weather = "晴れ"
temperature = 28.5

# 日時
now = datetime.datetime.now()
now_str = now.strftime("%Y-%m-%d %H:%M")

# 曜日
weekday_map = {0: "月", 1: "火", 2: "水", 3: "木", 4: "金", 5: "土", 6: "日"}
weekday = weekday_map[now.weekday()]

# サドル検出数（ここはYOLOのコードや他の処理に置き換え可能）
count = 5  # 仮に5台としてサンプル

# CSVが存在するか確認
file_exists = os.path.isfile(CSV_PATH)

# CSVに追記
with open(CSV_PATH, "a", newline="", encoding="cp932") as csvfile:
    writer = csv.writer(csvfile)
    if not file_exists:
        writer.writerow(["日時", "自転車の数", "天気", "気温", "曜日"])
    writer.writerow([now_str, count, weather, temperature, weekday])

print("CSVに記録しました！")

# ここから簡単にグラフを作ることも可能（Render上で保存するだけ）
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

df = pd.read_csv(CSV_PATH, encoding="cp932")
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

graph_file = "static/graph.png"
plt.savefig(graph_file, dpi=300)
plt.close()

print("グラフを更新しました！（static/graph.png）")