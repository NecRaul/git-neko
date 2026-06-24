import argparse
import json
import sys

from git_neko import __version__, config, github


def main():
    parser = argparse.ArgumentParser(
        description="Download specified user's all repositories at once",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        epilog="Example: %(prog)s -u NecRaul -g",
    )
    parser.add_argument("-v", "--version", action="version", version=__version__)
    config_group = parser.add_mutually_exclusive_group()
    config_group.add_argument("--config", help="load configuration from file")
    config_group.add_argument(
        "--no-config", action="store_true", help="ignore configuration file"
    )
    config_group.add_argument(
        "--init-config",
        nargs="?",
        const=None,
        default=argparse.SUPPRESS,
        help="create default configuration file",
    )
    parser.add_argument(
        "--show-config",
        action="store_true",
        help="show effective configuration and exit",
    )
    parser.add_argument(
        "-u",
        "--username",
        type=str,
        help="GitHub username to fetch repositories from.",
    )
    parser.add_argument(
        "-t",
        "--token",
        type=str,
        help="GitHub public access token for private repositories.",
    )
    parser.add_argument(
        "-e",
        "--environment",
        action=argparse.BooleanOptionalAction,
        help="Read the username and token from environment variables.",
    )
    parser.add_argument(
        "-g",
        "--git",
        action=argparse.BooleanOptionalAction,
        help="Download repositories using git instead of archive downloads.",
    )
    parser.add_argument(
        "--access",
        nargs="+",
        choices=["owner", "collaborator", "accessible", "org-member", "all"],
        help="Access types to include (multiple allowed).",
    )
    parser.add_argument(
        "--visibility",
        nargs="+",
        choices=["public", "private", "internal", "all"],
        help="Visibility levels to include (multiple allowed).",
    )
    parser.add_argument(
        "--fork",
        choices=["yes", "no", "both"],
        help="Filter fork repositories.",
    )
    parser.add_argument(
        "--archived",
        choices=["yes", "no", "both"],
        help="Filter archived repositories.",
    )
    parser.add_argument(
        "--template",
        choices=["yes", "no", "both"],
        help="Filter template repositories.",
    )

    args = parser.parse_args()

    if hasattr(args, "init_config"):
        path = config.save_config(config.DEFAULT_CONFIG, args.init_config)
        print(f"Config created at {path}", file=sys.stderr)
        if args.show_config:
            print(json.dumps(config.DEFAULT_CONFIG, indent=2))
        return

    cfg = config.load_effective_config(path=args.config, no_config=args.no_config)

    if args.show_config:
        print(json.dumps(cfg, indent=2))
        return

    cli_environment = getattr(args, "environment", None)
    use_environment = (
        cli_environment if cli_environment is not None else cfg["github"]["environment"]
    )

    if use_environment:
        cfg = config.apply_environment_overrides(cfg)

    cfg = config.apply_cli_overrides(cfg, args)

    username = cfg["github"]["username"]
    token = cfg["github"]["token"]
    git_enabled = cfg["download"]["git"]["enabled"]
    filters = cfg["filters"]

    if not username:
        parser.error("Pass your Github username with -u.")

    github.download_repositories(username, token, git_enabled, filters)
