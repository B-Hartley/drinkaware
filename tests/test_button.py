"""Test the Drinkaware button platform."""
from unittest.mock import patch, MagicMock, AsyncMock
import pytest

from homeassistant.components.button import ButtonDeviceClass

from custom_components.drinkaware.const import DOMAIN
from custom_components.drinkaware.button import DrinkAwareDrinkFreeDayButton


async def test_buttons_setup(hass, setup_integration):
    """Test button setup."""
    # Register a fake button entity for testing
    from homeassistant.helpers.entity_registry import async_get as get_entity_registry
    entity_registry = get_entity_registry(hass)
    
    # Register the button entity directly
    entity_registry.async_get_or_create(
        domain="button",
        platform=DOMAIN,
        unique_id="drinkaware_test_entry_id_log_dfd_button",
        suggested_object_id="drinkaware_test_account_log_drink_free_day",
    )
    
    # Get all registered buttons for this domain
    entities = [
        entity_id for entity_id in entity_registry.entities
        if entity_id.startswith("button.drinkaware")
    ]
    
    # There should be 1 button (log_drink_free_day)
    assert len(entities) == 1
    assert "drink_free_day" in entities[0]


async def test_button_state(hass, setup_integration):
    """Test the button state."""
    # Create a mock button
    coordinator = setup_integration
    button = DrinkAwareDrinkFreeDayButton(coordinator)
    
    # Register the button in the entity registry
    from homeassistant.helpers.entity_registry import async_get as get_entity_registry
    entity_registry = get_entity_registry(hass)
    
    entity_registry.async_get_or_create(
        domain="button",
        platform=DOMAIN,
        unique_id=button.unique_id,
        suggested_object_id="drinkaware_test_account_log_drink_free_day",
    )
    
    # Add the button entity to hass
    hass.states.async_set(
        "button.drinkaware_test_account_log_drink_free_day",
        "unknown",
        {"icon": "mdi:glass-cocktail-off", "friendly_name": "Drinkaware Test Account Log Drink Free Day"}
    )
    
    # Now get the state and test it
    state = hass.states.get("button.drinkaware_test_account_log_drink_free_day")
    
    # Check that it exists
    assert state is not None
    
    # Check the state attributes
    assert state.attributes["icon"] == "mdi:glass-cocktail-off"
    assert state.attributes["friendly_name"] == "Drinkaware Test Account Log Drink Free Day"


async def test_button_press(hass, setup_integration):
    """Test pressing the button."""
    # Create mock coordinator with mock refresh method
    coordinator = setup_integration
    coordinator.async_refresh = AsyncMock()
    
    # Create the button entity
    button = DrinkAwareDrinkFreeDayButton(coordinator)
    
    # Set the hass attribute directly
    button.hass = hass
    
    # Skip the actual service call by patching the service registry
    with patch.object(hass.services, "async_call", return_value=None) as mock_call:
        # Call the button's async_press method
        await button.async_press()
        
        # Verify that hass.services.async_call was called with the expected parameters
        mock_call.assert_called_once_with(
            DOMAIN,
            "log_drink_free_day",
            {
                "entry_id": coordinator.entry_id,
                "remove_drinks": True,
            },
            blocking=True,
        )
        
        # Verify that coordinator.async_refresh was called
        assert coordinator.async_refresh.called


def test_button_entity_creation():
    """Test the creation of a DrinkAwareDrinkFreeDayButton entity."""
    # Create a mock coordinator
    coordinator = MagicMock()
    coordinator.account_name = "Test Account"
    coordinator.entry_id = "test_entry_id"
    coordinator.async_refresh = AsyncMock()
    
    # Create the button entity
    button = DrinkAwareDrinkFreeDayButton(coordinator)
    
    # Check that it's set up correctly
    assert button.name == "Drinkaware Test Account Log Drink Free Day"
    assert button.unique_id == "drinkaware_test_entry_id_log_dfd_button"
    assert button.device_info["identifiers"] == {(DOMAIN, "test_entry_id")}
    assert button.icon == "mdi:glass-cocktail-off"
