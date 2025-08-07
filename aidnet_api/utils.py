import requests
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from time import sleep
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self, calls_per_second=1):
        self.calls_per_second = calls_per_second
        self.last_call = datetime.now()

    def wait(self):
        now = datetime.now()
        time_since_last_call = (now - self.last_call).total_seconds()
        if time_since_last_call < 1.0 / self.calls_per_second:
            sleep(1.0 / self.calls_per_second - time_since_last_call)
        self.last_call = datetime.now()

class ACLEDClient:
    def __init__(self, email: str, api_key: str):
        self.base_url = "https://api.acleddata.com/acled/read"
        self.email = email
        self.api_key = api_key
        self.rate_limiter = RateLimiter(calls_per_second=1)

    def fetch_conflict_data(self, start_date: str, end_date: str, countries: List[str] = None) -> pd.DataFrame:
        try:
            self.rate_limiter.wait()
            params = {
                "email": self.email,
                "key": self.api_key,
                "start_date": start_date,
                "end_date": end_date,
                "format": "json"
            }
            if countries:
                params["countries"] = ",".join(countries)

            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            return pd.DataFrame(data["data"])
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching ACLED data: {e}")
            return pd.DataFrame()

class ReliefWebClient:
    def __init__(self, app_name: str):
        self.base_url = "https://api.reliefweb.int/v1"
        self.app_name = app_name
        self.rate_limiter = RateLimiter(calls_per_second=1)

    def fetch_reports(self, country: str, limit: int = 10) -> List[Dict]:
        try:
            self.rate_limiter.wait()
            url = f"{self.base_url}/reports"
            params = {
                "appname": self.app_name,
                "filter": {
                    "operator": "AND",
                    "conditions": [
                        {"field": "country", "value": country},
                        {"field": "status", "value": "published"}
                    ]
                },
                "limit": limit
            }
            response = requests.post(url, json=params)
            response.raise_for_status()
            return response.json()["data"]
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching ReliefWeb data: {e}")
            return []

def fetch_acled_data(email: str, api_key: str, start_date: str, end_date: str, countries: Optional[List[str]] = None) -> pd.DataFrame:
    """Fetch conflict data from ACLED API."""
    client = ACLEDClient(email, api_key)
    return client.fetch_conflict_data(start_date, end_date, countries)

def fetch_reliefweb_data(country: str, limit: int = 10) -> List[Dict]:
    """Fetch humanitarian reports from ReliefWeb API."""
    client = ReliefWebClient("aidnet_api")
    return client.fetch_reports(country, limit)

def fetch_unicef_data():
    """Placeholder for UNICEF data integration."""
    logger.info("UNICEF data integration not yet implemented")
    return None

def fetch_osm_data():
    """Placeholder for OpenStreetMap data integration."""
    logger.info("OpenStreetMap data integration not yet implemented")
    return None