""" This module can get workflows from a galaxy instance. """
import json
import urllib.error
import urllib.parse
import urllib.request
import urllib.response
from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor
from functools import partial, reduce
from http.server import HTTPServer, SimpleHTTPRequestHandler, test
from typing import Dict, Tuple

from tqdm import tqdm


def get(base: str, *path: str):
    """Join base url with paths and get resulting JSON response.

    Args:
        base (str): the base url
        *path (str): the paths to join with base url

    Returns:
        JSON response decoded according to :class:`~json.JSONDecoder`
    """
    url = reduce(urllib.parse.urljoin, path, base)
    with urllib.request.urlopen(url) as response:
        return json.loads(response.read().decode())


def fetch_workflows(max_workflows: int, get_tool_names: bool, pbar,
                    host: Tuple[str, str]) -> Dict[str, Dict]:
    """Fetch workflows

    Args:
        max_workflows (int): max number of wrokflows to fetch
        get_tool_names (bool): if true also fetch tool names
        pbar: set desrciption for this tqdm object
        host (Tuple[str, str]): fetch workflows from this host

    Returns:
        (Dict[str, Dict]): Workflows of host
    """
    host_name = host[0]
    host_url = host[1]
    result = {}
    tools: Dict[str, Dict] = {}

    pbar.set_description(f"Fetching from {host_name} ({host_url})")
    workflows = get(host_url, "/api/workflows")

    pbar2 = tqdm(workflows[:max_workflows], leave=False)
    for workflow in pbar2:
        pbar2.set_description(
            f'Workflow "{workflow["name"]}" ({workflow["id"]})')

        workflow_tools = []
        workflow_info = get(host_url, "/api/workflows/", workflow["id"])

        for _, step in workflow_info["steps"].items():
            if step["type"] != "tool":
                continue

            tool_id = step["tool_id"]
            if tool_id not in tools:
                tool_name = ""
                if get_tool_names:
                    try:
                        tool_json = get(host_url, "/api/tools/",
                                        urllib.parse.quote(tool_id))
                        tool_name = tool_json["name"]
                    except urllib.error.HTTPError:
                        print(f"Error getting tool info for {tool_id}")
                        print(f"Skipping workflow {workflow['id']}")
                        break
                tools[tool_id] = {"id": tool_id, "name": tool_name}

            workflow_tools.append(tools[tool_id])
        else:
            result_key = host_url + "|" + workflow["id"]
            result[result_key] = {
                "host_name": host_name,
                "host_url": host_url,
                "id": workflow["id"],
                "name": workflow["name"],
                "owner": workflow["owner"],
                "tools": workflow_tools,
            }
    return result


class CORSRequestHandler(SimpleHTTPRequestHandler):
    """Simple CORS request handler"""
    def end_headers(self):
        """Set Access-Control-Allow-Origin before sending"""
        self.send_header("Access-Control-Allow-Origin",
                         "http://localhost:8081")
        SimpleHTTPRequestHandler.end_headers(self)


def main(args):
    """Fetch workflows if requested and serve on localhost

    Args:
        args: arguments passed to this script
    """
    if args.fetch or args.tool_names:
        with open("hosts.json") as file:
            hosts = json.load(file)

        with ThreadPoolExecutor(max_workers=args.max_workers) as tpe:
            pbar = tqdm(hosts.items())
            result = tpe.map(
                partial(fetch_workflows, args.max_workflows, args.tool_names,
                        pbar),
                pbar,
            )
            result = list(result)

        print("Total number of workflows fetched: ", len(result))

        with open("workflows.json", "w") as file:
            json.dump(result, file, indent=4, sort_keys=True)

    test(CORSRequestHandler, HTTPServer, port=8082)


if __name__ == "__main__":
    PARSER = ArgumentParser()
    PARSER.add_argument(
        "--max-workers",
        metavar="n",
        help="max number of workers to fetch workflows (default: 1)",
        type=int,
        default=1,
    )
    PARSER.add_argument("-f",
                        "--fetch",
                        help="fetch workflows",
                        action="store_true")
    PARSER.add_argument(
        "-t",
        "--tool-names",
        help="fetch tool names (2 requests/workflow). Implies -f",
        action="store_true",
    )
    PARSER.add_argument(
        "--max-workflows",
        metavar="N",
        help="max number of workflows to fetch from each hosts (default: 100)",
        type=int,
        default=100,
    )
    # PARSER.add_argument(
    #     "-q",
    #     "--quiet",
    #     action="store_false",
    #     dest="verbose",
    #     default=True,
    #     help="don't print status messages to stdout",
    # )

    main(PARSER.parse_args())
