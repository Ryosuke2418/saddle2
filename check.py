import pandas as pd

csv_path = "C:\Users\辻亮輔\Desktop\website\uploads\saddle_data.csv"
df = pd.read_csv(csv_path, encoding="cp932")  # Windowsならcp932
print("行数:", len(df))