import github
import json
import os

root_dir = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(root_dir, "data.json")) as f:
    data = json.load(f)

benches = list(data.keys())
benches.sort()

# print("<h2>All benchmarks</h2>")
print("<div id='benchall'></div>")
# for i, b in enumerate(benches):
#    print(f"<h2>{b}</h2>")
#    print(f"<div id='bench{i}'></div>")

print("<script type='text/javascript'>")
for i, b in enumerate(benches):
    print(f"var line{i} = {{")
    print("  x: [" + ", ".join([f"\"{j['date']}\"" for j in data[b]]) + "],")
    print("  y: [" + ", ".join([f"{j['mean']['estimate']}" for j in data[b]]) + "],")
    print("  type: 'scatter',")
    print("  mode: 'lines+markers',")
    print(f"  name: \"{b}\"")
    print("};")
print("Plotly.newPlot('benchall', [" + ", ".join([f"line{i}" for i, _ in enumerate(benches)]) + "]);")
# for i, _ in enumerate(benches):
#    print(f"Plotly.newPlot('bench{i}', [line{i}]);")
print("</script>")
