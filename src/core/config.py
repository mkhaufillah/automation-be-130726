"""
Configuration management.

Loads from config.yaml, environment variables, and provides
a typed configuration object for all framework components.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import ClassVar, Optional

import yaml
from pydantic import BaseModel
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

from src.core.constants import Environment

load_dotenv()


class _ReportingConfig(BaseSettings):
    enabled: bool = True
    output_dir: str = "reports/"
    format: str = "html"
    screenshots: bool = True


class _LoggingConfig(BaseSettings):
    level: str = "INFO"
    file: str = "logs/automation.log"
    format: str = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"


class _EnvConfig(BaseSettings):
    @property
    def env(self) -> Environment:
        env_str = os.getenv("ENV", "testnet")
        return Environment(env_str)


class _BinanceConfig(BaseSettings):
    rest_url_live: str = "https://api.binance.com"
    rest_url_demo: str = "https://demo-api.binance.com"
    rest_url_testnet: str = "https://testnet.binance.vision"
    stream_url_live: str = "wss://stream.binance.com:9443"
    stream_url_demo: str = "wss://demo-stream.binance.com"
    stream_url_testnet: str = "wss://testnet.binance.vision"
    ws_url_live: str = "wss://ws-api.binance.com"
    ws_url_demo: str = "wss://demo-ws-api.binance.com"
    ws_url_testnet: str = "wss://ws-api.testnet.binance.vision"

    @property
    def api_key_live(self) -> str:
        return os.getenv("BINANCE_API_KEY_LIVE", "")

    @property
    def secret_key_live(self) -> str:
        return os.getenv("BINANCE_SECRET_KEY_LIVE", "")

    @property
    def api_key_demo(self) -> str:
        return os.getenv("BINANCE_API_KEY_DEMO", "")

    @property
    def secret_key_demo(self) -> str:
        return os.getenv("BINANCE_SECRET_KEY_DEMO", "")

    @property
    def api_key_testnet(self) -> str:
        return os.getenv("BINANCE_API_KEY_TESTNET", "")

    @property
    def secret_key_testnet(self) -> str:
        return os.getenv("BINANCE_SECRET_KEY_TESTNET", "")

    @property
    def ed25519_api_key_live(self) -> str:
        return os.getenv("ED25519_BINANCE_API_KEY_LIVE", "")

    @property
    def ed25519_secret_key_live(self) -> str:
        return os.getenv("ED25519_BINANCE_SECRET_KEY_LIVE", "")

    @property
    def ed25519_api_key_demo(self) -> str:
        return os.getenv("ED25519_BINANCE_API_KEY_DEMO", "")

    @property
    def ed25519_secret_key_demo(self) -> str:
        return os.getenv("ED25519_BINANCE_SECRET_KEY_DEMO", "")

    @property
    def ed25519_api_key_testnet(self) -> str:
        return os.getenv("ED25519_BINANCE_API_KEY_TESTNET", "")

    @property
    def ed25519_secret_key_testnet(self) -> str:
        return os.getenv("ED25519_BINANCE_SECRET_KEY_TESTNET", "")


class AutomationConfig(BaseModel):
    """Central configuration — loads from config.yaml + env overrides."""

    # Config file path (set at runtime, not from env)
    _config_path: ClassVar[Optional[Path]] = None

    reporting: _ReportingConfig = _ReportingConfig()
    logging: _LoggingConfig = _LoggingConfig()
    env: _EnvConfig = _EnvConfig()
    binance: _BinanceConfig = _BinanceConfig()

    @classmethod
    def load(cls, path: str | Path = "config/config.yaml") -> "AutomationConfig":
        """Load configuration from YAML file with env overrides."""

        config_path = Path(path)
        cls._config_path = config_path

        if config_path.exists():
            with open(config_path) as f:
                raw = yaml.safe_load(f) or {}
        else:
            raw = {}

        # Flatten nested dicts for pydantic; pydantic_settings handles deep nesting
        # with env_nested_delimiter, but for YAML load we construct directly.
        return cls(**raw)

    def get_binance_rest_url(self) -> str:
        """Get the Binance REST API URL based on the environment."""

        if self.env.env == Environment.LIVE:
            return self.binance.rest_url_live
        if self.env.env == Environment.DEMO:
            return self.binance.rest_url_demo
        return self.binance.rest_url_testnet

    def get_binance_stream_url(self) -> str:
        """Get the Binance WebSocket stream URL based on the environment."""

        if self.env.env == Environment.LIVE:
            return self.binance.stream_url_live
        if self.env.env == Environment.DEMO:
            return self.binance.stream_url_demo
        return self.binance.stream_url_testnet

    def get_binance_ws_url(self) -> str:
        """Get the Binance WebSocket URL based on the environment."""

        if self.env.env == Environment.LIVE:
            return self.binance.ws_url_live
        if self.env.env == Environment.DEMO:
            return self.binance.ws_url_demo
        return self.binance.ws_url_testnet

    def get_binance_api_key(self) -> str:
        """Get the Binance API KEY based on the environment."""

        if self.env.env == Environment.LIVE:
            return self.binance.api_key_live
        if self.env.env == Environment.DEMO:
            return self.binance.api_key_demo
        return self.binance.api_key_testnet

    def get_binance_secret_key(self) -> str:
        """Get the Binance SECRET KEY based on the environment."""

        if self.env.env == Environment.LIVE:
            return self.binance.secret_key_live
        if self.env.env == Environment.DEMO:
            return self.binance.secret_key_demo
        return self.binance.secret_key_testnet

    def get_ed25519_binance_api_key(self) -> str:
        """Get the Binance API KEY based on the environment."""

        if self.env.env == Environment.LIVE:
            return self.binance.ed25519_api_key_live
        if self.env.env == Environment.DEMO:
            return self.binance.ed25519_api_key_demo
        return self.binance.ed25519_api_key_testnet

    def get_ed25519_binance_secret_key(self) -> str:
        """Get the Binance SECRET KEY based on the environment."""

        if self.env.env == Environment.LIVE:
            return self.binance.ed25519_secret_key_live
        if self.env.env == Environment.DEMO:
            return self.binance.ed25519_secret_key_demo
        return self.binance.ed25519_secret_key_testnet
