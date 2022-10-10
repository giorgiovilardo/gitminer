import csv
import datetime
import json
from typing import Optional

import dotenv
import requests


conf = dotenv.dotenv_values(".env")

org_name = conf.get("ORG")
interesting_topic = conf.get("TOPIC")
gh_token = conf.get("TOKEN")

all_repo_file = "all_repos.json"
interesting_repos_file = "interesting_repos.json"


def gh_get(url, all_pages=True, **kwargs):
    token = gh_token
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }
    if not all_pages:
        return requests.get(url, headers=headers, params=kwargs).json()
    result = []
    counter = 1
    while True:
        res = requests.get(
            url, headers=headers, params=kwargs | {"per_page": 100, "page": counter}
        ).json()
        if not res:
            break
        counter += 1
        result += res
    return result


def gh_datetime(gh_date: Optional[str]) -> datetime:
    try:
        return datetime.datetime.strptime(gh_date, "%Y-%m-%dT%H:%M:%SZ")
    except TypeError:
        return datetime.datetime.fromtimestamp(1)


def json_indented_dump(obj, fp):
    return json.dump(obj, fp, ensure_ascii=False, indent=2, default=str)


all_repos = gh_get(f"https://api.github.com/orgs/{org_name}/repos")

all_interesting_repos: list[dict] = [
    repo for repo in all_repos if interesting_topic in repo.get("topics", [])
]

with open(all_repo_file, "w") as file:
    json_indented_dump(all_repos, file)

with open(interesting_repos_file, "w") as file:
    json_indented_dump(all_interesting_repos, file)

# IF YOU ALREADY HAVE THE FILES
# with open(interesting_repos_file, "r") as file:
#     all_interesting_repos = json.load(file)

for repo in all_interesting_repos:
    repo_name: str = repo.get("name", "NONAME")
    print(f"parsing {repo_name}")
    branches: list[dict] = gh_get(
        f"https://api.github.com/repos/{org_name}/{repo_name}/branches"
    )
    pulls: list[dict] = gh_get(
        f"https://api.github.com/repos/{org_name}/{repo_name}/pulls",
        sort="updated",
        direction="desc",
    )
    releases: list[dict] = gh_get(
        f"https://api.github.com/repos/{org_name}/{repo_name}/releases"
    )
    sorted_releases = sorted(
        releases,
        key=lambda x: gh_datetime(x.get("published_at")),
        reverse=True,
    )
    repo["branches_count"] = len(branches)
    repo["pr_count"] = len(pulls)
    repo["last_pr_update"] = pulls[0].get("updated_at") if pulls else None
    repo["releases_count"] = len(releases)
    repo["released_releases_count"] = len(
        [
            item
            for item in sorted_releases
            if item.get("published_at") != datetime.datetime.fromtimestamp(1)
        ]
    )
    repo["last_release_name"] = (
        sorted_releases[0].get("name") if sorted_releases else None
    )
    repo["last_release_date"] = (
        sorted_releases[0].get("published_at") if sorted_releases else None
    )
    repo["first_release_name"] = (
        sorted_releases[-1].get("name") if sorted_releases else None
    )
    repo["first_release_date"] = (
        sorted_releases[-1].get("published_at") if sorted_releases else None
    )


def map_repo(repo: dict):
    g = lambda p: repo.get(p, "GREPPABLEERROR")
    return {
        "name": g("name"),
        "url": g("url"),
        "description": g("description"),
        "last_push": g("pushed_at"),
        "size_on_disk": g("size"),
        "language": g("language"),
        "topics": "|".join(g("topics")),
        "issues_count": g("open_issues"),
        "branches_count": g("branches_count"),
        "pr_count": g("pr_count"),
        "last_pr_update": g("last_pr_update"),
        "releases_count": g("releases_count"),
        "released_releases_count": g("released_releases_count"),
        "last_release_name": g("last_release_name"),
        "last_release_date": g("last_release_date"),
        "first_release_name": g("first_release_name"),
        "first_release_date": g("first_release_date"),
        "is_archived": g("archived"),
    }


interesting_data = [map_repo(repo) for repo in all_interesting_repos]

with open("interesting_data.json", "w") as file:
    json_indented_dump(interesting_data, file)

with open("interesting_data.csv", "w") as csvfile:
    r = csv.DictWriter(
        csvfile,
        delimiter=",",
        quotechar='"',
        fieldnames=map_repo({}).keys(),
        extrasaction="raise",
    )
    r.writeheader()
    r.writerows(interesting_data)

print("Done! Please run ./thinger.sh to finish the job.")

# A CAT-JQ COMMAND FOR AUTOCLONE:
# cat interesting_repos.json | jq -r '.[].ssh_url'
