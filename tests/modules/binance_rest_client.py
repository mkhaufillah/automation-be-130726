"""
Module class for Binance REST API client.
"""

import time

from src import get_logger, BaseBinanceRestClient

logger = get_logger(__name__)


class BinanceRestClient(BaseBinanceRestClient):
    def __init__(self, api_key, secret_key, base_url):
        super().__init__(api_key, secret_key, base_url)

    def get_order_book(self, symbol=None, limit=None):
        params = {}
        if symbol:
            params["symbol"] = symbol
        if limit:
            params["limit"] = limit
        return self.request("GET", "/api/v3/depth", params=params)

    def get_ticker_price(self, symbol):
        params = {"symbol": symbol}
        return self.request("GET", "/api/v3/ticker/price", params=params, signed=False)

    def place_order(self, symbol, side, type, quantity, price=None, timeInForce=None):
        params = {
            "symbol": symbol,
            "side": side,
            "type": type,
            "quantity": quantity
        }
        if price:
            params["price"] = price
        if timeInForce:
            params["timeInForce"] = timeInForce

        return self.request("POST", "/api/v3/order", params=params, signed=True)

    def cancel_order(self, symbol, orderId):
        params = {
            "symbol": symbol,
            "orderId": orderId
        }
        return self.request("DELETE", "/api/v3/order", params=params, signed=True)

    def get_open_orders(self, symbol=None):
        params = {}
        if symbol:
            params["symbol"] = symbol
        return self.request("GET", "/api/v3/openOrders", params=params, signed=True)

    def get_my_trades(self, symbol=None, limit=None, fromId=None):
        params = {}
        if symbol:
            params["symbol"] = symbol
        if limit:
            params["limit"] = limit
        if fromId:
            params["fromId"] = fromId
        return self.request("GET", "/api/v3/myTrades", params=params, signed=True)

    def get_account_balance(self):
        return self.request("GET", "/api/v3/account", signed=True)

    def generate_target_price(self, symbol: str, side: str = "BUY") -> float:
        # Get current ticker price to calculate a valid limit price
        price_resp = self.get_ticker_price(symbol)
        assert price_resp.status_code == 200, f"Failed to get ticker price: {price_resp.text}"
        current_price = float(price_resp.json()["price"])

        if side.upper() == "BUY":
            # Place limit buy 5% below current price
            return round(current_price * 0.95, 2)
        else:
            # Place limit sell 5% above current price
            return round(current_price * 1.05, 2)
