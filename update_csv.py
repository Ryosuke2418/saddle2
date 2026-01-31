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


# ========= YOLO 推論 =========
image_path = "C:/Users/辻亮輔/Desktop/ultralytics/photo/sample8.jpg"
model_path = "C:/Users/辻亮輔/Desktop/ultralytics/runs/detect/train19/weights/best.pt"

model = YOLO(model_path)
results = model.predict(source=image_path, conf=0.3)

count = len(results[0].boxes)

weather = input("今の天気は？（例：晴れ, 曇り, 雨）：")
temperature = input("今の気温は？（例：28.5）：")

now = datetime.datetime.now()
now_str = now.strftime("%Y-%m-%d %H:%M")

weekday_map = {0: "月", 1: "火", 2: "水", 3: "木", 4: "金", 5: "土", 6: "日"}
weekday = weekday_map[now.weekday()]

csv_file = "saddle_data.csv"
file_exists = os.path.isfile(csv_file)

with open(csv_file, "a", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    if not file_exists:
        writer.writerow(["日時", "自転車の数", "天気", "気温", "曜日"])
    writer.writerow([now_str, count, weather, temperature, weekday])

print("CSVに記録しました！")

# ========= 平均化してグラフ作成 =========

df = pd.read_csv(csv_file, encoding="utf-8")
df["日時"] = pd.to_datetime(df["日時"], errors="coerce")
df["自転車の数"] = pd.to_numeric(df["自転車の数"], errors="coerce").fillna(0)

# ---- 日付だけを抽出（平均化に必要） ----
df["日付"] = df["日時"].dt.date

# ---- 時間帯を10時/15時/20時に丸める ----
# ---- 時間帯を10時/15時/20時に丸める ----
def round_to_time(dt):
    if pd.isna(dt):
        return None
    target_hours = [10, 15, 20]
    hour = dt.hour
    closest = min(target_hours, key=lambda x: abs(x - hour))
    return f"{closest:02d}:00"

df["時間帯"] = df["日時"].apply(round_to_time)

# ---- 平均化（日付ごと絶対必要） ----
df_mean = (
    df.groupby(["日付", "曜日", "天気", "時間帯"], as_index=False)
    .agg({"自転車の数": "mean"})
)

# ---- プロット用ラベル ----
df_mean["表示ラベル"] = (
    df_mean["日付"].astype(str) + " / " +
    df_mean["曜日"] + " / " +
    df_mean["天気"]
)

# ---- グラフ描画 ----
plt.figure(figsize=(12, 6))

for combo in df_mean["表示ラベル"].unique():
    subset = df_mean[df_mean["表示ラベル"] == combo]
    plt.plot(subset["時間帯"], subset["自転車の数"], label=combo, marker="o")

plt.xlabel("時間帯（10時 / 15時 / 20時）")
plt.ylabel("平均自転車数")
plt.title("日付 × 曜日 × 天気 × 時間帯 の平均自転車数")
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()

graph_file = "graph.png"
plt.savefig(graph_file, dpi=300)
plt.close()

path = os.path.abspath(graph_file).replace("\\", "/")
webbrowser.open_new_tab("file://" + path)

print("グラフを更新しました。")