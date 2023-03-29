# auth.py
import os
import requests
from pydantic import BaseModel, Field


class FiberyAuth(BaseModel):
    token: str = Field(..., env="FIBERY_TOKEN")
    workspace: str = Field(..., env="FIBERY_WORKSPACE")
    base_url: str = None

    def __init__(self, **data):
        super().__init__(**data)
        self.base_url = f"https://{self.workspace}.fibery.io/api/commands"

    def authenticate(self):
        headers = {
            "Authorization": f"Token {self.token}",
            "Content-Type": "application/json",
        }
        response = requests.post(self.base_url, headers=headers)
        if response.status_code == 200:
            return True
        return False
