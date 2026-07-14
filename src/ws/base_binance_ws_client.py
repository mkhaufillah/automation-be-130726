"""
Base class for Binance WS API client.
"""

import asyncio
import json
import websockets
import hmac
import hashlib
import time
import json
import base64
from urllib.parse import urlencode
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import ed25519, rsa, padding

from src.utils.logger import get_logger

logger = get_logger(__name__)


class BaseBinanceWsClient:
    def __init__(self, api_key: str, secret_key: str, base_url: str):
        self.api_key = api_key
        self.secret_key = secret_key
        self.base_url = base_url

    def _generate_signature(self, params: dict) -> str:
        """Generate Ed25519, RSA, or HMAC SHA256 signature for Binance API."""
        sorted_params = dict(sorted(params.items()))
        query_string = urlencode(sorted_params)
        payload = query_string.encode("utf-8")

        # Binance Private keys usually come in PEM format
        secret = self.secret_key.replace('\\n', '\n')
        if "BEGIN PRIVATE" in secret or "BEGIN EC PRIVATE" in secret or "BEGIN RSA PRIVATE" in secret:
            try:
                private_key = serialization.load_pem_private_key(
                    secret.encode("utf-8"),
                    password=None
                )
                
                if isinstance(private_key, ed25519.Ed25519PrivateKey):
                    signature = private_key.sign(payload)
                elif isinstance(private_key, rsa.RSAPrivateKey):
                    signature = private_key.sign(
                        payload,
                        padding.PKCS1v15(),
                        hashes.SHA256()
                    )
                else:
                    raise ValueError(f"Unsupported private key type: {type(private_key)}")
                    
                return base64.b64encode(signature).decode("utf-8")
            except Exception as e:
                logger.error(f"Failed to sign with asymmetric key: {e}")
                # Fallthrough to hmac just in case
        
        # Fallback to HMAC SHA-256 for backwards compatibility or REST endpoints
        return hmac.new(
            self.secret_key.encode("utf-8"),
            payload,
            hashlib.sha256
        ).hexdigest()

    def _get_timestamp(self) -> int:
        return int(time.time() * 1000)

    def build_payload(self, method: str, params: dict = {}, signed: bool = False, request_id: str = "") -> str:
        """
        Builds the JSON payload string for a WebSocket API request.
        """
        if params is None:
            params = {}

        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}

        if signed:
            params["apiKey"] = self.api_key
            params["timestamp"] = self._get_timestamp()
            signature = self._generate_signature(params)
            params["signature"] = signature

        if request_id is None:
            request_id = str(self._get_timestamp())

        payload = {
            "id": request_id,
            "method": method,
            "params": params
        }

        logger.debug(f"Built WS API payload for {method}: {payload}")
        return json.dumps(payload)

    def get_ws_url(self) -> str:
        """Returns the WebSocket URL."""
        return self.base_url

    async def connect(self):
        url = self.get_ws_url()
        self.websocket = await websockets.connect(url)
        return self

    async def disconnect(self):
        if hasattr(self, 'websocket') and self.websocket:
            await self.websocket.close()

    async def __aenter__(self):
        return await self.connect()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()

    async def send_payload(self, payload: str):
        if not hasattr(self, 'websocket') or not self.websocket:
            raise RuntimeError("WebSocket is not connected")
        await self.websocket.send(payload)

    async def recv_json(self, timeout=5.0) -> dict:
        if not hasattr(self, 'websocket') or not self.websocket:
            raise RuntimeError("WebSocket is not connected")
        response_str = await asyncio.wait_for(self.websocket.recv(), timeout=timeout)
        return json.loads(response_str)

