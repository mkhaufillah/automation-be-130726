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

    @pytest.fixture
    def binance_rest_client_no_key(self, config: AutomationConfig) -> BinanceRestClient:
        return BinanceRestClient("", config.get_binance_secret_key(), config.get_binance_rest_url())

    @pytest.mark.id("TC-REST-05-01")
    @pytest.mark.testnet
    @pytest.mark.demo
    def test_fetch_account_balance(self, binance_rest_client: BinanceRestClient, test_data_based_id: dict):
        data_assertion = test_data_based_id.get("assertion", {})

        response = binance_rest_client.get_account_balance()
        assert str(response.status_code) in data_assertion.get("status_code")
        data = response.json()
        assert "makerCommission" in data
        assert "balances" in data
        assert isinstance(data["balances"], list)

    @pytest.mark.id("TC-REST-05-02")
    @pytest.mark.testnet
    @pytest.mark.demo
    def test_fetch_account_balance_security_failures(self, binance_rest_client_no_key: BinanceRestClient, test_data_based_id: dict):
        data_assertion = test_data_based_id.get("assertion", {})

        response = binance_rest_client_no_key.get_account_balance()
        assert str(response.status_code) in data_assertion.get("status_code")
        assert response.json()["code"] == -2014
