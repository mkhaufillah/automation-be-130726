"""
pytest conftest — framework fixtures and hooks.

Provides:
  - load_config: Loads config.yaml
"""

from __future__ import annotations

import os
import pytest
from _pytest.config.argparsing import Parser

from src import AutomationConfig, setup_logging, get_logger, Environment, TestData

logger = get_logger(__name__)


def pytest_addoption(parser: Parser) -> None:
    parser.addoption(
        "--config",
        action="store",
        default="config/config.yaml",
        help="Path to the configuration YAML file.",
    )


def pytest_configure(config: pytest.Config) -> None:
    config_path = config.getoption("--config")
    cfg = AutomationConfig.load(config_path)

    setup_logging(
        level=cfg.logging.level,
        file_path=cfg.logging.file,
        fmt=cfg.logging.format
    )

    os.makedirs(cfg.reporting.output_dir, exist_ok=True)

    # Set HTML report path dynamically based on config.yaml
    if cfg.reporting.enabled and cfg.reporting.format == "html":
        report_path = os.path.join(cfg.reporting.output_dir, "report.html")
        config.option.htmlpath = report_path
        config.option.self_contained_html = True


def pytest_runtest_setup(item: pytest.Item) -> None:
    cfg = AutomationConfig.load()

    test_markers = [mark.name for mark in item.iter_markers()]

    supported_envs = {Environment.TESTNET, Environment.LIVE, Environment.DEMO}
    has_env_marker = any(m in supported_envs for m in test_markers)

    if has_env_marker and cfg.env.env not in test_markers:
        pytest.skip(
            f"Test skipped: Not configured for the '{cfg.env.env}' environment.")


@pytest.fixture(autouse=True)
def check_marker(request: pytest.FixtureRequest):
    # Retrieve the marker from the current test node
    marker = request.node.get_closest_marker("id")

    if marker:
        # Access positional arguments (marker.args)
        if marker.args:
            logger.info(
                f"\n\n ========= RUNNING TEST WITH ID: {marker.args[0]} ========= \n")


@pytest.fixture(scope="session")
def config(request: pytest.FixtureRequest) -> AutomationConfig:
    config_path = request.config.getoption("--config")
    cfg = AutomationConfig.load(config_path)

    logger.info(
        "Framework configured: config=%s",
        config_path,
    )
    return cfg


@pytest.fixture
def test_data_based_id(request: pytest.FixtureRequest) -> dict:
    """Load test data from JSON files."""
    data = {}

    marker = request.node.get_closest_marker("id")
    if marker:
        if marker.args:
            test_data = TestData()
            test_data.load_test_data()
            data = test_data.get_test_data(marker.args[0])
            logger.info(
                f"Loaded test data for marker '{marker.args[0]}': {data}")

    return data
