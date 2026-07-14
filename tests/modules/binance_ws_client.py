"""
Module class for Binance WS API client.
"""

from requests import Response

from src import get_logger, BaseBinanceWsClient
from tests.modules.binance_rest_client import BinanceRestClient

logger = get_logger(__name__)


class BinanceWsClient(BaseBinanceWsClient):
    def __init__(self, api_key: str, secret_key: str, ws_api_url: str, api_key_hmac: str, secret_key_hmac: str, rest_api_url: str):
        super().__init__(api_key, secret_key, ws_api_url)
        self.binance_rest_client = BinanceRestClient(
            api_key_hmac, secret_key_hmac, rest_api_url)
        path = "/ws-api/v3"
        if not self.base_url.endswith(path):
            self.path = path
        else:
            self.path = ""

    def get_ws_url(self) -> str:
        """Returns the fully constructed WebSocket URL for WS API."""
        url = f"{self.base_url}{self.path}"
        logger.info(f"Built WS API URL: {url}")
        return url

    def get_logon_payload(self, request_id: str = "") -> str:
        """Returns the JSON string payload to authenticate the session."""
        return self.build_payload(method="session.logon", signed=True, request_id=request_id)

    def get_subscribe_user_data_payload(self, request_id: str = "") -> str:
        """Returns the JSON string payload to subscribe to user data streams."""
        # After a successful session.logon, the socket is authenticated.
        return self.build_payload(method="userDataStream.subscribe", signed=False, request_id=request_id)

    def get_unsubscribe_user_data_payload(self, request_id: str = "") -> str:
        """Returns the JSON string payload to unsubscribe to user data streams."""
        # After a successful session.logon, the socket is authenticated.
        return self.build_payload(method="userDataStream.unsubscribe", signed=False, request_id=request_id)

    def simulate_place_sell_limit_order(self, symbol: str) -> Response:
        response = self.binance_rest_client.place_order(
            symbol=symbol,
            side="SELL",
            type="LIMIT",
            timeInForce="GTC",
            quantity=0.001,
            price=self.binance_rest_client.generate_target_price(
                symbol, "SELL")
        )

        return response

    def simulate_cancel_order(self, symbol: str, order_id: str) -> Response:
        return self.binance_rest_client.cancel_order(symbol, order_id)

    async def logon(self, request_id: str = "") -> dict:
        payload = self.get_logon_payload(request_id)
        await self.send_payload(payload)
        return await self.recv_json()

    async def subscribe_user_data(self, request_id: str = "") -> dict:
        payload = self.get_subscribe_user_data_payload(request_id)
        await self.send_payload(payload)
        return await self.recv_json()

    async def unsubscribe_user_data(self, request_id: str = "") -> dict:
        payload = self.get_unsubscribe_user_data_payload(request_id)
        await self.send_payload(payload)
        return await self.recv_json()
