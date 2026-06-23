import unittest

from git_neko.download import get_repositories


class GithubIntegrationTests(unittest.TestCase):
    def test_fetches_public_repositories_from_necraul_account(self):
        repos = get_repositories(username="NecRaul", headers=None)

        self.assertIsInstance(repos, list)
        self.assertGreater(len(repos), 60)
        self.assertTrue(all(repo["full_name"].startswith("NecRaul/") for repo in repos))
