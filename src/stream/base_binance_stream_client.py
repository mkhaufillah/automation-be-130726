"""
Base class for Binance Stream API client.
"""

from src.utils.logger import get_logger

logger = get_logger(__name__)


class BaseBinanceStreamClient:
    def __init__(self, api_key, secret_key, base_url):
        self.api_key = api_key
        self.secret_key = secret_key
        self.base_url = base_url
