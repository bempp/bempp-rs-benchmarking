import json
import github

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

r = g.get_repo("bempp/bempp-rs-benchmarking")

file = r.get_contents("data.json")
data = json.loads(file.decoded_content.decode("utf8"))

with open("new.json") as f:
    new_data = json.load(f)

assert len(new_data) > 0

for i, j in new_data.items():
    if i not in data:
        data[i] = []
    data[i].append(j)

r.update_file("data.json", "Upload benchmark results", json.dumps(data), sha=file.sha)

with open("new.json", "w") as f:
    json.dump({}, f)

print(data)
