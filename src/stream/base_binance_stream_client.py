"""
Base class for Binance Stream API client.
"""
import asyncio
import json
import websockets
from src.utils.logger import get_logger

logger = get_logger(__name__)


class StreamConnection:
    """Helper to abstract WebSocket connections for streams."""

    def __init__(self, url: str):
        self.url = url
        self.websocket = None

    async def __aenter__(self):
        self.websocket = await websockets.connect(self.url)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.websocket:
            await self.websocket.close()

    async def recv_json(self, timeout=5.0) -> dict:
        if not self.websocket:
            raise RuntimeError("WebSocket is not connected")
        response_str = await asyncio.wait_for(self.websocket.recv(), timeout=timeout)
        return json.loads(response_str)


class BaseBinanceStreamClient:
    def __init__(self, api_key, secret_key, base_url):
        self.api_key = api_key
        self.secret_key = secret_key
        self.base_url = base_url
