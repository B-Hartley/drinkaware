"""
Button platform for Drinkaware integration.
"""
import logging
from datetime import datetime

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import DrinkAwareDataUpdateCoordinator
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Drinkaware button based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = [
        DrinkAwareDrinkFreeDayButton(coordinator),
    ]
    
    async_add_entities(entities)


class DrinkAwareDrinkFreeDayButton(CoordinatorEntity, ButtonEntity):
    """Button to log a drink-free day for today."""

    def __init__(self, coordinator: DrinkAwareDataUpdateCoordinator) -> None:
        """Initialize the button."""
        super().__init__(coordinator)
        self._attr_name = f"Drinkaware {coordinator.account_name} Log Drink Free Day"
        self._attr_unique_id = f"drinkaware_{coordinator.entry_id}_log_dfd_button"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.entry_id)},
            "name": f"Drinkaware {coordinator.account_name}",
            "manufacturer": "Drinkaware",
            "model": "Account",
            "sw_version": "1.0",
        }
        self._attr_icon = "mdi:glass-cocktail-off"
    
    async def async_press(self) -> None:
        """Handle the button press - Log today as a drink-free day."""
        try:
            # Call the service with today's date
            _LOGGER.info("Button pressed: Logging drink-free day for today")
            
            # Call the log_drink_free_day service with entry_id and remove_drinks=True
            await self.hass.services.async_call(
                DOMAIN,
                "log_drink_free_day",
                {
                    "entry_id": self.coordinator.entry_id,
                    "remove_drinks": True,  # Automatically remove existing drinks
                },
                blocking=True,
            )
            
            # Refresh coordinator data to update all sensors
            await self.coordinator.async_refresh()
            
            _LOGGER.info("Successfully logged drink-free day for today")
        except Exception as err:
            _LOGGER.error("Error logging drink-free day: %s", err)