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

    mock_drinks_resp = AsyncMock()
    mock_drinks_resp.status = 200
    mock_drinks_resp.json = AsyncMock(return_value=load_fixture("drinks.json"))

    # Set up the context manager returns for mock_client.get()
    mock_aiohttp_client.get = AsyncMock()
    mock_aiohttp_client.get.side_effect = lambda url, **kwargs: {
        "https://api.drinkaware.co.uk/tools/v1/selfassessment": mock_assess_resp,
        "https://api.drinkaware.co.uk/tracking/v1/stats": mock_stats_resp,
        "https://api.drinkaware.co.uk/tracking/v1/goals": mock_goals_resp,
        "https://api.drinkaware.co.uk/drinks/v1/generic": mock_drinks_resp,
        "https://api.drinkaware.co.uk/drinks/v1/search": mock_drinks_resp,
    }.get(url, mock_summary_resp)

    # Also mock post/put/delete
    mock_success_resp = AsyncMock()
    mock_success_resp.status = 200
    mock_success_resp.json = AsyncMock(return_value={"success": True})

    mock_aiohttp_client.post = AsyncMock(return_value=mock_success_resp)
    mock_aiohttp_client.put = AsyncMock(return_value=mock_success_resp)
    mock_aiohttp_client.delete = AsyncMock(return_value=mock_success_resp)

    return mock_aiohttp_client


@pytest.fixture
async def setup_integration(hass, mock_config_entry, mock_api_responses):
    """Set up the Drinkaware integration."""
    # Initialize the component
    from homeassistant.config_entries import ConfigEntry
    
    # Create a ConfigEntry from the mock data
    config_entry = ConfigEntry(
        version=1,
        domain=DOMAIN,
        title=mock_config_entry["title"],
        data=mock_config_entry["data"],
        source="test",
        options={},
        entry_id=mock_config_entry["entry_id"],
        unique_id=mock_config_entry["unique_id"],
    )
    
    # Set up the domain in hass.data
    hass.data.setdefault(DOMAIN, {})
    
    # Mock the coordinator creation
    with patch("homeassistant.helpers.aiohttp_client.async_get_clientsession"), \
         patch("custom_components.drinkaware.DrinkAwareDataUpdateCoordinator._async_update_data"):
        
        # Set up the integration
        assert await hass.config_entries.async_setup(config_entry.entry_id)
        await hass.async_block_till_done()
    
    return hass