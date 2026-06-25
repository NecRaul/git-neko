from pathlib import Path
from typing import cast

from git_neko.models import Config, Repository


def matches_access(
    repo: Repository, username: str, org_names: list[str], filter: list[str]
) -> bool:
    if "all" in filter:
        return True

    owner = repo.get("owner", {})
    owner_login = owner.get("login")
    owner_type = owner.get("type")
    permissions = repo.get("permissions", {})

    if "owner" in filter and owner_login == username:
        return True
    if "collaborator" in filter and owner_login != username and permissions.get("push"):
        return True

    if "accessible" in filter and owner_login != username and permissions.get("pull"):
        return True

    if (
        "org-member" in filter
        and owner_login in org_names
        and owner_type == "Organization"
    ):
        return True

    return False


def matches_visibility(repo: Repository, filter: list[str]) -> bool:
    if "all" in filter:
        return True
    return repo["visibility"] in filter


def matches_fork(repo: Repository, filter: str) -> bool:
    return matches_bool(repo["fork"], filter)


def matches_archived(repo: Repository, filter: str) -> bool:
    return matches_bool(repo["archived"], filter)


def matches_template(repo: Repository, filter: str) -> bool:
    return matches_bool(repo["is_template"], filter)


def matches_bool(value: bool, filter: str) -> bool:
    if filter == "both":
        return True
    return value == (filter == "yes")


def remove_none(data: Config) -> Config:
    if isinstance(data, dict):
        return cast(
            Config,
            {
                key: remove_none(value) if isinstance(value, dict) else value  # ty:ignore[invalid-argument-type]
                for key, value in data.items()
                if value is not None
            },
        )
    return data


def validate_directory(path: Path) -> None:
    if path.exists() and not path.is_dir():
        raise NotADirectoryError(f"Path exists but is not a directory: {path}")
