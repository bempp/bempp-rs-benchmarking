from abc import ABC, abstractproperty
import typing
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
    bempp_shapes = []
    bempp_annotations = []
    r = g.get_repo("bempp/bempp-rs")
    for release in r.get_releases():
        date = release.created_at.strftime("%Y-%m-%d")
        bempp_shapes.append(
            f"{{type: 'line', xref: 'x', yref: 'paper', x0: '{date}', x1: '{date}', "
            "y0: 0, y1: 1, line: {color: '#000000', width: 1, dash: 'dash'}}")
        bempp_annotations.append(
            f"{{showarrow: false, text: 'Bempp {release.title}', xref: 'x', "
            f"yref: 'paper', x: '{date}', y: 1, xanchor: 'left', yanchor: 'top', textangle: 90}}")

    # Get Kifmm releases
    kifmm_shapes = []
    kifmm_annotations = []
    r = g.get_repo("bempp/kifmm")
    for release in r.get_releases():
        date = release.created_at.strftime("%Y-%m-%d")
        kifmm_shapes.append(
            f"{{type: 'line', xref: 'x', yref: 'paper', x0: '{date}', x1: '{date}', "
            "y0: 0, y1: 1, line: {color: '#000000', width: 1, dash: 'dash'}}")
        kifmm_annotations.append(
            f"{{showarrow: false, text: 'Kifmm {release.title}', xref: 'x', "
            f"yref: 'paper', x: '{date}', y: 1, xanchor: 'left', yanchor: 'top', textangle: 90}}")

except (ModuleNotFoundError, FileNotFoundError):
    has_github = False

root_dir = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(root_dir, "data.json")) as f:
    data = json.load(f)


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


class AbstractPlotLine(ABC):
    @abstractproperty
    def label(self) -> str:
        """The label on the plot."""

    @abstractproperty
    def color(self) -> typing.Optional[str]:
        """Custom colour to use for the line."""

    @abstractproperty
    def dates(self) -> typing.List[str]:
        """The dates of each data point."""

    @abstractproperty
    def times(self) -> typing.List[float]:
        """The execution time for each data point."""

    @abstractproperty
    def used(self) -> typing.List[str]:
        """Labels used by this line."""


class PlotLine(AbstractPlotLine):
    def __init__(self, label, color=None):
        self._label = label
        self._color = color

    @property
    def label(self) -> str:
        return self._label

    @property
    def color(self) -> typing.Optional[str]:
        return self._color

    @property
    def dates(self) -> typing.List[str]:
        return [j['date'] for j in data[self._label]]

    @property
    def times(self) -> typing.List[float]:
        return [to_seconds(j['mean']['estimate'], j['mean']['unit']) for j in data[self._label]]

    @property
    def used(self) -> typing.List[str]:
        return [self._label]


class RelabelledPlotLine(PlotLine):
    def __init__(self, label, new_name, color=None):
        super().__init__(label, color)
        self._new_name = new_name

    @property
    def label(self) -> str:
        return self._new_name


class SumLine(AbstractPlotLine):
    def __init__(self, lines, label, color=None):
        self._label = label
        self._lines = lines
        self._color = color

    @property
    def label(self) -> str:
        return self._label

    @property
    def color(self) -> typing.Optional[str]:
        return self._color

    @property
    def dates(self) -> typing.List[str]:
        dates = [j['date'] for j in data[self._lines[0]]]
        for i in self._lines:
            dates2 = [j['date'] for j in data[i]]
            dates = [j for j in dates if j in dates2]
        return dates

    @property
    def times(self) -> typing.List[float]:
        dates = self.dates
        all_data = [{
            j['date']: to_seconds(j['mean']['estimate'], j['mean']['unit']) for j in data[i]
        } for i in self._lines]
        return [sum(i[j] for i in all_data) for j in dates]

    @property
    def used(self) -> typing.List[str]:
        return self._lines


