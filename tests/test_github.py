import unittest

from git_neko import config, download


class GithubIntegrationTests(unittest.TestCase):
    def test_fetches_public_repositories_from_necraul_account(self):
        filters = config.DEFAULT_CONFIG.get("filters")
        repos = download.get_repositories(username="NecRaul", headers=None)
        filtered_repos = download.filter_repositories(repos, "NecRaul", [], filters)

        self.assertIsInstance(filtered_repos, list)
        self.assertGreater(len(filtered_repos), 60)
        self.assertTrue(
            all(repo["owner"]["login"] == "NecRaul" for repo in filtered_repos)
        )
