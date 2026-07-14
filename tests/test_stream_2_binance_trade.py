import pytest
import asyncio
import json
import websockets

from src import get_logger, AutomationConfig
from tests.modules.binance_stream_client import BinanceStreamClient

logger = get_logger(__name__)

pytestmark = pytest.mark.asyncio


@pytest.mark.smoke
@pytest.mark.stream
class TestWebSocketStreams:

    @pytest.fixture
    def binance_stream_client(self, config: AutomationConfig) -> BinanceStreamClient:
        return BinanceStreamClient(
            config.get_binance_api_key(),
            config.get_binance_secret_key(),
            config.get_binance_stream_url(),
            config.get_binance_rest_url()
        )

    @pytest.mark.id("TC-STREAM-02-01")
    async def test_subscribe_trade_stream(self, binance_stream_client: BinanceStreamClient, test_data_based_id: dict):
        data_request = test_data_based_id.get("request", {})

        url = binance_stream_client.get_url_trade(
            data_request.get("symbol"))

        async with websockets.connect(url) as websocket:
            # wait up to 30s for a trade
            response = await asyncio.wait_for(websocket.recv(), timeout=30.0)
            data = json.loads(response)

            logger.info(f"data test_subscribe_trade_stream: {data}")

            assert data.get("e") == "trade"
            assert data.get("s") == data_request.get("symbol")

    @pytest.mark.id("TC-STREAM-02-02")
    async def test_trade_event_payload_schema(self, binance_stream_client: BinanceStreamClient, test_data_based_id: dict):
        data_request = test_data_based_id.get("request", {})

        url = binance_stream_client.get_url_trade(
            data_request.get("symbol"))

        # Short delay to prevent connection reset from proxy/rate limits
        await asyncio.sleep(1)
        async with websockets.connect(url) as websocket:
            # wait up to 30s for a trade
            response = await asyncio.wait_for(websocket.recv(), timeout=30.0)
            data = json.loads(response)

            logger.info(f"data test_trade_event_payload_schema: {data}")

            assert data.get("e") == "trade"
            assert "E" in data
            assert data.get("s") == data_request.get("symbol")
            assert "t" in data
            assert "p" in data
            assert "q" in data
            assert "T" in data
            assert "m" in data
            assert "M" in data
