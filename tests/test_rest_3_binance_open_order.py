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

    @pytest.mark.id("TC-REST-03-01")
    @pytest.mark.testnet
    @pytest.mark.demo
    def test_fetch_open_orders_specific_symbol(self, binance_rest_client: BinanceRestClient, test_data_based_id: dict):
        data_request = test_data_based_id.get("request", {})
        data_assertion = test_data_based_id.get("assertion", {})

        response = binance_rest_client.get_open_orders(
            symbol=data_request.get("symbol"))
        assert str(response.status_code) in data_assertion.get("status_code")
        assert isinstance(response.json(), list)

    @pytest.mark.id("TC-REST-03-02")
    @pytest.mark.testnet
    @pytest.mark.demo
    def test_fetch_open_orders_all_symbols(self, binance_rest_client: BinanceRestClient, test_data_based_id: dict):
        data_assertion = test_data_based_id.get("assertion", {})

        response = binance_rest_client.get_open_orders()
        assert str(response.status_code) in data_assertion.get("status_code")
        assert isinstance(response.json(), list)

    @pytest.mark.id("TC-REST-03-03")
    @pytest.mark.testnet
    @pytest.mark.demo
    def test_fetch_open_orders_invalid_params(self, binance_rest_client: BinanceRestClient, test_data_based_id: dict):
        data_request = test_data_based_id.get("request", {})
        data_assertion = test_data_based_id.get("assertion", {})

        if not binance_rest_client.api_key:
            pytest.skip("No API key configured")
        response = binance_rest_client.get_open_orders(
            symbol=data_request.get("symbol"))
        assert str(response.status_code) in data_assertion.get("status_code")
        assert response.json()["code"] == -1121
