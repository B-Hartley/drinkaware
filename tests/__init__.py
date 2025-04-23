"""Test the Drinkaware integration setup."""
from unittest.mock import patch, MagicMock, AsyncMock
import pytest

from homeassistant.setup import async_setup_component
from homeassistant.const import CONF_TOKEN
from homeassistant.config_entries import ConfigEntry

from custom_components.drinkaware.const import DOMAIN
from custom_components.drinkaware import async_setup, async_setup_entry, async_unload_entry


async def test_async_setup(hass):
    """Test the component setup."""
    # Mock finding the integration in Home Assistant
    with patch("homeassistant.loader.async_get_integration") as mock_get_integration:
        # Create a mock integration
        mock_integration = MagicMock()
        mock_integration.domain = DOMAIN
        # Set up the mock to return our mock integration
        mock_get_integration.return_value = mock_integration
        
        with patch("custom_components.drinkaware.async_setup_entry", return_value=True):
            assert await async_setup(hass, {})
            assert DOMAIN in hass.data
        

async def test_async_setup_entry(hass, mock_config_entry, mock_api_responses):
    """Test the config entry setup."""
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
    
    # Initialize the component data
    hass.data.setdefault(DOMAIN, {})
    
    # Mock the coordinator's refresh method
    with patch("custom_components.drinkaware.DrinkAwareDataUpdateCoordinator.async_config_entry_first_refresh"):
        # Set up the entry
        result = await async_setup_entry(hass, config_entry)
        
        # Verify the results
        assert result is True
        assert config_entry.entry_id in hass.data[DOMAIN]
        
        # Check that the coordinator is set up correctly
        coordinator = hass.data[DOMAIN][config_entry.entry_id]
        assert coordinator.account_name == "Test Account"
        assert coordinator.email == "test@example.com"
        assert coordinator.access_token == "test_access_token"


async def test_async_unload_entry(hass, mock_config_entry):
    """Test the config entry unloading."""
    # Create a ConfigEntry
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
    
    # Set up mock coordinator in hass.data
    mock_coordinator = MagicMock()
    hass.data[DOMAIN] = {config_entry.entry_id: mock_coordinator}
    
    # Mock platform unloading
    with patch("homeassistant.config_entries.ConfigEntries.async_unload_platforms", return_value=True):
        # Unload the entry
        result = await async_unload_entry(hass, config_entry)
        
        # Verify the results
        assert result is True
        assert config_entry.entry_id not in hass.data[DOMAIN]


async def test_update_listener(hass, mock_config_entry):
    """Test the update listener."""
    # Create a ConfigEntry
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
    
    # Mock config entry reloading
    with patch("homeassistant.config_entries.ConfigEntries.async_reload") as mock_reload:
        # Call the update listener
        from custom_components.drinkaware import update_listener
        await update_listener(hass, config_entry)
        
        # Verify that reload was called with the correct entry_id
        mock_reload.assert_called_once_with(config_entry.entry_id)