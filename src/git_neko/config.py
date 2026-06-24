import copy
import json
import os
import platform
from pathlib import Path

from git_neko import util

CONFIG_NAMESPACE = "necraul"
CONFIG_NAME = "git-neko.json"

DEFAULT_CONFIG = {
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


def get_default_config_path():
    match platform.system():
        case "Windows":
            base = os.getenv("APPDATA")
            if base:
                config_dir = Path(base)
            else:
                config_dir = Path.home() / "AppData" / "Roaming"
        case "Darwin":
            config_dir = Path.home() / "Library" / "Application Support"
        case "Linux":
            config_dir = Path(os.getenv("XDG_CONFIG_HOME", Path.home() / ".config"))
        case _:
            config_dir = Path(os.getenv("XDG_CONFIG_HOME", Path.home() / ".config"))
    return config_dir / CONFIG_NAMESPACE / CONFIG_NAME


def load_config(path=None):
    if path is None:
        path = get_default_config_path()
    else:
        path = Path(path).expanduser()
    if not path.exists():
        return copy.deepcopy(DEFAULT_CONFIG)
    with path.open("r", encoding="utf-8") as f:
        user_cfg = json.load(f)
    return merge_config(DEFAULT_CONFIG, user_cfg)


def merge_config(base, override):
    result = copy.deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = merge_config(result[key], value)
        else:
            result[key] = value
    return result


def save_config(cfg, path=None):
    if path is None:
        path = get_default_config_path()
    path = Path(path).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)
        f.write("\n")
    return path.absolute()


def load_effective_config(path=None, no_config=False):
    if no_config:
        return copy.deepcopy(DEFAULT_CONFIG)
    if path:
        return load_config(path)
    return load_config()


def apply_environment_overrides(config):
    overrides = {
        "github": {
            "username": os.getenv("GITHUB_USERNAME"),
            "token": os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN"),
        }
    }
    return merge_config(config, util.remove_none(overrides))


def apply_cli_overrides(config, args):
    overrides = {
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
