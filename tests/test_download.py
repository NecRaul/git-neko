import unittest
from typing import Any
from unittest.mock import MagicMock, patch

import requests

from git_neko import config, github
from git_neko.models import FiltersConfig


class _FakeResponse:
    def __init__(
        self, payload: list[dict[str, Any]], status_code: int, text: str = ""
    ) -> None:
        self._payload: list[dict[str, Any]] = payload
        self.status_code: int = status_code
        self.text: str = text

    def json(self) -> list[dict[str, Any]]:
        return self._payload

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise requests.HTTPError(
                f"{self.status_code} {self.text}",
                response=MagicMock(status_code=self.status_code),
            )


def fake_repo(
    name: str,
    owner: str = "alice",
    visibility: str = "public",
    fork: bool = False,
    archived: bool = False,
    template: bool = False,
) -> dict[str, Any]:
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
    def test_get_repositories_uses_public_endpoint_without_token(self) -> None:
        calls: list[tuple[str, dict[str, str] | None, dict[str, Any] | None]] = []
        filters: FiltersConfig = config.DEFAULT_CONFIG["filters"]
        headers: dict[str, str] | None = None

        responses: list[_FakeResponse] = [
            _FakeResponse(
                payload=[fake_repo("repo-1"), fake_repo("repo", owner="someone-else")],
                status_code=200,
            ),
            _FakeResponse(payload=[], status_code=200),
        ]

        def fake_get(
            url: str,
            headers: dict[str, str] | None = None,
            params: dict[str, Any] | None = None,
        ) -> _FakeResponse:
            calls.append((url, headers, params))
            return responses.pop(0)

        with patch.object(github.requests, "get", side_effect=fake_get):
            repos: list[dict[str, Any]] = github.get_repositories(
                "alice", headers=headers
            )
            filtered_repos: list[dict[str, Any]] = github.filter_repositories(
                repos, "alice", [], filters
            )

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

    def test_get_repositories_uses_authenticated_endpoint_with_token(self) -> None:
        calls: list[tuple[str, dict[str, str] | None, dict[str, Any] | None]] = []
        filters: FiltersConfig = config.DEFAULT_CONFIG["filters"]
        headers: dict[str, str] | None = {"Authorization": "token abc123"}

        responses: list[_FakeResponse] = [
            _FakeResponse(
                payload=[
                    fake_repo("private-repo"),
                    fake_repo("private-repo", owner="someone-else"),
                ],
                status_code=200,
            ),
            _FakeResponse(payload=[], status_code=200),
        ]

        def fake_get(
            url: str,
            headers: dict[str, str] | None = None,
            params: dict[str, Any] | None = None,
        ) -> _FakeResponse:
            calls.append((url, headers, params))
            return responses.pop(0)

        with patch.object(github.requests, "get", side_effect=fake_get):
            repos: list[dict[str, Any]] = github.get_repositories(
                "alice", headers=headers
            )
            filtered_repos: list[dict[str, Any]] = github.filter_repositories(
                repos, "alice", [], filters
            )

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

    def test_get_repositories_stops_and_returns_collected_on_error(self) -> None:
        calls: list[tuple[str, dict[str, str] | None, dict[str, Any] | None]] = []
        headers: dict[str, str] | None = None

        responses: list[_FakeResponse] = [
            _FakeResponse(payload=[fake_repo("repo-1")], status_code=200),
            _FakeResponse(payload=[], status_code=500, text="boom"),
        ]

        def fake_get(
            url: str,
            headers: dict[str, str] | None = None,
            params: dict[str, Any] | None = None,
        ) -> _FakeResponse:
            calls.append((url, headers, params))
            return responses.pop(0)

        with patch.object(github.requests, "get", side_effect=fake_get):
            with self.assertRaises(requests.HTTPError):
                github.get_repositories("alice", headers=headers)
