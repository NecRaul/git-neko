import argparse
import os

from .download import download_repositories
from .version import __version__


def main():
    parser = argparse.ArgumentParser(
        description="Download specified user's all repositories at once",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        epilog="Example: %(prog)s -u NecRaul -g",
    )
    parser.add_argument("-v", "--version", action="version", version=__version__)
    parser.add_argument(
        "-u",
        "--username",
        type=str,
        metavar="Username",
        help="Github username to download repositories from.",
    )
    parser.add_argument(
        "-t",
        "--token",
        type=str,
        metavar="Token",
        help="Github public access token if you want to also download private "
        "repositories.",
    )
    parser.add_argument(
        "-e",
        "--environment",
        action="store_true",
        help="Whether to use environment variables or not.",
    )
    parser.add_argument(
        "-g",
        "--git",
        action="store_true",
        help="Whether to download with git or not. False by default since it's "
        "dependent on whether or not git is downloaded (and your ssh/gpg key).",
    )
    parser.add_argument(
        "--access",
        nargs="+",
        choices=["owner", "collaborator", "accessible", "org-member", "all"],
        default=["owner"],
        help="Access types to include (multiple allowed).",
    )
    parser.add_argument(
        "--visibility",
        nargs="+",
        choices=["public", "private", "internal", "all"],
        default=["all"],
        help="Visibility levels to include (multiple allowed).",
    )
    parser.add_argument(
        "--fork",
        choices=["yes", "no", "both"],
        default="both",
        help="Filter fork repositories.",
    )
    parser.add_argument(
        "--archived",
        default="both",
        choices=["yes", "no", "both"],
        help="Filter archived repositories.",
    )
    parser.add_argument(
        "--template",
        default="both",
        choices=["yes", "no", "both"],
        help="Filter template repositories.",
    )

    args = parser.parse_args()

    if args.environment:
        username = os.getenv("GITHUB_USERNAME")
        token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    else:
        username = args.username
        token = args.token

    git_check = args.git
    options = {
        "access": args.access,
        "visibility": args.visibility,
        "fork": args.fork,
        "archived": args.archived,
        "template": args.template,
    }

    if not username:
        print("Pass your Github username with -u.")
    else:
        download_repositories(username, token, git_check, options)
