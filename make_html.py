import github
import json
import os


def to_seconds(time, unit):
    if unit == "ns":
        return time / 10**9
    if unit == "μs":
        return time / 10**6
    if unit == "ms":
        return time / 10**3
    if unit == "s":
        return time

    raise ValueError(f"Unsupported unit: {unit}")


root_dir = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(root_dir, "data.json")) as f:
    data = json.load(f)

benches = list(data.keys())
benches.sort()

print("<div id='benchall'></div>")

print("<script type='text/javascript'>")
for i, b in enumerate(benches):
    print(f"var line{i} = {{")
    print("  x: [" + ", ".join([f"\"{j['date']}\"" for j in data[b]]) + "],")
    print("  y: [" + ", ".join([
        f"{to_seconds(j['mean']['estimate'], j['mean']['unit'])}"
        for j in data[b]]) + "],")
    print("  type: 'scatter',")
    print("  mode: 'lines+markers',")
    print(f"  name: \"{b}\"")
    print("};")

print("var layout = {")
print("  showlegend: true,")
print("  height: 650,")
print("  legend: {x: 1, yanchor: 'top', xanchor: 'right', y: -0.2},")
print("  xaxis: {title: 'Date'},")
print("  yaxis: {title: 'Time (s)'}")
print("};")

print("Plotly.newPlot('benchall', "
      "[" + ", ".join([f"line{i}" for i, _ in enumerate(benches)]) + "], "
      "layout);")
print("</script>")
