"""
Custom exceptions.
"""


class AutomationException(Exception):
    """Base exception for all framework errors."""


class ConfigException(AutomationException):
    """Configuration loading or validation errors."""


class TimeoutException(AutomationException):
    """Timeout when execute some test or configuration."""
