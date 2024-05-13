import json
import os

# List of benchmarks to exclude from website
exclude = [
    "Helmholtz Potentials f32/M2L=FFT, N=1000000, wavenumber=0.0000001",
    "Helmholtz Potentials f32/M2L=BLAS, N=1000000, wavenumber=0.0000001",
    "Helmholtz Gradients f32/M2L=FFT, N=1000000, wavenumber=0.0000001",
    "Helmholtz Gradients f32/M2L=BLAS, N=1000000, wavenumber=0.0000001"
]
# Include error bars?
error_bars = False

plots = [
    ["Assembly", "assembly/"],
    ["Laplace FMM", "Laplace "],
    ["Helmholtz FMM", "Helmholtz"],
    ["Other", None],
]


def to_seconds(time, unit):
    if unit == "ps":
        return time / 10**12
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

benches = [b for b in data.keys() if b not in exclude]
benches.sort()

for title, start in plots:
    id = title.lower().replace(" ", "_")

    remove = []
    lines = []
    for i, b in enumerate(benches):
        if start is None or b.startswith(start):
            lines.append(f"var line{i}_{id} = {{")
            lines.append("  x: [" + ", ".join([f"\"{j['date']}\"" for j in data[b]]) + "],")
            lines.append("  y: [" + ", ".join([
                f"{to_seconds(j['mean']['estimate'], j['mean']['unit'])}"
                for j in data[b]]) + "],")
            if error_bars:
                lines.append("  error_y: {")
                lines.append("    type: 'data',")
                lines.append("    symmetric: false,")
                lines.append("    array: [" + ", ".join([str(
                    to_seconds(j['mean']['upper_bound'] - j['mean']['estimate'], j['mean']['unit'])
                ) for j in data[b]]) + "],")
                lines.append("    arrayminus: [" + ", ".join([str(
                    to_seconds(j['mean']['estimate'] - j['mean']['lower_bound'], j['mean']['unit'])
                ) for j in data[b]]) + "]")
                lines.append("  },")
            lines.append("  type: 'scatter',")
            lines.append("  mode: 'lines+markers',")
            lines.append(f"  name: \"{b}\"")
            lines.append("};")
            remove.append(b)
    for b in remove:
        benches.remove(b)
    if len(lines) > 0:
        print(f"<h3>{title}</h3>")
        print(f"<div id='bench_{id}'></div>")

        print("<script type='text/javascript'>")
        print("\n".join(lines))

        print("var layout = {")
        print("  showlegend: true,")
        print("  height: 650,")
        print("  legend: {x: 1, yanchor: 'top', xanchor: 'right', y: -0.2},")
        print("  xaxis: {title: 'Date'},")
        print("  yaxis: {title: 'Time (s)', rangemode: 'tozero'},")
        print("  margin: {t: 15}")
        print("};")

        print(f"Plotly.newPlot('bench_{id}', "
              "[" + ", ".join([f"line{i}_{id}" for i, _ in enumerate(benches)]) + "], "
              "layout);")
        print("</script>")
