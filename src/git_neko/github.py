import shutil
import subprocess
import tarfile
from pathlib import Path

import requests

from git_neko import util
from git_neko.models import FiltersConfig, Organization, Repository


def download_with_requests(
    repos: list[Repository], headers: dict[str, str] | None
) -> None:
    repo_count: int = len(repos)
    count_digit: int = len((str(repo_count)))
    for i, repo in enumerate(repos, start=1):
        tarball_url: str = f"{repo['html_url']}/tarball/{repo['default_branch']}"
        repo_name: str = repo["name"]
        repo_dir: Path = Path(repo_name)
        if not repo_dir.exists():
            print(f"[{i:>{count_digit}}/{repo_count}] Downloading '{repo_name}'...")
        else:
            shutil.rmtree(repo_dir)
            print(f"[{i:>{count_digit}}/{repo_count}] Updating '{repo_name}'...")
        response: requests.Response = requests.get(
            tarball_url, headers=headers, timeout=30
        )
        response.raise_for_status()
        tar_path: Path = Path(f"{repo_name}.tar.gz")
        tar_path.write_bytes(response.content)
        with tarfile.open(tar_path, "r:gz") as tar_ref:
            root_dir: str = next(
                member.name.split("/", 1)[0]
                for member in tar_ref.getmembers()
                if member.name
            )
            tar_ref.extractall()
        Path(root_dir).rename(repo_dir)
        tar_path.unlink()


def download_with_git(repos: list[Repository]) -> None:
    repo_count: int = len(repos)
    count_digit: int = len(str(repo_count))
    for i, repo in enumerate(repos, start=1):
        repo_name: str = repo["name"]
        repo_pull_url: str = repo["ssh_url"]
        if not Path(repo_name).exists():
            print(f"[{i:>{count_digit}}/{repo_count}]", end=" ", flush=True)
            subprocess.call(["git", "clone", "--recursive", repo_pull_url])
        else:
            print(f"[{i:>{count_digit}}/{repo_count}] Pulling '{repo_name}'...")
            subprocess.call(["git", "-C", repo_name, "pull", "--recurse-submodules"])


def github_get_all(
    endpoint: str, headers: dict[str, str] | None
) -> list[Repository] | list[Organization]:
    items: list[Repository] | list[Organization] = []
    page = 1

    while True:
        response: requests.Response = requests.get(
            endpoint, headers=headers, params={"per_page": 100, "page": page}
        )
        response.raise_for_status()
        page_items: list[Repository] | list[Organization] = response.json()
        if not page_items:
            break
        items.extend(page_items)
        page += 1

    return items


def get_repositories(username: str, headers: dict[str, str] | None) -> list[Repository]:
    if not headers:
        endpoint = f"https://api.github.com/users/{username}/repos"
    else:
        endpoint = "https://api.github.com/user/repos"

    return github_get_all(endpoint, headers)


def get_organizations(
    username: str, headers: dict[str, str] | None
) -> list[Organization]:
    if not headers:
        endpoint = f"https://api.github.com/users/{username}/orgs"
    else:
        endpoint = "https://api.github.com/user/orgs"

    return github_get_all(endpoint, headers)


def filter_repositories(
    repos: list[Repository],
    username: str,
    orgs: list[str],
    filters: FiltersConfig,
) -> list[Repository]:
    return [
        repo
        for repo in repos
        if util.matches_access(repo, username, orgs, filters["access"])
        and util.matches_visibility(repo, filters["visibility"])
        and util.matches_fork(repo, filters["fork"])
        and util.matches_archived(repo, filters["archived"])
        and util.matches_template(repo, filters["template"])
    ]


def download_repositories(
    username: str, token: str | None, git_enabled: bool, filters: FiltersConfig
) -> None:
    headers: dict[str, str] | None = (
        {"Authorization": f"token {token}"} if token else None
    )
    repos: list[Repository] = get_repositories(username, headers)
    orgs: list[Organization] = get_organizations(username, headers)
    org_names: list[str] = [org["login"] for org in orgs]
    filtered_repos: list[Repository] = filter_repositories(
        repos, username, org_names, filters
    )

    if git_enabled:
        download_with_git(filtered_repos)
    else:
        download_with_requests(filtered_repos, headers)