plots = [
    [
        "Assembly", [RelabelledPlotLine(
            "assembly/Assembly of non-singular terms of 512x512 matrix",
            "Assembly of non-singular terms of 512x512 matrix"
        ), RelabelledPlotLine(
            "assembly/Assembly of singular terms of 512x512 matrix",
            "Assembly of singular terms of 512x512 matrix"
        ), RelabelledPlotLine(
            "assembly/Assembly of non-singular terms of 2048x2048 matrix",
            "Assembly of non-singular terms of 2048x2048 matrix"
        ), RelabelledPlotLine(
            "assembly/Assembly of singular terms of 2048x2048 matrix",
            "Assembly of singular terms of 2048x2048 matrix"
        ), SumLine(
            [
                "assembly/Assembly of non-singular terms of 2048x2048 matrix",
                "assembly/Assembly of singular terms of 2048x2048 matrix"
            ], "Assembly of full 2048x2048 matrix", "#000000"
        )], "Bempp" if has_github else None, [("Bempp-cl 2048x2048", 0.128, "#000000")]
    ],
    # ["Laplace FMM", "Laplace ", "Kifmm" if has_github else None],
    # ["Helmholtz FMM", "Helmholtz", "Kifmm" if has_github else None],
    ["Other", None, None, None],
]

if test:
    print("<html>")
    print("<head>")
    print('<script src="https://cdn.plot.ly/plotly-2.27.0.min.js" charset="utf-8"></script>')
    print("</head>")
    print("<body>")

benches = [b for b in data.keys() if b not in exclude]
benches.sort()

for title, lines, releases, hlines in plots:
    id = title.lower().replace(" ", "_")

    if lines is None:
        lines = [PlotLine(b) for b in benches]

    remove = []
    lines_html = []
    line_ids = []
    for i, line in enumerate(lines):
        for u in line.used:
            if u in benches:
                benches.remove(u)
        line_ids.append(f"line{i}_{id}")
        lines_html.append(f"var {line_ids[-1]} = {{")
        lines_html.append("  x: [" + ", ".join([f"\"{j}\"" for j in line.dates]) + "],")
        lines_html.append("  y: [" + ", ".join([f"{j}" for j in line.times]) + "],")
        lines_html.append("  type: 'scatter',")
        if line.color is not None:
            lines_html.append(f"  marker: {{color: '{line.color}'}},")
            lines_html.append(f"  line: {{color: '{line.color}'}},")
        lines_html.append("  mode: 'lines+markers',")
        lines_html.append(f"  name: \"{line.label}\"")
        lines_html.append("};")

    if len(lines_html) > 0:
        print(f"<h3>{title}</h3>")
        print(f"<div id='bench_{id}'></div>")

        print("<script type='text/javascript'>")
        print("\n".join(lines_html))

        print("var layout = {")
        print("  showlegend: true,")
        print("  height: 650,")
        print("  legend: {x: 1, yanchor: 'top', xanchor: 'right', y: -0.2},")
        print("  xaxis: {title: 'Date'},")
        print("  yaxis: {title: 'Time (s)', rangemode: 'tozero'},")
        shapes = []
        annotations = []
        if releases == "Bempp":
            shapes += bempp_shapes
            annotations += bempp_annotations
        elif releases == "Kifmm":
            shapes += kifmm_shapes
            annotations += kifmm_annotations
        else:
            assert releases is None

        if hlines is not None:
            for label, value, color in hlines:
                shapes.append(
                    "{type: 'line', xref: 'paper', yref: 'y', x0: 0, x1: 1, "
                    f"y0: {value}, y1: {value}, line: {{color: '{color}', width: 1, "
                    "dash: 'dash'}}")
                annotations.append(
                    f"{{showarrow: false, text: '{label}', xref: 'paper', yref: 'y', "
                    f"x: '1', y: {value}, xanchor: 'right', yanchor: 'bottom', "
                    f"font: {{color: '{color}'}}}}")

        if len(shapes) == 0:
            print("  margin: {t: 15}")
        else:
            print("  margin: {t: 15},")
            print("  shapes: [" + ", ".join(shapes) + "],")
            print("  annotations: [" + ", ".join(annotations) + "]")

        print("};")

        print(f"Plotly.newPlot('bench_{id}', "
              "[" + ", ".join(line_ids) + "], "
              "layout);")
        print("</script>")

if test:
    print("</body>")
    print("</html>")
