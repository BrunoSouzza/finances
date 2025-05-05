import requests
import pandas as pd

class SupabaseClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url        
        self.headers = {
            "apikey": api_key,
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }

    def get(self, resource: str, params: dict = None) -> pd.DataFrame:
        url = f"{self.base_url}/{resource}"
        response = requests.get(url, headers=self.headers, params=params)
        if response.status_code == 200:
            return pd.DataFrame(response.json())
        return pd.DataFrame()

    def post(self, resource: str, payload: dict):
        url = f"{self.base_url}/{resource}"
        return requests.post(url, headers=self.headers, json=payload)
    
    def patch(self, resource: str, id: str, data: dict):
        url = f"{self.base_url}/{resource}?id=eq.{id}"
        return requests.patch(url, headers=self.headers, json=data)
