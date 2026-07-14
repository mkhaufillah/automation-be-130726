import pytest

from src import AutomationConfig, validate_schema
from tests.modules.binance_rest_client import BinanceRestClient

from src import get_logger

logger = get_logger(__name__)


@pytest.mark.smoke
@pytest.mark.rest
class TestRestAPI:

    @pytest.fixture
    def binance_rest_client(self, config: AutomationConfig) -> BinanceRestClient:
        return BinanceRestClient(config.get_binance_api_key(), config.get_binance_secret_key, config.get_binance_rest_url())

    @pytest.mark.id("TC-REST-01-01")
    def test_fetch_order_book_valid(self, binance_rest_client: BinanceRestClient, test_data_based_id: dict):
        data_request = test_data_based_id.get("request", {})
        data_assertion = test_data_based_id.get("assertion", {})

        response = binance_rest_client.get_order_book(
            symbol=data_request.get("symbol"))

        st = data_assertion.get("status_code")
        logger.info(f"debug st -> {st}")

        assert str(response.status_code) in data_assertion.get("status_code")

        # Check weight used header
        weight = response.headers.get("x-mbx-used-weight-1m")
        assert weight is not None

        data = response.json()

        # validate against schema
        schema = data_assertion.get("schema")
        result = validate_schema(data, schema)
        if result != "":
            pytest.fail(reason=result)

        assert "bids" in data
        assert "asks" in data
        assert len(data["bids"]) <= 100  # default limit is 100
        assert len(data["asks"]) <= 100

        if len(data["bids"]) > 0:
            assert isinstance(data["bids"][0][0], str)
            assert isinstance(data["bids"][0][1], str)

    @pytest.mark.id("TC-REST-01-02")
    def test_fetch_order_book_custom_limits(self, binance_rest_client: BinanceRestClient, test_data_based_id: dict):
        data_request = test_data_based_id.get("request", {})
        data_assertion = test_data_based_id.get("assertion", {})

        limits = [5, 5000]

        for limit in limits:
            response = binance_rest_client.get_order_book(
                symbol=data_request.get("symbol"), limit=limit)
            assert str(response.status_code) in data_assertion.get(
                "status_code")
            assert len(response.json()["bids"]) <= limit

    @pytest.mark.id("TC-REST-01-03")
    def test_fetch_order_book_negative(self, binance_rest_client: BinanceRestClient, test_data_based_id: dict):
        data_request = test_data_based_id.get("request", {})
        data_assertion = test_data_based_id.get("assertion", {})

        # Invalid symbol
        response = binance_rest_client.get_order_book(
            symbol=data_request.get("symbol"))
        assert str(response.status_code) in data_assertion.get("status_code")
        assert response.json()["code"] == -1121

        # Missing symbol
        response = binance_rest_client.get_order_book()
        assert str(response.status_code) in data_assertion.get("status_code")
        assert response.json()["code"] == -1102
