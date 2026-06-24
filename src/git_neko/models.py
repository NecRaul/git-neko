from typing import Any, TypeAlias, TypedDict


class GithubConfig(TypedDict, total=False):
    username: str | None
    token: str | None
    environment: bool


class GitDownloadConfig(TypedDict, total=False):
    enabled: bool
    clone_args: list[str]
    pull_args: list[str]


class DownloadConfig(TypedDict, total=False):
    git: GitDownloadConfig


class FiltersConfig(TypedDict, total=False):
    access: list[str]
    visibility: list[str]
    fork: str
    archived: str
    template: str


class Config(TypedDict, total=False):
    github: GithubConfig
    download: DownloadConfig
    filters: FiltersConfig


ConfigDict: TypeAlias = dict[str, Any]
Repository: TypeAlias = dict[str, Any]
Organization: TypeAlias = dict[str, Any]
