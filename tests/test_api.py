import os
import unittest
from dotenv import load_dotenv
from fibery_api.api import FiberyAPI


class TestFiberyAPI(unittest.TestCase):
    def setUp(self) -> None:
        load_dotenv()
        self.workspace = os.environ.get("FIBERY_WORKSPACE")
        self.token = os.environ.get("FIBERY_TOKEN")
        return super().setUp()

    def test_get_schema_success(self):
        fibery_api = FiberyAPI(token=self.token, account=self.workspace)
        result = fibery_api.get_schema()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, list)
        self.assertTrue("success" in result[0] and result[0]["success"])

    def test_get_schema_with_description(self):
        fibery_api = FiberyAPI(token=self.token, account=self.workspace)
        result = fibery_api.get_schema(with_description=True)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, list)
        self.assertTrue("success" in result[0] and result[0]["success"])


if __name__ == "__main__":
    unittest.main()
