import shutil
import subprocess
import tarfile
from pathlib import Path

import requests

from git_neko import util


def download_with_requests(repos, headers):
    repo_count = len(repos)
    count_digit = len((str(repo_count)))
    for i, repo in enumerate(repos, start=1):
        tarball_url = f"{repo['html_url']}/tarball/{repo['default_branch']}"
        repo_name = repo["name"]
        repo_dir = Path(repo_name)
        if not repo_dir.exists():
            print(f"[{i:>{count_digit}}/{repo_count}] Downloading '{repo_name}'...")
        else:
            shutil.rmtree(repo_dir)
            print(f"[{i:>{count_digit}}/{repo_count}] Updating '{repo_name}'...")
        response = requests.get(tarball_url, headers=headers, timeout=30)
        response.raise_for_status()
        tar_path = Path(f"{repo_name}.tar.gz")
        tar_path.write_bytes(response.content)
        with tarfile.open(tar_path, "r:gz") as tar_ref:
            root_dir = next(
                member.name.split("/", 1)[0]
                for member in tar_ref.getmembers()
                if member.name
            )
            tar_ref.extractall()
        Path(root_dir).rename(repo_dir)
        tar_path.unlink()


def download_with_git(repos):
    repo_count = len(repos)
    count_digit = len(str(repo_count))
    for i, repo in enumerate(repos, start=1):
        repo_name = repo["name"]
        repo_pull_url = repo["ssh_url"]
        if not Path(repo_name).exists():
            print(f"[{i:>{count_digit}}/{repo_count}]", end=" ", flush=True)
            subprocess.call(["git", "clone", "--recursive", repo_pull_url])
        else:
            print(f"[{i:>{count_digit}}/{repo_count}] Pulling '{repo_name}'...")
            subprocess.call(["git", "-C", repo_name, "pull", "--recurse-submodules"])


def github_get_all(endpoint, headers):
    items = []
    page = 1

    while True:
        response = requests.get(
            endpoint, headers=headers, params={"per_page": 100, "page": page}
        )

        response.raise_for_status()

        page_items = response.json()

        if not page_items:
            break

        items.extend(page_items)
        page += 1

    return items


def get_repositories(username, headers):
    if not headers:
        endpoint = f"https://api.github.com/users/{username}/repos"
    else:
        endpoint = "https://api.github.com/user/repos"

    return github_get_all(endpoint, headers)


def get_organizations(username, headers):
    if not headers:
        endpoint = f"https://api.github.com/users/{username}/orgs"
    else:
        endpoint = "https://api.github.com/user/orgs"

    return github_get_all(endpoint, headers)


def filter_repositories(repos, username, orgs, filters):
    return [
        repo
        for repo in repos
        if util.matches_access(repo, username, orgs, filters["access"])
        and util.matches_visibility(repo, filters["visibility"])
        and util.matches_fork(repo, filters["fork"])
        and util.matches_archived(repo, filters["archived"])
        and util.matches_template(repo, filters["template"])
    ]


def download_repositories(username, token, git_enabled, filters):
    headers = {"Authorization": f"token {token}"} if token else None
    repos = get_repositories(username, headers)
    orgs = get_organizations(username, headers)
    filtered_repos = filter_repositories(repos, username, orgs, filters)

    if git_enabled:
        download_with_git(filtered_repos)
    else:
        download_with_requests(filtered_repos, headers)
