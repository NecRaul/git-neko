import io
import sys
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from unittest.mock import patch

from git_neko import cli, config
from git_neko.models import FiltersConfig


class CliTests(unittest.TestCase):
    def test_main_uses_explicit_cli_arguments(self) -> None:
        called: dict[
            str,
            tuple[
                str, str | None, bool, tuple[list[str], list[str]], FiltersConfig, Path
            ],
        ] = {}
        filters: FiltersConfig = config.DEFAULT_CONFIG["filters"]
        clone_args: list[str] = config.DEFAULT_CONFIG["download"]["git"]["clone_args"]
        pull_args: list[str] = config.DEFAULT_CONFIG["download"]["git"]["pull_args"]
        git_args: tuple[list[str], list[str]] = (clone_args, pull_args)
        directory_value: str | None = config.DEFAULT_CONFIG["download"]["directory"]
        assert directory_value is not None
        directory: Path = Path(directory_value).expanduser()

        def fake_download_repositories(
            username: str,
            token: str | None,
            git_enabled: bool,
            git_args: tuple[list[str], list[str]],
            filters: FiltersConfig,
            directory: Path,
        ) -> None:
            called["args"] = (
                username,
                token,
                git_enabled,
                git_args,
                filters,
                directory,
            )

        with (
            patch.object(
                cli.github,
                "download_repositories",
                side_effect=fake_download_repositories,
            ),
            patch.object(
                sys,
                "argv",
                ["git-neko", "-u", "alice", "-t", "token123", "-g", "--no-config"],
            ),
        ):
            cli.main()

        self.assertEqual(
            called["args"], ("alice", "token123", True, git_args, filters, directory)
        )

    def test_main_uses_environment_variables_when_enabled(self) -> None:
        called: dict[
            str,
            tuple[
                str, str | None, bool, tuple[list[str], list[str]], FiltersConfig, Path
            ],
        ] = {}
        git_enabled: bool = config.DEFAULT_CONFIG["download"]["git"]["enabled"]
        filters: FiltersConfig = config.DEFAULT_CONFIG["filters"]
        clone_args: list[str] = config.DEFAULT_CONFIG["download"]["git"]["clone_args"]
        pull_args: list[str] = config.DEFAULT_CONFIG["download"]["git"]["pull_args"]
        git_args: tuple[list[str], list[str]] = (clone_args, pull_args)
        directory_value: str | None = config.DEFAULT_CONFIG["download"]["directory"]
        assert directory_value is not None
        directory: Path = Path(directory_value).expanduser()

        def fake_download_repositories(
            username: str,
            token: str | None,
            git_enabled: bool,
            git_args: tuple[list[str], list[str]],
            filters: FiltersConfig,
            directory: Path,
        ) -> None:
            called["args"] = (
                username,
                token,
                git_enabled,
                git_args,
                filters,
                directory,
            )

        with (
            patch.object(
                cli.github,
                "download_repositories",
                side_effect=fake_download_repositories,
            ),
            patch.dict(
                "os.environ",
                {
                    "GITHUB_USERNAME": "env-user",
                    "GITHUB_PERSONAL_ACCESS_TOKEN": "env-token",
                },
                clear=False,
            ),
            patch.object(sys, "argv", ["git-neko", "-e", "--no-config"]),
        ):
            cli.main()

        self.assertEqual(
            called["args"],
            ("env-user", "env-token", git_enabled, git_args, filters, directory),
        )

    def test_main_prints_hint_if_username_missing(self) -> None:
        stderr: io.StringIO = io.StringIO()

        with (
            patch.object(sys, "argv", ["git-neko", "--no-config"]),
            redirect_stderr(stderr),
            self.assertRaises(SystemExit) as ctx,
        ):
            cli.main()

        self.assertEqual(ctx.exception.code, 2)
        self.assertIn("Pass your GitHub username with -u.", stderr.getvalue())
