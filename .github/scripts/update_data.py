import json

with open("data.json") as f:
    data = json.load(f)

with open("new.json") as f:
    new_data = json.load(f)

assert len(new_data) > 0

for i, j in new_data.items():
    if i not in data:
        data[i] = []
    data[i].append(j)

with open("data.json", "w") as f:
    json.dump(data, f)

with open("new.json", "w") as f:
    json.dump({}, f)
