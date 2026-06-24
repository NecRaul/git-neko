import unittest

from git_neko import config, github
from git_neko.models import FiltersConfig, Repository


class GithubIntegrationTests(unittest.TestCase):
    def test_fetches_public_repositories_from_necraul_account(self) -> None:
        filters: FiltersConfig = config.DEFAULT_CONFIG["filters"]
        repos: list[Repository] = github.get_repositories(
            username="NecRaul", headers=None
        )
        filtered_repos: list[Repository] = github.filter_repositories(
            repos, "NecRaul", [], filters
        )

        self.assertIsInstance(filtered_repos, list)
        self.assertGreater(len(filtered_repos), 60)
        self.assertTrue(
            all(repo["owner"]["login"] == "NecRaul" for repo in filtered_repos)
        )
