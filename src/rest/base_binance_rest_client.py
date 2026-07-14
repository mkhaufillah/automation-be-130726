"""
Base class for Binance REST API client.
"""

import hmac
import hashlib
import time
import requests
from urllib.parse import urlencode

from src.utils.logger import get_logger

logger = get_logger(__name__)


class BaseBinanceRestClient:
    def __init__(self, api_key, secret_key, base_url):
        self.api_key = api_key
        self.secret_key = secret_key
        self.base_url = base_url
        self.session = requests.Session()
        if self.api_key:
            self.session.headers.update({
                "X-MBX-APIKEY": self.api_key
            })

    def _generate_signature(self, query_string: str) -> str:
        return hmac.new(
            self.secret_key.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

    def _get_timestamp(self):
        return int(time.time() * 1000)

    def request(self, method, endpoint, params=None, signed=False):
        if params is None:
            params = {}

        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}

        if signed:
            params["timestamp"] = self._get_timestamp()
            query_string = urlencode(params)
            signature = self._generate_signature(query_string)
            params["signature"] = signature

        url = f"{self.base_url}{endpoint}"

        logger.info(f"Request: {method} {url} {params}")
        response = self.session.request(method, url, params=params)
        logger.info(f"Response: {response.status_code} {response.text}")
        return response
