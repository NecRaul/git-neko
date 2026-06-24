import argparse
import copy
import json
import os
import platform
from pathlib import Path
from typing import cast

from git_neko import util
from git_neko.models import Config, ConfigDict

CONFIG_NAMESPACE = "necraul"
CONFIG_NAME = "git-neko.json"

DEFAULT_CONFIG: Config = {
    "github": {
        "username": None,
        "token": None,
        "environment": False,
    },
    "download": {
        "git": {
            "enabled": True,
            "clone_args": ["--recursive"],
            "pull_args": ["--recurse-submodules"],
        },
    },
    "filters": {
        "access": ["owner"],
        "visibility": ["public", "private"],
        "fork": "both",
        "archived": "both",
        "template": "both",
    },
}


def get_default_config_path() -> Path:
    match platform.system():
        case "Windows":
            base: str | None = os.getenv("APPDATA")
            if base:
                config_dir: Path = Path(base)
            else:
                config_dir: Path = Path.home() / "AppData" / "Roaming"
        case "Darwin":
            config_dir: Path = Path.home() / "Library" / "Application Support"
        case "Linux":
            config_dir: Path = Path(
                os.getenv("XDG_CONFIG_HOME", Path.home() / ".config")
            )
        case _:
            config_dir: Path = Path(
                os.getenv("XDG_CONFIG_HOME", Path.home() / ".config")
            )
    return config_dir / CONFIG_NAMESPACE / CONFIG_NAME


def load_config(path: str | None = None) -> Config:
    if path is None:
        path: Path = get_default_config_path()
    else:
        path: Path = Path(path).expanduser()
    if not path.exists():
        return copy.deepcopy(DEFAULT_CONFIG)
    with path.open("r", encoding="utf-8") as f:
        user_cfg: Config = json.load(f)
    return merge_config(DEFAULT_CONFIG, user_cfg)


def merge_config(base: Config, override: Config) -> Config:
    result: Config = copy.deepcopy(base)
    result_dict: ConfigDict = cast(ConfigDict, result)
    override_dict: ConfigDict = cast(ConfigDict, override)
    for key, value in override_dict.items():
        if isinstance(value, dict) and isinstance(result_dict.get(key), dict):
            result_dict[key] = merge_config(result_dict[key], value)
        else:
            result_dict[key] = value
    return cast(Config, result_dict)


def save_config(cfg: Config, path: str | None = None) -> Path:
    if path is None:
        path: Path = get_default_config_path()
    path: Path = Path(path).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)
        f.write("\n")
    return path.absolute()


def load_effective_config(path: str | None = None, no_config: bool = False) -> Config:
    if no_config:
        return copy.deepcopy(DEFAULT_CONFIG)
    if path:
        return load_config(path)
    return load_config()


def apply_environment_overrides(config: Config) -> Config:
    overrides: Config = {
        "github": {
            "username": os.getenv("GITHUB_USERNAME"),
            "token": os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN"),
        }
    }
    return merge_config(config, util.remove_none(overrides))


def apply_cli_overrides(config: Config, args: argparse.Namespace) -> Config:
    overrides: Config = {
        "github": {
            "username": args.username,
            "token": args.token,
        },
        "download": {
            "git": {
                "enabled": args.git,
            },
        },
        "filters": {
            "access": args.access,
            "visibility": args.visibility,
            "fork": args.fork,
            "archived": args.archived,
            "template": args.template,
        },
    }
    return merge_config(config, util.remove_none(overrides))
