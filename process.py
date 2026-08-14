import json
from pathlib import Path
from datetime import datetime, timezone
import csv

OUTPUT_DIR = Path("output")
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

json_path = OUTPUT_DIR / "latest.json"

if not json_path.exists():
    print("❌ latest.json not found")
    exit(1)

with open(json_path, encoding="utf-8") as f:
    data = json.load(f)

confidence_series = data.get("Confidence", {})
if not confidence_series:
    print("❌ No Confidence data found in latest.json")
    exit(1)

# 按时间戳排序，生成完整历史
sorted_items = sorted(
    ((int(ts), float(val)) for ts, val in confidence_series.items() if val is not None),
    key=lambda x: x[0]
)

csv_path = DATA_DIR / "cbbi.csv"

with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["date", "timestamp", "confidence"])  # 表头

    for ts, val in sorted_items:
        date_str = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d")
        # Confidence 原本是 0~1，转成 0~100
        confidence_100 = round(val * 100, 2)
        writer.writerow([date_str, ts, confidence_100])

# 同时更新 latest.txt（方便快速查看最新值）
if sorted_items:
    latest_ts, latest_val = sorted_items[-1]
    latest_date = datetime.fromtimestamp(latest_ts, tz=timezone.utc).strftime("%Y-%m-%d")
    latest_conf = round(latest_val * 100, 2)

    with open(DATA_DIR / "latest.txt", "w", encoding="utf-8") as f:
        f.write(f"{latest_date},{latest_conf}\n")

    print(f"✅ 完整历史已写入 cbbi.csv（共 {len(sorted_items)} 条）")
    print(f"✅ 最新值: {latest_date} → {latest_conf}")
else:
    print("❌ 没有有效数据")
