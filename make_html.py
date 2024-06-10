import json
import os
import sys

test = "test" in sys.argv

# List of benchmarks to exclude from website
exclude = [
    "Helmholtz Potentials f32/M2L=FFT, N=1000000, wavenumber=0.0000001",
    "Helmholtz Potentials f32/M2L=BLAS, N=1000000, wavenumber=0.0000001",
    "Helmholtz Gradients f32/M2L=FFT, N=1000000, wavenumber=0.0000001",
    "Helmholtz Gradients f32/M2L=BLAS, N=1000000, wavenumber=0.0000001"
]
# Include error bars?
error_bars = False

try:
    import github
    has_github = True
    with open("key.pem") as f:
        key = f.read()

    with open("info.private") as f:
        content = f.read()
        app_id = int(content.split("\n")[0].split()[-1])
        id = int(content.split("\n")[1].split()[-1])

    gi = github.GithubIntegration(auth=github.Auth.AppAuth(app_id, key))
    for i in gi.get_installations():
        if i.id == id:
            g = i.get_github_for_installation()
            break
    else:
        raise RuntimeError()

    # Get Bempp-rs releases
    shapes = []
    annotations = []
    r = g.get_repo("bempp/bempp-rs")
    for release in r.get_releases():
        date = release.created_at.strftime("%Y-%m-%d")
        shapes.append(f"{{type: 'line', xref: 'x', yref: 'paper', x0: '{date}', x1: '{date}', "
                      "y0: 0, y1: 1, line: {color: '#000000', width: 1, dash: 'dash'}}")
        annotations.append(f"{{showarrow: false, text: 'Bempp {release.title}', xref: 'x', "
                           f"yref: 'paper', x: '{date}', y: 1, xanchor: 'left', yanchor: 'top', "
                           "textangle: 90}")
    bempp_releases = "  shapes: [" + ", ".join(shapes) + "],\n"
    bempp_releases += "  annotations: [" + ", ".join(annotations) + "]"

    # Get Kifmm releases
    shapes = []
    annotations = []
    r = g.get_repo("bempp/kifmm")
    for release in r.get_releases():
        date = release.created_at.strftime("%Y-%m-%d")
        shapes.append(f"{{type: 'line', xref: 'x', yref: 'paper', x0: '{date}', x1: '{date}', "
                      "y0: 0, y1: 1, line: {color: '#000000', width: 1, dash: 'dash'}}")
        annotations.append(f"{{showarrow: false, text: 'Kifmm {release.title}', xref: 'x', "
                           f"yref: 'paper', x: '{date}', y: 1, xanchor: 'left', yanchor: 'top', "
                           "textangle: 90}")
    kifmm_releases = "  shapes: [" + ", ".join(shapes) + "],\n"
    kifmm_releases += "  annotations: [" + ", ".join(annotations) + "]"

except (ModuleNotFoundError, FileNotFoundError):
    has_github = False

plots = [
    ["Assembly", "assembly/", "Bempp" if has_github else None],
    ["Laplace FMM", "Laplace ", "Kifmm" if has_github else None],
    ["Helmholtz FMM", "Helmholtz", "Kifmm" if has_github else None],
    ["Other", None, None],
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


if test:
    print("<html>")
    print("<head>")
    print('<script src="https://cdn.plot.ly/plotly-2.27.0.min.js" charset="utf-8"></script>')
    print("</head>")
    print("<body>")

root_dir = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(root_dir, "data.json")) as f:
    data = json.load(f)

benches = [b for b in data.keys() if b not in exclude]
benches.sort()

for title, start, releases in plots:
    id = title.lower().replace(" ", "_")

    remove = []
    lines = []
    i = 0
    for b in benches:
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

            i += 1
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
        print("  margin: {t: 15}" + ("" if releases is None else ","))
        if releases == "Bempp":
            print(bempp_releases)
        elif releases == "Kifmm":
            print(kifmm_releases)
        else:
            assert releases is None

        print("};")

        print(f"Plotly.newPlot('bench_{id}', "
              "[" + ", ".join([f"line{j}_{id}" for j in range(i)]) + "], "
              "layout);")
        print("</script>")

if test:
    print("</body>")
    print("</html>")
