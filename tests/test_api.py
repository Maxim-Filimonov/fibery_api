import os
import unittest
from dotenv import load_dotenv
from fibery_api.api import FiberyAPI, FiberyType, FiberyField
from fibery_api.api import TypeNotFoundError


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

    def test_get_type_by_name(self):
        fibery_api = FiberyAPI(token=self.token, account=self.workspace)
        type_name = "fibery/Button"
        result = fibery_api.get_type_by_name(type_name)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, FiberyType)
        self.assertEqual(result.fibery_name, type_name)

    def test_get_type_by_name_not_found(self):
        fibery_api = FiberyAPI(token=self.token, account=self.workspace)
        type_name = "nonexistent-type"
        with self.assertRaises(TypeNotFoundError):
            fibery_api.get_type_by_name(type_name)

    def test_create_entity(self):
        fibery_api = FiberyAPI(token=self.token, account=self.workspace)

        entity_type = "Demo/Player"
        entity_data = {
            "Demo/name": "Curtly Ambrose"
        }
        try:
            fields = [
                FiberyField(name="Demo/name", type="fibery/text", meta={}),
            ]
            fibery_api.create_database(entity_type, fields)
            result = fibery_api.create_entity(entity_type, entity_data)
            self.assertIsInstance(result, dict)
            self.assertIn("fibery/id", result)
            self.assertEqual(result["Demo/name"], entity_data["Demo/name"])
        finally:
            fibery_api.delete_database(entity_type)

    def test_create_database(self):
        fibery_api = FiberyAPI(token=self.token, account=self.workspace)
        database_name = "Demo/Player"
        fields = [
            FiberyField(name="Demo/name", type="fibery/text", meta={}),
        ]
        try:
            result = fibery_api.create_database(database_name, fields)
            self.assertEqual(result.success, True, result.result)
        finally:
            fibery_api.delete_database(database_name)


if __name__ == "__main__":
    unittest.main()
