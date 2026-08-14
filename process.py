import json
from pathlib import Path
from datetime import datetime, timezone
import csv

OUTPUT_DIR = Path("output")
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

json_path = OUTPUT_DIR / "latest.json"
if not json_path.exists():
    print("latest.json not found")
    exit(1)

with open(json_path, encoding="utf-8") as f:
    data = json.load(f)

# CBBI 的 Confidence 字段
confidence_series = data.get("Confidence", {})
if not confidence_series:
    print("No Confidence data found")
    exit(1)

# 取最新一条
latest_ts = max(int(k) for k in confidence_series.keys())
latest_value = confidence_series[str(latest_ts)]
latest_date = datetime.fromtimestamp(latest_ts, tz=timezone.utc).strftime("%Y-%m-%d")

csv_path = DATA_DIR / "cbbi.csv"
write_header = not csv_path.exists()

# 避免重复写入同一天
rows = []
if csv_path.exists():
    with open(csv_path, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    if rows and rows[-1][0] == latest_date:
        print(f"Already updated for {latest_date}")
        exit(0)

with open(csv_path, "a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    if write_header:
        writer.writerow(["date", "confidence"])
    writer.writerow([latest_date, round(float(latest_value) * 100, 2)])  # 转成 0-100

print(f"Updated: {latest_date} → {round(float(latest_value)*100, 2)}")

# 同时保存最新值方便快速读取
with open(DATA_DIR / "latest.txt", "w") as f:
    f.write(f"{latest_date},{round(float(latest_value)*100, 2)}\n")
