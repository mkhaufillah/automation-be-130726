import time
import pytest
import asyncio
import json
import websockets

from src import get_logger, AutomationConfig
from tests.modules.binance_stream_client import BinanceStreamClient
from tests.modules.binance_ws_client import BinanceWsClient

logger = get_logger(__name__)

pytestmark = pytest.mark.asyncio


@pytest.mark.smoke
@pytest.mark.stream
@pytest.mark.testnet
class TestWebSocket:

    @pytest.fixture
    def binance_ws_client(self, config: AutomationConfig) -> BinanceWsClient:
        return BinanceWsClient(
            config.get_ed25519_binance_api_key(),
            config.get_ed25519_binance_secret_key(),
            config.get_binance_ws_url(),
            config.get_binance_api_key(),
            config.get_binance_secret_key(),
            config.get_binance_rest_url()
        )

    @pytest.mark.id("TC-WS-01-01")
    async def test_initialize_user_data_stream_and_unsubscribe(self, binance_ws_client: BinanceWsClient):
        url = binance_ws_client.get_ws_url()

        async with websockets.connect(url) as websocket:
            # Logon to authenticate session
            logon_id = "logon-TC-WS-01-01"
            logon_payload = binance_ws_client.get_logon_payload(
                request_id=logon_id)
            await websocket.send(logon_payload)

            # Wait for logon response
            response_str = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            data = json.loads(response_str)
            logger.info(
                f"logon test_initialize_user_data_stream_and_unsubscribe: {data}")
            assert data.get("id") == logon_id
            assert data.get("status") == 200

            # Subscribe to user data stream
            sub_id = "sub-TC-WS-01-01"
            subscribe_payload = binance_ws_client.get_subscribe_user_data_payload(
                request_id=sub_id)
            await websocket.send(subscribe_payload)

            # Wait for subscribe response
            response_str = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            data = json.loads(response_str)
            logger.info(
                f"subscribe test_initialize_user_data_stream_and_unsubscribe: {data}")
            assert data.get("id") == sub_id
            assert data.get("status") == 200

            # Unsubscribe to user data stream
            unsub_id = "unsub-TC-WS-01-01"
            unsubscribe_payload = binance_ws_client.get_unsubscribe_user_data_payload(
                request_id=unsub_id)
            await websocket.send(unsubscribe_payload)

            # Wait for unsubscribe response
            response_str = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            data = json.loads(response_str)
            logger.info(
                f"unsubscribe test_initialize_user_data_stream_and_unsubscribe: {data}")
            assert data.get("event") != None
            assert data.get("event").get("e") == "eventStreamTerminated"

    @pytest.mark.id("TC-WS-01-02")
    @pytest.mark.testnet
    async def test_order_state_changes(self, binance_ws_client: BinanceWsClient, test_data_based_id: dict):
        data_request = test_data_based_id.get("request", {})

        url = binance_ws_client.get_ws_url()

        async with websockets.connect(url) as websocket:
            # Logon to authenticate session
            logon_id = "logon-TC-WS-01-02"
            logon_payload = binance_ws_client.get_logon_payload(
                request_id=logon_id)
            await websocket.send(logon_payload)

            # Wait for logon response
            response_str = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            data = json.loads(response_str)
            logger.info(f"logon test_order_state_changes: {data}")
            assert data.get("id") == logon_id
            assert data.get("status") == 200

            # Subscribe to user data stream
            sub_id = "sub-TC-WS-01-02"
            subscribe_payload = binance_ws_client.get_subscribe_user_data_payload(
                request_id=sub_id)
            await websocket.send(subscribe_payload)

            # Place order
            order_resp = binance_ws_client.simulate_place_sell_limit_order(
                symbol=data_request.get("symbol")
            )
            order_data = order_resp.json()
            order_id = order_data.get("orderId")

            limit = 0

            # Wait for executionReport (SELL LIMIT)
            while True:
                time.sleep(1)
                response_str = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(response_str)
                logger.info(f"subscribe test_order_state_changes: {data}")
                if limit > 5:
                    break
                if (data != None and data.get("event") != None and data.get("event").get("e") == "executionReport"):
                    assert data.get("event").get("e") == "executionReport"
                    assert data.get("event").get(
                        "s") == data_request.get("symbol")
                    assert data.get("event").get("S") == "SELL"
                    assert data.get("event").get("o") == "LIMIT"
                    assert data.get("event").get("i") == order_id
                    limit = 0
                    break
                limit += 1

            if limit > 10:
                pytest.fail("Event not listened")

            # Cancel order
            binance_ws_client.simulate_cancel_order(
                data_request.get("symbol"), order_id)

            # Wait for executionReport (CANCELED)
            while True:
                time.sleep(1)
                response_str = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(response_str)
                logger.info(f"subscribe test_order_state_changes: {data}")
                if limit > 5:
                    break
                if (data != None and data.get("event") != None and data.get("event").get("e") == "executionReport"):
                    assert data.get("event").get("e") == "executionReport"
                    assert data.get("event").get(
                        "s") == data_request.get("symbol")
                    assert data.get("event").get("X") == "CANCELED"
                    assert data.get("event").get("x") == "CANCELED"
                    assert data.get("event").get("i") == order_id
                    limit = 0
                    break
                limit += 1

            if limit > 10:
                pytest.fail("Event not listened")

            # Unsubscribe to user data stream
            unsub_id = "unsub-TC-WS-01-02"
            unsubscribe_payload = binance_ws_client.get_unsubscribe_user_data_payload(
                request_id=unsub_id)
            await websocket.send(unsubscribe_payload)

    @pytest.mark.id("TC-WS-01-03")
    @pytest.mark.testnet
    async def test_account_balance_change(self, binance_ws_client: BinanceWsClient, test_data_based_id: dict):
        data_request = test_data_based_id.get("request", {})

        url = binance_ws_client.get_ws_url()

        async with websockets.connect(url) as websocket:
            # Logon to authenticate session
            logon_id = "logon-TC-WS-01-03"
            logon_payload = binance_ws_client.get_logon_payload(
                request_id=logon_id)
            await websocket.send(logon_payload)

            # Wait for logon response
            response_str = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            data = json.loads(response_str)
            logger.info(f"logon test_account_balance_change: {data}")
            assert data.get("id") == logon_id
            assert data.get("status") == 200

            # Subscribe to user data stream
            sub_id = "sub-TC-WS-01-03"
            subscribe_payload = binance_ws_client.get_subscribe_user_data_payload(
                request_id=sub_id)
            await websocket.send(subscribe_payload)

            # Place order
            order_resp = binance_ws_client.simulate_place_sell_limit_order(
                symbol=data_request.get("symbol"),
            )
            order_data = order_resp.json()
            order_id = order_data.get("orderId")

            limit = 0

            # Wait for outboundAccountPosition
            while True:
                time.sleep(1)
                response_str = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(response_str)
                logger.info(f"subscribe test_account_balance_change: {data}")
                if limit > 5:
                    break
                if (data != None and data.get("event") != None and data.get("event").get("e") == "outboundAccountPosition"):
                    assert data.get("event").get(
                        "e") == "outboundAccountPosition"
                    assert "E" in data.get("event")
                    assert "u" in data.get("event")
                    assert "B" in data.get("event")
                    for v in data.get("event").get("B"):
                        assert "a" in v
                        assert "f" in v
                        assert "l" in v
                    limit = 0
                    break
                limit += 1

            if limit > 10:
                pytest.fail("Event not listened")

            # Cancel order
            binance_ws_client.simulate_cancel_order(
                data_request.get("symbol"), order_id)

            # Unsubscribe to user data stream
            unsub_id = "unsub-TC-WS-01-02"
            unsubscribe_payload = binance_ws_client.get_unsubscribe_user_data_payload(
                request_id=unsub_id)
            await websocket.send(unsubscribe_payload)
