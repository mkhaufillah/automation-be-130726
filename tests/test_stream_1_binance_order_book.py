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

    @pytest.mark.id("TC-STREAM-01-01")
    async def test_subscribe_order_book_stream(self, binance_stream_client: BinanceStreamClient, test_data_based_id: dict):
        data_request = test_data_based_id.get("request", {})

        url = binance_stream_client.get_url_orderbook(
            data_request.get("symbol"))

        async with websockets.connect(url) as websocket:
            # Wait for 1 message
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            data = json.loads(response)

            logger.info(f"data test_subscribe_order_book_stream: {data}")

            assert data.get("e") == "depthUpdate"
            assert data.get("s") == data_request.get("symbol")
            assert "E" in data
            assert "U" in data
            assert "u" in data
            assert "b" in data
            assert "a" in data
            assert isinstance(data.get("b"), list)
            assert isinstance(data.get("a"), list)

    @pytest.mark.id("TC-STREAM-01-02")
    async def test_order_book_stream_continuity(self, binance_stream_client: BinanceStreamClient, test_data_based_id: dict):
        data_request = test_data_based_id.get("request", {})

        url = binance_stream_client.get_url_orderbook(
            data_request.get("symbol"))

        messages = []
        async with websockets.connect(url) as websocket:
            for _ in range(3):
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                messages.append(json.loads(response))

        assert len(messages) == 3

        logger.info(f"messages test_order_book_stream_continuity: {messages}")

        # ensure message interval are below 1500 ms
        for i in range(1, len(messages)):
            prev_u = messages[i-1].get("E")
            curr_U = messages[i].get("E")
            assert prev_u - curr_U <= 1500
