import shutil
import subprocess
import tarfile
from pathlib import Path

import requests

from git_neko import util
from git_neko.models import FiltersConfig, Organization, Repository


def download_with_requests(
    repos: list[Repository], headers: dict[str, str] | None, directory: Path
) -> None:
    repo_count: int = len(repos)
    count_digit: int = len(str(repo_count))
    util.validate_directory(directory)
    directory.mkdir(parents=True, exist_ok=True)
    for i, repo in enumerate(repos, start=1):
        tarball_url: str = f"{repo['html_url']}/tarball/{repo['default_branch']}"
        repo_name: str = repo["name"]
        repo_path: Path = directory / repo_name
        util.validate_directory(repo_path)
        if not repo_path.exists():
            print(f"[{i:>{count_digit}}/{repo_count}] Downloading '{repo_path}'...")
        else:
            shutil.rmtree(repo_path)
            print(f"[{i:>{count_digit}}/{repo_count}] Updating '{repo_path}'...")
        response: requests.Response = requests.get(
            tarball_url, headers=headers, timeout=30
        )
        response.raise_for_status()
        tar_path: Path = repo_path.with_suffix(".tar.gz")
        tar_path.write_bytes(response.content)
        with tarfile.open(tar_path, "r:gz") as tar_ref:
            root_path: Path = directory / next(
                member.name.split("/", 1)[0]
                for member in tar_ref.getmembers()
                if member.name
            )
            tar_ref.extractall(directory)
        Path(root_path).rename(repo_path)
        tar_path.unlink()


def download_with_git(
    repos: list[Repository], git_args: tuple[list[str], list[str]], directory: Path
) -> None:
    repo_count: int = len(repos)
    count_digit: int = len(str(repo_count))
    util.validate_directory(directory)
    directory.mkdir(parents=True, exist_ok=True)
    clone_args, pull_args = git_args
    for i, repo in enumerate(repos, start=1):
        repo_pull_url: str = repo["ssh_url"]
        repo_name: str = repo["name"]
        repo_path: Path = directory / repo_name
        util.validate_directory(repo_path)
        if not repo_path.exists():
            print(f"[{i:>{count_digit}}/{repo_count}]", end=" ", flush=True)
            cmd = ["git", "clone", *clone_args, repo_pull_url, repo_path.as_posix()]
            subprocess.call(cmd)
        else:
            print(f"[{i:>{count_digit}}/{repo_count}] Pulling '{repo_path}'...")
            cmd = ["git", "-C", repo_path.as_posix(), "pull", *pull_args]
            subprocess.call(cmd)


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
    username: str,
    token: str | None,
    git_enabled: bool,
    git_args: tuple[list[str], list[str]],
    filters: FiltersConfig,
    directory: Path,
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
        download_with_git(filtered_repos, git_args, directory)
    else:
        download_with_requests(filtered_repos, headers, directory)
