import concurrent.futures
import json
import sys
import urllib.parse
import urllib.request
from argparse import ArgumentParser
from functools import partial, reduce
from http.server import HTTPServer, SimpleHTTPRequestHandler, test

from tqdm import tqdm


def get(base, *path):
    url = reduce(urllib.parse.urljoin, path, base)
    with urllib.request.urlopen(url) as h:
        return json.loads(h.read().decode())


def fetch_workflows(args, pbar, host):
    host_name = host[0]
    host_url = host[1]
    result = {}
    tools = {}

    pbar.set_description("Fetching from {} ({})".format(host_name, host_url))
    workflows = get(host_url, "/api/workflows")

    pbar2 = tqdm(workflows[:args.max_workflows], leave=False)
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
                if args.tool_names:
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
    return result


class CORSRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "http://localhost:8081")
        SimpleHTTPRequestHandler.end_headers(self)


def main(args):
    if args.fetch or args.tool_names:
        with open("hosts.json") as f:
            hosts = json.load(f)

        with concurrent.futures.ThreadPoolExecutor(max_workers=args.max_workers) as e:
            pbar = tqdm(hosts.items())
            result = e.map(partial(fetch_workflows, args, pbar), pbar)
            result = list(result)

        print("Total number of workflows fetched: ", len(result))

        with open("workflows.json", "w") as f:
            json.dump(result, f, indent=4, sort_keys=True)

    test(CORSRequestHandler, HTTPServer, port=8082)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "--max-workers",
        metavar="n",
        help="max number of workers to fetch workflows (default: 1)",
        type=int,
        default=1,
    )
    parser.add_argument("-f", "--fetch", help="fetch workflows", action="store_true")
    parser.add_argument(
        "-t",
        "--tool-names",
        help="fetch tool names (2 requests/workflow). Implies -f",
        action="store_true",
    )
    parser.add_argument(
        "--max-workflows",
        metavar="N",
        help="max number of workflows to fetch from each hosts (default: 10)",
        type=int,
        default=100,
    )
    # parser.add_argument(
    #     "-q",
    #     "--quiet",
    #     action="store_false",
    #     dest="verbose",
    #     default=True,
    #     help="don't print status messages to stdout",
    # )

    args = parser.parse_args()
    main(args)
