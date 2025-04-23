"""Fixtures for Drinkaware integration tests."""
import json
import os
from unittest.mock import patch, AsyncMock, MagicMock
import pytest

from homeassistant.setup import async_setup_component
from homeassistant.const import CONF_TOKEN
from homeassistant.components.http import HomeAssistantView
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from custom_components.drinkaware.const import DOMAIN


@pytest.fixture
def mock_config_entry():
    """Create a mock config entry."""
    return {
        "entry_id": "test_entry_id",
        "domain": DOMAIN,
        "title": "Drinkaware - Test Account",
        "data": {
            "token": {
                "access_token": "test_access_token",
                "refresh_token": "test_refresh_token",
                "expires_in": 3600,
            },
            "account_name": "Test Account",
            "user_id": "test_user_id",
            "email": "test@example.com",
        },
        "options": {},
        "unique_id": "test_user_id",
    }


@pytest.fixture
def mock_setup_entry():
    """Mock setting up a config entry."""
    with patch(
        "custom_components.drinkaware.async_setup_entry", return_value=True
    ) as mock_setup:
        yield mock_setup


@pytest.fixture
def mock_aiohttp_client():
    """Mock aiohttp client."""
    with patch("homeassistant.helpers.aiohttp_client.async_get_clientsession") as mock_session:
        mock_client = AsyncMock()
        mock_session.return_value = mock_client
        yield mock_client


@pytest.fixture
def load_fixture():
    """Load a fixture."""
    def _load_fixture(filename):
        """Load a fixture file."""
        path = os.path.join(os.path.dirname(__file__), "fixtures", filename)
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    return _load_fixture


@pytest.fixture
def mock_api_responses(mock_aiohttp_client, load_fixture):
    """Set up mock API responses."""
    # Create a mock response for each API endpoint
    mock_assess_resp = AsyncMock()
    mock_assess_resp.status = 200
    mock_assess_resp.json = AsyncMock(return_value=load_fixture("assessment.json"))

    mock_stats_resp = AsyncMock()
    mock_stats_resp.status = 200
    mock_stats_resp.json = AsyncMock(return_value=load_fixture("stats.json"))

    mock_goals_resp = AsyncMock()
    mock_goals_resp.status = 200
    mock_goals_resp.json = AsyncMock(return_value=load_fixture("goals.json"))

    mock_summary_resp = AsyncMock()
    mock_summary_resp.status = 200
    mock_summary_resp.json = AsyncMock(return_value=load_fixture("summary.json"))

    mock_drinks_resp = Asyn
