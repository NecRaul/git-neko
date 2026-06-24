import unittest
from unittest.mock import MagicMock, patch

import requests

from git_neko import config, github


class _FakeResponse:
    def __init__(self, payload, status_code: int, text: str = ""):
        self._payload = payload
        self.status_code = status_code
        self.text = text

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(
                f"{self.status_code} {self.text}",
                response=MagicMock(status_code=self.status_code),
            )


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
        calls: list[tuple[str, dict | None, dict | None]] = []
        filters = config.DEFAULT_CONFIG.get("filters")
        headers = None

        responses = [
            _FakeResponse(
                payload=[fake_repo("repo-1"), fake_repo("repo", owner="someone-else")],
                status_code=200,
            ),
            _FakeResponse(payload=[], status_code=200),
        ]

        def fake_get(url, headers=None, params=None):
            calls.append((url, headers, params))
            return responses.pop(0)

        with patch.object(github.requests, "get", side_effect=fake_get):
            repos = github.get_repositories("alice", headers=headers)
            filtered_repos = github.filter_repositories(repos, "alice", [], filters)

        self.assertEqual(filtered_repos, [fake_repo("repo-1")])
        self.assertEqual(
            calls,
            [
                (
                    "https://api.github.com/users/alice/repos",
                    headers,
                    {"per_page": 100, "page": 1},
                ),
                (
                    "https://api.github.com/users/alice/repos",
                    headers,
                    {"per_page": 100, "page": 2},
                ),
            ],
        )

    def test_get_repositories_uses_authenticated_endpoint_with_token(self):
        calls: list[tuple[str, dict | None, dict | None]] = []
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

        def fake_get(url, headers=None, params=None):
            calls.append((url, headers, params))
            return responses.pop(0)

        with patch.object(github.requests, "get", side_effect=fake_get):
            repos = github.get_repositories("alice", headers=headers)
            filtered_repos = github.filter_repositories(repos, "alice", [], filters)

        self.assertEqual(filtered_repos, [fake_repo("private-repo")])
        self.assertEqual(
            calls,
            [
                (
                    "https://api.github.com/user/repos",
                    headers,
                    {"per_page": 100, "page": 1},
                ),
                (
                    "https://api.github.com/user/repos",
                    headers,
                    {"per_page": 100, "page": 2},
                ),
            ],
        )

    def test_get_repositories_stops_and_returns_collected_on_error(self):
        calls: list[tuple[str, dict | None, dict | None]] = []
        headers = None

        responses = [
            _FakeResponse(payload=[fake_repo("repo-1")], status_code=200),
            _FakeResponse(payload=[], status_code=500, text="boom"),
        ]

        def fake_get(url, headers=None, params=None):
            calls.append((url, headers, params))
            return responses.pop(0)

        with patch.object(github.requests, "get", side_effect=fake_get):
            with self.assertRaises(requests.HTTPError):
                github.get_repositories("alice", headers=headers)
