# api.py
import requests
from .auth import FiberyAuth
from pydantic import BaseModel, Field


class FiberyAPI:
    def __init__(self, token=None, account=None):
        self.auth = FiberyAuth(token=token, workspace=account)
        self.base_url = self.auth.base_url

    def get_schema(self, with_description=False):
        headers = {
            "Authorization": f"Token {self.auth.token}",
            "Content-Type": "application/json",
        }
        data = [
            {
                "command": "fibery.schema/query",
                "args": {"with-description?": with_description}
            }
        ]
        response = requests.post(self.base_url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()
        response.raise_for_status()

    def get_type_by_name(self, type_name):
        schema = self.get_schema()
        if schema and schema[0].get("result"):
            types = schema[0]["result"]["fibery/types"]
            for type_data in types:
                if type_data["fibery/name"] == type_name:
                    return FiberyType(**type_data)
        raise TypeNotFoundError(f"Type '{type_name}' not found in the schema.")


class TypeNotFoundError(Exception):
    pass


class FiberyType(BaseModel):
    fibery_name: str = Field(..., alias="fibery/name")
    fibery_fields: list = Field(..., alias="fibery/fields")
    fibery_meta: dict = Field(..., alias="fibery/meta")
    fibery_id: str = Field(..., alias="fibery/id")
