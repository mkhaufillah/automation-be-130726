"""
Package initializer.
"""

from src.core.config import AutomationConfig
from src.core.constants import Environment, DEFAULT_POLL_INTERVAL_MS, DEFAULT_TIMEOUT_MS
from src.core.exceptions import AutomationException, ConfigException, TimeoutException
from src.core.test_data import TestData
from src.utils.logger import get_logger, setup_logging
from src.rest.base_binance_rest_client import BaseBinanceRestClient
from src.stream.base_binance_stream_client import BaseBinanceStreamClient, StreamConnection
from src.ws.base_binance_ws_client import BaseBinanceWsClient
from src.utils.schema import validate_schema

__all__ = [
    "AutomationConfig",
    "Environment",
    "AutomationException",
    "ConfigException",
    "TimeoutException",
    "get_logger",
    "setup_logging",
    "DEFAULT_POLL_INTERVAL_MS",
    "DEFAULT_TIMEOUT_MS",
    "BaseBinanceRestClient",
    "BaseBinanceStreamClient",
    "StreamConnection",
    "BaseBinanceWsClient",
    "TestData",
    "validate_schema"
]
