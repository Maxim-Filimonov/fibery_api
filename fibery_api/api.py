import requests
from .auth import FiberyAuth

class FiberyAPI:
    def __init__(self, token=None, account=None):
        self.auth = FiberyAuth(token, account)
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
