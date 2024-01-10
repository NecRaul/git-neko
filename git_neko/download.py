import requests
import os
import subprocess
import shutil
import tarfile
import zipfile


def with_request(repo, headers):
    repo_name = repo["name"]
    tarball_url = f"{repo['html_url']}/tarball/{repo['default_branch']}"
    if not os.path.exists(repo_name):
        os.mkdir(repo_name)
        print(f"Downloading the repository '{repo_name}'...")
    else:
        print(f"Updating the repository '{repo_name}'...")
        shutil.rmtree(repo_name)
    response = requests.get(tarball_url, headers=headers)
    with open(f"{repo_name}.tar.gz", "wb") as file:
        file.write(response.content)
    with tarfile.open(f"{repo_name}.tar.gz", "r:gz") as tar_ref:
        tar_info = tar_ref.getmembers()[1:]
        for member in tar_info:
            member.name = f"{repo_name}/{member.name.split('/', 1)[-1]}"
            tar_ref.extract(member)
    os.remove(f"{repo_name}.tar.gz")


def with_git(repo):
    repo_name = repo["name"]
    repo_pull_url = repo["ssh_url"]
    if not os.path.exists(repo_name):
        subprocess.call(["git", "clone", "--recursive", repo_pull_url])
    else:
        subprocess.call(["git", "-C", repo_name, "pull", "--recurse-submodules"])


def download_repositories(username, token, git_check):
    if not token:
        API_ENDPOINT = f"https://api.github.com/users/{username}/repos"
        headers = None
    else:
        API_ENDPOINT = f"https://api.github.com/user/repos"
        headers = {
            "Authorization": f"token {token}",
        }

    response = requests.get(API_ENDPOINT, headers=headers)

    if response.status_code == 200:
        for repo in response.json():
            if not username in repo["full_name"]:
                continue
            with_request(repo, headers) if not git_check else with_git(repo)
    else:
        print(response.status_code, response.text)
