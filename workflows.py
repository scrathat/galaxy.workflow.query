import json
import urllib.parse
import urllib.request
from functools import reduce

from tqdm import tqdm


def get(base, *path):
    url = reduce(urllib.parse.urljoin, path, base)
    with urllib.request.urlopen(url) as h:
        return json.loads(h.read().decode())


def main():
    result = {}
    tools = {}

    with open("hosts.json") as f:
        hosts = json.load(f)

    pbar1 = tqdm(hosts.items())
    for host_name, host_url in pbar1:
        pbar1.set_description("Fetching from {} ({})".format(host_name, host_url))

        workflows = get(host_url, "/api/workflows")

        pbar2 = tqdm(workflows, leave=False)
        for w in pbar2:
            pbar2.set_description('Workflow "{}" ({})'.format(w["name"], w["id"]))

            workflow_tools = []
            workflow_info = get(host_url, "/api/workflows/", w["id"])

            for _, step in workflow_info["steps"].items():
                if step["type"] != "tool":
                    continue

                tool_id = step["tool_id"]
                if tool_id not in tools:
                    tool_name = ""
                    try:
                        tool_json = get(
                            host_url, "/api/tools/", urllib.parse.quote(tool_id)
                        )
                        tool_name = tool_json["name"]
                    except urllib.error.HTTPError:
                        print("Error getting tool info for {}".format(tool_id))
                        print("Skipping workflow {}".format(w["id"]))
                        break

                    tools[tool_id] = {"id": tool_id, "name": tool_name}
                    workflow_tools.append(tools[tool_id])
            else:
                result_key = host_url + "|" + w["id"]
                result[result_key] = {
                    "host_name": host_name,
                    "host_url": host_url,
                    "id": w["id"],
                    "name": w["name"],
                    "owner": w["owner"],
                    "tools": workflow_tools,
                }

    print("Total number of workflows fetched: ", len(result))

    with open("workflows.json", "w") as f:
        json.dump(result, f, indent=4, sort_keys=True)

    with open("_tools.json", "w") as f:
        json.dump(tools, f, indent=4, sort_keys=True)


if __name__ == "__main__":
    main()
