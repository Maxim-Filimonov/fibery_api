import os
import requests


class FiberyAuth:
    def __init__(self, token=None, workspace=None):
        self.token = token or os.getenv("FIBERY_TOKEN")
        self.workspace = workspace or os.getenv("FIBERY_workspace")
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
