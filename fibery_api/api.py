# api.py
import requests
from .auth import FiberyAuth
from pydantic import BaseModel, Field
from .utils import configure_logger
from typing import List

logger = configure_logger()


class FiberyFieldIn(BaseModel):
    name: str
    type: str
    meta: dict


class FiberyFieldOut(BaseModel):
    name: str = Field(alias="fibery/name")
    type: str = Field(alias="fibery/type")
    meta: dict = Field(alias="fibery/meta")


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

    def create_database(self, database_name: str, fibery_fields: List[FiberyFieldIn]) -> dict:
        headers = {
            "Authorization": f"Token {self.auth.token}",
            "Content-Type": "application/json",
        }

        # make sure that fields are valid
        for field in fibery_fields:
            FiberyFieldOut(**field.dict(by_alias=False)

        data=[
            {
                "command": "fibery.schema/batch",
                "args": {
                    "commands": [
                        {
                            "command": "schema.type/create",
                            "args": {
                                "fibery/name": database_name,
                                "fibery/meta": {
                                    "fibery/domain?": True,
                                    "fibery/secured?": True,
                                },
                                "fibery/fields": [field.dict(by_alias=True) for field in fibery_fields]
                            }
                        },
                        {
                            "command": "fibery.app/install-mixins",
                            "args": {
                                "types": {
                                    database_name: [
                                        "fibery/rank-mixin"
                                    ]
                                }
                            }
                        }
                    ]
                }
            }
        ]
        response=requests.post(self.base_url, headers=headers, json=data)
        if response.status_code == 200:
            created_db=CreateDatabaseModel(**response.json()[0]["result"])
            return created_db.dict(by_alias=True)
        response.raise_for_status()

    def create_entity(self, entity_type: str, entity_data: dict) -> dict:
        logger.debug("Creating entity")
        headers={
            "Authorization": f"Token {self.auth.token}",
            "Content-Type": "application/json",
        }
        data=[
            {
                "command": "fibery.entity/create",
                "args": {
                    "type": entity_type,
                    "entity": entity_data
                }
            }
        ]
        response=requests.post(self.base_url, headers=headers, json=data)
        if response.status_code == 200:
            created_entity=CreatedEntity(**response.json()[0])
            if created_entity.success:
                logger.debug("Entity created successfully: %s",
                             created_entity.result)
                return created_entity.result
            else:
                logger.error("Failed to create the entity: %s",
                             response.status_code)
                raise EntityCreationError("Failed to create the entity.")
        response.raise_for_status()


class EntityCreationError(Exception):
    pass


class TypeNotFoundError(Exception):
    pass


class FiberyType(BaseModel):
    fibery_name: str=Field(..., alias="fibery/name")
    fibery_fields: list=Field(..., alias="fibery/fields")
    fibery_meta: dict=Field(..., alias="fibery/meta")
    fibery_id: str=Field(..., alias="fibery/id")


class CreatedEntity(BaseModel):
    success: bool
    result: dict


class CreateDatabaseModel(BaseModel):
    fibery_name: str=Field(..., alias="fibery/name")
    fibery_meta: dict=Field(..., alias="fibery/meta")
    fibery_fields: List[FiberyFieldIn]=Field(..., alias="fibery/fields")
