"""
Module class for Binance Stream API client.
"""

from src import get_logger, BaseBinanceStreamClient

logger = get_logger(__name__)


class BinanceStreamClient(BaseBinanceStreamClient):
    def __init__(self, api_key, secret_key, stream_url, rest_url):
        super().__init__(api_key, secret_key, stream_url)
        self.rest_url = rest_url
        path = "/ws"
        if not self.base_url.endswith(path):
            self.path = path
        else:
            self.path = ""

    def get_url_orderbook(self, symbol: str) -> str:
        symbol_lower = symbol.lower().replace("_", "")
        url = f"{self.base_url}{self.path}/{symbol_lower}@depth"
        logger.info(f"url get_url_orderbook {url}")
        return url

    def get_url_trade(self, symbol: str) -> str:
        symbol_lower = symbol.lower().replace("_", "")
        url = f"{self.base_url}{self.path}/{symbol_lower}@trade"
        logger.info(f"url get_url_trade {url}")
        return url
