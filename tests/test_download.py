import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

import requests

from git_neko import download


class _FakeResponse:
    def __init__(self, status_code: int, payload, text: str = ""):
        self.status_code = status_code
        self._payload = payload
        self.text = text

    def json(self):
        return self._payload


class DownloadTests(unittest.TestCase):
    def test_get_repositories_uses_public_endpoint_without_token(self):
        self.assertEqual(requests.__name__, "requests")
        calls: list[tuple[str, dict | None]] = []

        responses = [
            _FakeResponse(
                200,
                [
                    {"full_name": "alice/repo-1"},
                    {"full_name": "someone-else/repo"},
                ],
            ),
            _FakeResponse(200, []),
        ]

        def fake_get(url, headers=None):
            calls.append((url, headers))
            return responses.pop(0)

        with patch.object(download.requests, "get", side_effect=fake_get):
            repos = download.get_repositories("alice", headers=None)

        self.assertEqual(repos, [{"full_name": "alice/repo-1"}])
        self.assertEqual(
            calls,
            [
                ("https://api.github.com/users/alice/repos?per_page=100&page=1", None),
                ("https://api.github.com/users/alice/repos?per_page=100&page=2", None),
            ],
        )

    def test_get_repositories_uses_authenticated_endpoint_with_token(self):
        calls: list[tuple[str, dict | None]] = []
        headers = {"Authorization": "token abc123"}

        responses = [
            _FakeResponse(
                200,
                [
                    {"full_name": "alice/private-repo"},
                    {"full_name": "other/private-repo"},
                ],
            ),
            _FakeResponse(200, []),
        ]

        def fake_get(url, headers=None):
            calls.append((url, headers))
            return responses.pop(0)

        with patch.object(download.requests, "get", side_effect=fake_get):
            repos = download.get_repositories("alice", headers=headers)

        self.assertEqual(repos, [{"full_name": "alice/private-repo"}])
        self.assertEqual(
            calls,
            [
                ("https://api.github.com/user/repos?per_page=100&page=1", headers),
                ("https://api.github.com/user/repos?per_page=100&page=2", headers),
            ],
        )

    def test_get_repositories_stops_and_returns_collected_on_error(self):
        responses = [
            _FakeResponse(200, [{"full_name": "alice/repo-1"}]),
            _FakeResponse(500, [], text="boom"),
        ]

        def fake_get(url, headers=None):
            return responses.pop(0)

        output = io.StringIO()
        with (
            patch.object(download.requests, "get", side_effect=fake_get),
            redirect_stdout(output),
        ):
            repos = download.get_repositories("alice", headers=None)

        self.assertEqual(repos, [{"full_name": "alice/repo-1"}])
        self.assertIn("500 boom", output.getvalue())
