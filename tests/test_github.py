import unittest

import requests

from git_neko import config, github
from git_neko.models import FiltersConfig, Repository


class GitHubIntegrationTests(unittest.TestCase):
    def test_fetches_public_repositories_from_necraul_account(self) -> None:
        filters: FiltersConfig = config.DEFAULT_CONFIG["filters"]
        with requests.Session() as session:
            repos: list[Repository] = github.get_repositories(
                session, username="NecRaul", headers=None
            )
            filtered_repos: list[Repository] = github.filter_repositories(
                repos, "NecRaul", [], filters
            )

        self.assertIsInstance(filtered_repos, list)
        self.assertGreater(len(filtered_repos), 60)
        self.assertTrue(
            all(repo["owner"]["login"] == "NecRaul" for repo in filtered_repos)
        )
