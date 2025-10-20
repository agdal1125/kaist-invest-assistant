import os
import json

NH_HOME = os.getenv("NH_HOME")

SOURCE_PATH = f"{NH_HOME}/stock_database/stock_korean_name.json"
TARGET_PATH = f"{NH_HOME}/stock_database/stock_database.json"

with open(SOURCE_PATH, "r") as f:
    data = json.load(f)
    
processed_data = {}

for item in data:
    names = item["nicknames"]
    names.append(item["name"])
    names.append(item["symbol"])
    names = list(set(names))
    
    processed_data[item["symbol"]] = names

with open(TARGET_PATH, "w") as f:
    json.dump(processed_data, f, indent=4, ensure_ascii=False)