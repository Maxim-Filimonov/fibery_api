import unittest
from dotenv import load_dotenv
from fibery.auth import FiberyAuth
import os


class TestFiberyAuth(unittest.TestCase):
    def setUp(self) -> None:
        load_dotenv()
        self.workspace = os.environ.get("FIBERY_WORKSPACE")
        self.token = os.environ.get("FIBERY_TOKEN")
        return super().setUp()

    def test_authenticate_success(self):
        fibery_auth = FiberyAuth(
            token=self.token, workspace=self.workspace)
        self.assertTrue(fibery_auth.authenticate())

    def test_authenticate_failure_invalid_token(self):
        fibery_auth = FiberyAuth(
            token="INVALID_TOKEN", workspace=self.workspace)
        self.assertFalse(fibery_auth.authenticate())

    def test_authenticate_failure_invalid_workspace(self):
        fibery_auth = FiberyAuth(
            token=self.token, workspace="INVALID_WORKSPACE")
        self.assertFalse(fibery_auth.authenticate())


if __name__ == "__main__":
    unittest.main()
