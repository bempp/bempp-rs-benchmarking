import github
import json
import os
import sys

key = sys.argv[-1]
git = github.Github(key)

root_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    os.path.join(os.path.pardir, os.path.pardir))
with open(os.path.join(root_dir, "data.json")) as f:
    data = json.load(f)

benches = list(data.keys())
benches.sort()

html = ""
# html += "<h2>All benchmarks</h2>\n"
html += "<div id='benchall'></div>\n"
# for i, b in enumerate(benches):
#    html += f"<h2>{b}</h2>\n"
#    html += f"<div id='bench{i}'></div>\n"

html += "<script type='text/javascript'>\n"
for i, b in enumerate(benches):
    html += f"var line{i} = {{\n"
    html += "  x: [" + ", ".join([f"\"{j['date']}\"" for j in data[b]]) + "],\n"
    html += "  y: [" + ", ".join([f"{j['mean']['estimate']}" for j in data[b]]) + "],\n"
    html += "  type: 'scatter',\n"
    html += "  mode: 'lines+markers',\n"
    html += f"  name: \"{b}\"\n"
    html += "};\n"
html += "Plotly.newPlot('benchall', [" + ", ".join([f"line{i}" for i, _ in enumerate(benches)]) + "]);\n"
# for i, _ in enumerate(benches):
#    html += f"Plotly.newPlot('bench{i}', [line{i}]);\n"
html += "</script>\n"


r = git.get_repo("bempp/bempp-website")
current = r.get_contents("_includes/_rs_benches.html")


r.update_file("_includes/_rs_benches.html", "Update benchmark plots", html, sha=current.sha)
