"""
Constants and enumerations.
"""

from __future__ import annotations

from enum import Enum


class Environment(str, Enum):
    """Environment types."""

    LIVE = "live"
    DEMO = "demo"
    TESTNET = "testnet"


DEFAULT_TIMEOUT_MS = 10_000  # 10 seconds
DEFAULT_POLL_INTERVAL_MS = 500  # 0.5 seconds
