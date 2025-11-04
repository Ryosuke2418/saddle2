from ultralytics import YOLO
import datetime
import csv
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import os, webbrowser
import sys


try:
    import PyQt6
    pyqt_path = os.path.join(os.path.dirname(PyQt6.__file__), "Qt6", "plugins", "platforms")
except ImportError:
    try:
        import PyQt5
        pyqt_path = os.path.join(os.path.dirname(PyQt5.__file__), "Qt", "plugins", "platforms")
    except ImportError:
        pyqt_path = None

if pyqt_path:
    os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = pyqt_path


matplotlib.use("Agg")


matplotlib.rcParams['font.family'] = 'Meiryo'


image_path = "C:/Users/辻亮輔/Desktop/ultralytics/photo/sample5.jpg"
model_path = "C:/Users/辻亮輔/Desktop/ultralytics/runs/detect/train19/weights/best.pt"

model = YOLO(model_path)
results = model.predict(source=image_path, conf=0.3)

# 検出されたサドル数
count = len(results[0].boxes)


weather = input("今の天気は？（例：晴れ, 曇り, 雨）：")
temperature = input("今の気温は？（例：28.5）：")

now = datetime.datetime.now()
now_str = now.strftime("%Y-%m-%d %H:%M")

weekday_map = {0: "月", 1: "火", 2: "水", 3: "木", 4: "金", 5: "土", 6: "日"}
weekday = weekday_map[now.weekday()]


csv_file = "saddle_data.csv"
file_exists = os.path.isfile(csv_file)

with open(csv_file, "a", newline="", encoding="cp932") as csvfile:
    writer = csv.writer(csvfile)
    if not file_exists:
        writer.writerow(["日時", "自転車の数", "天気", "気温", "曜日"])
    writer.writerow([now_str, count, weather, temperature, weekday])

print("CSVに記録しました！")


df = pd.read_csv(csv_file, encoding="cp932")


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


graph_file = "graph.png"
plt.savefig(graph_file, dpi=300)
plt.close()


path = os.path.abspath(graph_file).replace("\\", "/")
webbrowser.open_new_tab("file://" + path)

print("グラフを更新しました！（graph.png ＋ ブラウザ表示）")