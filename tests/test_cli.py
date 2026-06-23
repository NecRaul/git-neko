import io
import sys
import unittest
from contextlib import redirect_stderr
from unittest.mock import patch

from git_neko import cli, config


class CliTests(unittest.TestCase):
    def test_main_uses_explicit_cli_arguments(self):
        called = {}
        filters = config.DEFAULT_CONFIG.get("filters")

        def fake_download_repositories(username, token, git_enabled, filters):
            called["args"] = (username, token, git_enabled, filters)

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

        self.assertEqual(called["args"], ("alice", "token123", True, filters))

    def test_main_uses_environment_variables_when_enabled(self):
        called = {}
        filters = config.DEFAULT_CONFIG.get("filters")

        def fake_download_repositories(username, token, git_enabled, filters):
            called["args"] = (username, token, git_enabled, filters)

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

        self.assertEqual(called["args"], ("env-user", "env-token", True, filters))

    def test_main_prints_hint_if_username_missing(self):
        stderr = io.StringIO()

        with (
            patch.object(sys, "argv", ["git-neko", "--no-config"]),
            redirect_stderr(stderr),
            self.assertRaises(SystemExit) as ctx,
        ):
            cli.main()

        self.assertEqual(ctx.exception.code, 2)
        self.assertIn("Pass your Github username with -u.", stderr.getvalue())
