import pytest
import asyncio

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
        async with binance_ws_client:
            # Logon to authenticate session
            logon_id = "logon-TC-WS-01-01"
            data = await binance_ws_client.logon(request_id=logon_id)
            logger.info(
                f"logon test_initialize_user_data_stream_and_unsubscribe: {data}")
            assert data.get("id") == logon_id
            assert data.get("status") == 200

            # Subscribe to user data stream
            sub_id = "sub-TC-WS-01-01"
            data = await binance_ws_client.subscribe_user_data(request_id=sub_id)
            logger.info(
                f"subscribe test_initialize_user_data_stream_and_unsubscribe: {data}")
            assert data.get("id") == sub_id
            assert data.get("status") == 200

            # Unsubscribe to user data stream
            unsub_id = "unsub-TC-WS-01-01"
            data = await binance_ws_client.unsubscribe_user_data(request_id=unsub_id)
            logger.info(
                f"unsubscribe test_initialize_user_data_stream_and_unsubscribe: {data}")
            event = data.get("event")
            assert isinstance(event, dict)
            assert event.get("e") == "eventStreamTerminated"

    @pytest.mark.id("TC-WS-01-02")
    @pytest.mark.testnet
    async def test_order_state_changes(self, binance_ws_client: BinanceWsClient, test_data_based_id: dict):
        data_request = test_data_based_id.get("request", {})

        async with binance_ws_client:
            # Logon to authenticate session
            logon_id = "logon-TC-WS-01-02"
            data = await binance_ws_client.logon(request_id=logon_id)
            logger.info(f"logon test_order_state_changes: {data}")
            assert data.get("id") == logon_id
            assert data.get("status") == 200

            # Subscribe to user data stream
            sub_id = "sub-TC-WS-01-02"
            data = await binance_ws_client.subscribe_user_data(request_id=sub_id)
            logger.info(f"subscribe test_order_state_changes: {data}")
            assert data.get("status") == 200

            # Place order
            order_resp = binance_ws_client.simulate_place_sell_limit_order(
                symbol=data_request.get("symbol")
            )
            order_data = order_resp.json()
            order_id = order_data.get("orderId")

            limit = 0

            # Wait for executionReport (SELL LIMIT)
            while True:
                await asyncio.sleep(1)
                data = await binance_ws_client.recv_json(timeout=5.0)
                logger.info(f"subscribe test_order_state_changes: {data}")
                if limit > 5:
                    break
                if data and isinstance(data.get("event"), dict):
                    event = data["event"]
                    if event.get("e") == "executionReport":
                        assert event.get("e") == "executionReport"
                        assert event.get("s") == data_request.get("symbol")
                        assert event.get("S") == "SELL"
                        assert event.get("o") == "LIMIT"
                        assert event.get("i") == order_id
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
                await asyncio.sleep(1)
                data = await binance_ws_client.recv_json(timeout=5.0)
                logger.info(f"subscribe test_order_state_changes: {data}")
                if limit > 5:
                    break
                if data and isinstance(data.get("event"), dict):
                    event = data["event"]
                    if event.get("e") == "executionReport":
                        assert event.get("e") == "executionReport"
                        assert event.get("s") == data_request.get("symbol")
                        assert event.get("X") == "CANCELED"
                        assert event.get("x") == "CANCELED"
                        assert event.get("i") == order_id
                        limit = 0
                        break
                limit += 1

            if limit > 10:
                pytest.fail("Event not listened")

            # Unsubscribe to user data stream
            unsub_id = "unsub-TC-WS-01-02"
            await binance_ws_client.unsubscribe_user_data(request_id=unsub_id)

    @pytest.mark.id("TC-WS-01-03")
    @pytest.mark.testnet
    async def test_account_balance_change(self, binance_ws_client: BinanceWsClient, test_data_based_id: dict):
        data_request = test_data_based_id.get("request", {})

        async with binance_ws_client:
            # Logon to authenticate session
            logon_id = "logon-TC-WS-01-03"
            data = await binance_ws_client.logon(request_id=logon_id)
            logger.info(f"logon test_account_balance_change: {data}")
            assert data.get("id") == logon_id
            assert data.get("status") == 200

            # Subscribe to user data stream
            sub_id = "sub-TC-WS-01-03"
            data = await binance_ws_client.subscribe_user_data(request_id=sub_id)
            assert data.get("status") == 200

            # Place order
            order_resp = binance_ws_client.simulate_place_sell_limit_order(
                symbol=data_request.get("symbol"),
            )
            order_data = order_resp.json()
            order_id = order_data.get("orderId")

            limit = 0

            # Wait for outboundAccountPosition
            while True:
                await asyncio.sleep(1)
                data = await binance_ws_client.recv_json(timeout=5.0)
                logger.info(f"subscribe test_account_balance_change: {data}")
                if limit > 5:
                    break
                if data and isinstance(data.get("event"), dict):
                    event = data["event"]
                    if event.get("e") == "outboundAccountPosition":
                        assert event.get("e") == "outboundAccountPosition"
                        assert "E" in event
                        assert "u" in event
                        assert "B" in event
                        for v in event.get("B", []):
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
            unsub_id = "unsub-TC-WS-01-03"
            await binance_ws_client.unsubscribe_user_data(request_id=unsub_id)
