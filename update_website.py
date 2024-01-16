import sys
import json
import github

assert len(sys.argv) == 2
html_file = sys.argv[-1]
with open(html_file) as f:
    html = f.read()

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

r = g.get_repo("bempp/bempp-website")
current = r.get_contents("_includes/_rs_benches.html")

r.update_file("_includes/_rs_benches.html", "Update benchmark plots", html, sha=current.sha)
