# api.py
import requests
from pydantic import BaseModel, Field
from marshmallow import Schema, ValidationError, fields
from fibery_api.constants import DOMAIN_TYPE_FIELDS
from fibery_api.mashmallow_ext import UnionField
from .auth import FiberyAuth
from .utils import configure_logger
from typing import List


logger = configure_logger()


class FiberyField(BaseModel):
    name: str
    type: str
    meta: dict


class FiberyFieldSchema(Schema):
    name = fields.String(data_key="fibery/name")
    type = fields.String(data_key="fibery/type")
    meta = fields.Dict(data_key="fibery/meta")


class CreateDatabaseModel(BaseModel):
    success: bool
    result: dict | str


class CreateDatabaseSchema(Schema):
    success = fields.Boolean()
    # this type can be dict or string
    # when it's dict, it's failed to create database
    # when it's string, it means it worked
    result = UnionField(types=[dict, str])


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

    def create_database(self, database_name: str, fibery_fields: List[FiberyField]) -> CreateDatabaseModel:
        headers = {
            "Authorization": f"Token {self.auth.token}",
            "Content-Type": "application/json",
        }
        fibery_fields = add_missing_domain_fields(fibery_fields)

        # convert fields to FiberyFieldSchema
        fibery_fields_serialized = [FiberyFieldSchema().dump(field)
                                    for field in fibery_fields]

        data = [
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
                                "fibery/fields": fibery_fields_serialized
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
        response = requests.post(self.base_url, headers=headers, json=data)
        if response.status_code == 200:
            result = response.json()[0]
            created_db = CreateDatabaseSchema().load(result)
            return CreateDatabaseModel(**created_db)
        response.raise_for_status()

    def create_entity(self, entity_type: str, entity_data: dict) -> dict:
        logger.debug("Creating entity")
        headers = {
            "Authorization": f"Token {self.auth.token}",
            "Content-Type": "application/json",
        }
        data = [
            {
                "command": "fibery.entity/create",
                "args": {
                    "type": entity_type,
                    "entity": entity_data
                }
            }
        ]
        response = requests.post(self.base_url, headers=headers, json=data)
        if response.status_code == 200:
            created_entity = CreatedEntity(**response.json()[0])
            if created_entity.success:
                logger.debug("Entity created successfully: %s",
                             created_entity.result)
                return created_entity.result
            else:
                logger.error("Failed to create the entity: %s",
                             response.status_code)
                raise EntityCreationError("Failed to create the entity.")
        response.raise_for_status()


def add_missing_domain_fields(fields: List[FiberyField]) -> List[FiberyField]:
    field_names = [field.name for field in fields]
    missing_domain_fields = []
    for field in DOMAIN_TYPE_FIELDS:
        schema = FiberyFieldSchema().load(field)
        fibery_model = FiberyField(**schema)
        if fibery_model.name not in field_names:
            missing_domain_fields.append(fibery_model)
    fields.extend(missing_domain_fields)
    return fields


class EntityCreationError(Exception):
    pass


class TypeNotFoundError(Exception):
    pass


class FiberyType(BaseModel):
    fibery_name: str = Field(..., alias="fibery/name")
    fibery_fields: list = Field(..., alias="fibery/fields")
    fibery_meta: dict = Field(..., alias="fibery/meta")
    fibery_id: str = Field(..., alias="fibery/id")


class CreatedEntity(BaseModel):
    success: bool
    result: dict | str
