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

    @pytest.mark.id("TC-REST-04-01")
    @pytest.mark.testnet
    @pytest.mark.demo
    def test_fetch_trade_history_valid(self, binance_rest_client: BinanceRestClient, test_data_based_id: dict):
        data_request = test_data_based_id.get("request", {})
        data_assertion = test_data_based_id.get("assertion", {})

        response = binance_rest_client.get_my_trades(
            symbol=data_request.get("symbol"))
        assert str(response.status_code) in data_assertion.get("status_code")
        assert isinstance(response.json(), list)

    @pytest.mark.id("TC-REST-04-02")
    @pytest.mark.testnet
    @pytest.mark.demo
    def test_fetch_trade_history_pagination(self, binance_rest_client: BinanceRestClient, test_data_based_id: dict):
        data_request = test_data_based_id.get("request", {})
        data_assertion = test_data_based_id.get("assertion", {})

        response = binance_rest_client.get_my_trades(
            symbol=data_request.get("symbol"), limit=2)
        assert str(response.status_code) in data_assertion.get("status_code")
        trades = response.json()
        assert len(trades) <= 2

        if len(trades) > 0:
            last_id = trades[-1]["id"]
            response_next = binance_rest_client.get_my_trades(
                symbol=data_request.get("symbol"), fromId=last_id + 1, limit=5)
            assert response_next.status_code == 200

    @pytest.mark.id("TC-REST-04-03")
    @pytest.mark.testnet
    @pytest.mark.demo
    def test_fetch_trade_history_missing_symbol(self, binance_rest_client: BinanceRestClient, test_data_based_id: dict):
        data_assertion = test_data_based_id.get("assertion", {})

        response = binance_rest_client.get_my_trades()
        assert str(response.status_code) in data_assertion.get("status_code")
        assert response.json()["code"] == -1102
