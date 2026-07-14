import pytest

from src import AutomationConfig
from tests.modules.binance_rest_client import BinanceRestClient

from src import get_logger

logger = get_logger(__name__)


@pytest.mark.smoke
@pytest.mark.rest
class TestRestAPI:

    @pytest.fixture
    def binance_rest_client(self, config: AutomationConfig) -> BinanceRestClient:
        return BinanceRestClient(config.get_binance_api_key(), config.get_binance_secret_key(), config.get_binance_rest_url())

    @pytest.mark.id("TC-REST-02-01")
    @pytest.mark.testnet
    def test_place_limit_buy_order_success(self, binance_rest_client: BinanceRestClient, test_data_based_id: dict):
        data_request = test_data_based_id.get("request", {})
        data_assertion = test_data_based_id.get("assertion", {})

        symbol = data_request.get("symbol")

        response = binance_rest_client.place_order(
            symbol=symbol,
            side="BUY",
            type="LIMIT",
            timeInForce="GTC",
            quantity=0.001,
            price=binance_rest_client.generate_target_price(symbol, "BUY")
        )
        assert str(response.status_code) in data_assertion.get("status_code")
        data = response.json()
        assert data["symbol"] == symbol
        assert data["status"] == "NEW"

        # Cleanup
        response = binance_rest_client.cancel_order(symbol, data["orderId"])
        assert response.status_code == 200

    @pytest.mark.id("TC-REST-02-02")
    @pytest.mark.testnet
    def test_place_limit_sell_order_success(self, binance_rest_client: BinanceRestClient, test_data_based_id: dict):
        data_request = test_data_based_id.get("request", {})
        data_assertion = test_data_based_id.get("assertion", {})

        symbol = data_request.get("symbol")

        response = binance_rest_client.place_order(
            symbol=symbol,
            side="SELL",
            type="LIMIT",
            timeInForce="GTC",
            quantity=0.001,
            price=binance_rest_client.generate_target_price(symbol, "SELL")
        )
        assert str(response.status_code) in data_assertion.get("status_code")
        data = response.json()
        assert data["status"] == "NEW"

        # Cleanup
        response = binance_rest_client.cancel_order(symbol, data["orderId"])
        assert response.status_code == 200

    @pytest.mark.id("TC-REST-02-03")
    @pytest.mark.testnet
    @pytest.mark.demo
    def test_place_order_auth_failures(self, binance_rest_client: BinanceRestClient, test_data_based_id: dict):
        data_request = test_data_based_id.get("request", {})
        data_assertion = test_data_based_id.get("assertion", {})

        symbol = data_request.get("symbol")

        if not binance_rest_client.api_key:
            pytest.skip("No API key configured")
        # We can simulate incorrect signature by replacing the secret_key
        original_secret = binance_rest_client.secret_key
        binance_rest_client.secret_key = "invalid_secret"

        response = binance_rest_client.place_order(
            symbol=symbol,
            side="BUY",
            type="LIMIT",
            timeInForce="GTC",
            quantity=0.001,
            price=binance_rest_client.generate_target_price(symbol, "BUY")
        )
        assert str(response.status_code) in data_assertion.get("status_code")
        assert response.json()["code"] == -1022

        # Restore secret
        binance_rest_client.secret_key = original_secret

    @pytest.mark.id("TC-REST-02-04")
    @pytest.mark.testnet
    @pytest.mark.demo
    def test_place_order_filter_violations(self, binance_rest_client: BinanceRestClient, test_data_based_id: dict):
        data_request = test_data_based_id.get("request", {})
        data_assertion = test_data_based_id.get("assertion", {})

        symbol = data_request.get("symbol")

        if not binance_rest_client.api_key:
            pytest.skip("No API key configured")
        # Insufficient Balance (or price filter violation)
        response = binance_rest_client.place_order(
            symbol=symbol,
            side="BUY",
            type="LIMIT",
            timeInForce="GTC",
            quantity=10,  # Very high quantity
            price=binance_rest_client.generate_target_price(symbol, "BUY")
        )
        assert str(response.status_code) in data_assertion.get("status_code")
        # Either insufficient balance (-2010) or filter failure (-1013)
        assert response.json()["code"] in [-2010, -1013]
        assert str(response.status_code) in data_assertion.get("status_code")
