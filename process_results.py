import json
from datetime import datetime

date = datetime.now().strftime("%Y-%m-%d %H:%M")

data = {}
with open("bempp-rs/output.json") as f:
    for line in f:
        raw_data = json.loads(line)
        if raw_data["reason"] == "benchmark-complete":
            data[raw_data["id"]] = {"date": date, "mean": raw_data["mean"]}

with open("new.json", "w") as f:
    json.dump(data, f)
