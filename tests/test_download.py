import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from git_neko import config, download


class _FakeResponse:
    def __init__(self, payload, status_code: int, text: str = ""):
        self._payload = payload
        self.status_code = status_code
        self.text = text

    def json(self):
        return self._payload


def fake_repo(
    name,
    owner="alice",
    visibility="public",
    fork=False,
    archived=False,
    template=False,
):
    return {
        "full_name": f"{owner}/{name}",
        "owner": {
            "login": owner,
            "type": "User",
        },
        "permissions": {
            "push": owner == "alice",
            "pull": True,
        },
        "visibility": visibility,
        "fork": fork,
        "archived": archived,
        "is_template": template,
    }


class DownloadTests(unittest.TestCase):
    def test_get_repositories_uses_public_endpoint_without_token(self):
        calls: list[tuple[str, dict | None]] = []
        filters = config.DEFAULT_CONFIG.get("filters")
        headers = None

        responses = [
            _FakeResponse(
                payload=[fake_repo("repo-1"), fake_repo("repo", owner="someone-else")],
                status_code=200,
            ),
            _FakeResponse(payload=[], status_code=200),
        ]

        def fake_get(url, headers=None):
            calls.append((url, headers))
            return responses.pop(0)

        with patch.object(download.requests, "get", side_effect=fake_get):
            repos = download.get_repositories("alice", headers=headers)
            filtered_repos = download.filter_repositories(repos, "alice", [], filters)

        self.assertEqual(filtered_repos, [fake_repo("repo-1")])
        self.assertEqual(
            calls,
            [
                (
                    "https://api.github.com/users/alice/repos?per_page=100&page=1",
                    headers,
                ),
                (
                    "https://api.github.com/users/alice/repos?per_page=100&page=2",
                    headers,
                ),
            ],
        )

    def test_get_repositories_uses_authenticated_endpoint_with_token(self):
        calls: list[tuple[str, dict | None]] = []
        filters = config.DEFAULT_CONFIG.get("filters")
        headers = {"Authorization": "token abc123"}

        responses = [
            _FakeResponse(
                payload=[
                    fake_repo("private-repo"),
                    fake_repo("private-repo", owner="someone-else"),
                ],
                status_code=200,
            ),
            _FakeResponse(payload=[], status_code=200),
        ]

        def fake_get(url, headers=None):
            calls.append((url, headers))
            return responses.pop(0)

        with patch.object(download.requests, "get", side_effect=fake_get):
            repos = download.get_repositories("alice", headers=headers)
            filtered_repos = download.filter_repositories(repos, "alice", [], filters)

        self.assertEqual(filtered_repos, [fake_repo("private-repo")])
        self.assertEqual(
            calls,
            [
                ("https://api.github.com/user/repos?per_page=100&page=1", headers),
                ("https://api.github.com/user/repos?per_page=100&page=2", headers),
            ],
        )

    def test_get_repositories_stops_and_returns_collected_on_error(self):
        calls: list[tuple[str, dict | None]] = []
        filters = config.DEFAULT_CONFIG.get("filters")
        headers = None

        responses = [
            _FakeResponse(payload=[fake_repo("repo-1")], status_code=200),
            _FakeResponse(payload=[], status_code=500, text="boom"),
        ]

        def fake_get(url, headers=None):
            calls.append((url, headers))
            return responses.pop(0)

        stdout = io.StringIO()
        with (
            patch.object(download.requests, "get", side_effect=fake_get),
            redirect_stdout(stdout),
        ):
            repos = download.get_repositories("alice", headers=headers)
            filtered_repos = download.filter_repositories(repos, "alice", [], filters)

        self.assertEqual(filtered_repos, [fake_repo("repo-1")])
        self.assertIn("500 boom", stdout.getvalue())
