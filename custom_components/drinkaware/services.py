"""
Services for Drinkaware integration.
"""
import logging
import voluptuous as vol
from datetime import datetime, timedelta
import aiohttp

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import config_validation as cv
from homeassistant.const import CONF_ENTITY_ID, ATTR_DATE, CONF_NAME
from homeassistant.exceptions import HomeAssistantError

from .const import (
    DOMAIN,
    API_BASE_URL,
    ENDPOINT_DAY,
    ENDPOINT_DRINKS,
    SERVICE_LOG_DRINK_FREE_DAY,
    SERVICE_LOG_DRINK,
    SERVICE_DELETE_DRINK,
    SERVICE_REMOVE_DRINK_FREE_DAY,
    SERVICE_LOG_SLEEP_QUALITY,
    SERVICE_REFRESH,
    ATTR_DRINK_TYPE,
    ATTR_DRINK_MEASURE,
    ATTR_DRINK_ABV,
    ATTR_DRINK_QUANTITY,
    ATTR_ENTRY_ID,
    ATTR_SLEEP_QUALITY,
    ATTR_ACCOUNT_NAME,
)

from .utils import get_entry_id_by_account_name

_LOGGER = logging.getLogger(__name__)

# Create a validator for requiring exactly one of entry_id or account_name
def require_entry_id_or_account_name(value):
    """Validate that either entry_id or account_name is provided."""
    if ATTR_ENTRY_ID not in value and ATTR_ACCOUNT_NAME not in value:
        raise vol.Invalid("Either entry_id or account_name must be provided")
    return value

# Base dictionary for all Drinkaware service calls
BASE_DICT = {
    vol.Optional(ATTR_ENTRY_ID): cv.string,
    vol.Optional(ATTR_ACCOUNT_NAME): cv.string,
}

# Function to create schema with validation
def create_schema(schema_dict):
    """Create a schema with the base validation."""
    return vol.Schema(vol.All(schema_dict, require_entry_id_or_account_name))

# Schemas for service calls
DRINK_FREE_DAY_SCHEMA = create_schema({
    **BASE_DICT,
    vol.Optional(ATTR_DATE): cv.date,
    vol.Optional("remove_drinks", default=False): cv.boolean,  # Add this line
})

LOG_DRINK_SCHEMA = create_schema({
    **BASE_DICT,
    vol.Required(ATTR_DRINK_TYPE): cv.string,  # This would be the drink ID from API
    vol.Required(ATTR_DRINK_MEASURE): cv.string,  # This would be the measure ID from API
    vol.Optional(ATTR_DRINK_ABV, default=0): vol.Coerce(float),
    vol.Optional(ATTR_DRINK_QUANTITY, default=1): vol.Coerce(int),
    vol.Optional(ATTR_DATE): cv.date,
    vol.Optional("auto_remove_dfd", default=False): cv.boolean,
})

DELETE_DRINK_SCHEMA = create_schema({
    **BASE_DICT,
    vol.Required(ATTR_DRINK_TYPE): cv.string,
    vol.Required(ATTR_DRINK_MEASURE): cv.string,
    vol.Optional(ATTR_DATE): cv.date,
})

REMOVE_DRINK_FREE_DAY_SCHEMA = create_schema({
    **BASE_DICT,
    vol.Optional(ATTR_DATE): cv.date,
})

LOG_SLEEP_QUALITY_SCHEMA = create_schema({
    **BASE_DICT,
    vol.Required(ATTR_SLEEP_QUALITY): vol.In(["poor", "average", "great"]),
    vol.Optional(ATTR_DATE): cv.date,
})

REFRESH_SCHEMA = create_schema({
    **BASE_DICT,
})

def get_coordinator_by_name_or_id(hass, entry_id=None, account_name=None):
    """Get coordinator by either entry_id or account_name."""
    if entry_id and entry_id in hass.data[DOMAIN]:
        return hass.data[DOMAIN][entry_id]
    
    if account_name:
        # Check the account name map first for more efficient lookup
        mapped_entry_id = get_entry_id_by_account_name(hass, account_name)
        if mapped_entry_id and mapped_entry_id in hass.data[DOMAIN]:
            return hass.data[DOMAIN][mapped_entry_id]
            
        # Fallback to searching if not in the map
        for entry_id, coordinator in hass.data[DOMAIN].items():
            if entry_id == "account_name_map":
                continue  # Skip the mapping dictionary
            if hasattr(coordinator, 'account_name') and coordinator.account_name.lower() == account_name.lower():
                return coordinator
    
    # If we have only one entry, return that
    entries = [
        entry_id for entry_id in hass.data[DOMAIN] 
        if entry_id != "account_name_map"
    ]
    if len(entries) == 1:
        return hass.data[DOMAIN][entries[0]]
    
    return None

async def async_setup_services(hass: HomeAssistant) -> None:
    """Set up services for Drinkaware integration."""
    
    async def log_drink_free_day(coordinator, date, remove_drinks=False):
        """Log a drink-free day to Drinkaware."""
        # Convert date to ISO format string
        date_str = date.strftime("%Y-%m-%d")
        
        # If remove_drinks is True, first remove any existing drinks for the day
        if remove_drinks:
            try:
                await remove_all_drinks_for_day(coordinator, date)
                _LOGGER.info("Automatically removed all drinks before marking as drink-free day")
            except Exception as err:
                _LOGGER.warning("Error removing drinks before marking as drink-free day: %s", err)
        
        # Based on MITM logs, for drink-free day we need to PUT to the day endpoint
        url = f"{API_BASE_URL}/tracking/v1/activity/{date_str}/drinkfreeday"
        
        headers = {
            "Authorization": f"Bearer {coordinator.access_token}",
            "Accept": "application/json",
        }
        
        async with coordinator.session.put(url, headers=headers) as resp:
            if resp.status != 200 and resp.status != 204:
                text = await resp.text()
                _LOGGER.error("Error logging drink-free day: %s - %s", resp.status, text)
                raise Exception(f"Failed to log drink-free day: {resp.status} - {text}")
            
            _LOGGER.info("Successfully logged drink-free day for %s", date_str)
            return True


    async def remove_all_drinks_for_day(coordinator, date):
        """Remove all drinks for a specific day.
        
        This is a helper function used before marking a day as drink-free.
        It first gets all drinks for the day, then removes them one by one.
        """
        # Convert date to ISO format string
        date_str = date.strftime("%Y-%m-%d")
        
        # First, we need to get all drinks for the day
        url = f"{API_BASE_URL}/tracking/v1/activity/{date_str}"
        
        headers = {
            "Authorization": f"Bearer {coordinator.access_token}",
            "Accept": "application/json",
        }
        
        try:
            # Get all activity for the day
            async with coordinator.session.get(url, headers=headers) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    _LOGGER.error("Error getting drinks for day: %s - %s", resp.status, text)
                    return False
                    
                activity = await resp.json()
                if not activity or "drinks" not in activity:
                    _LOGGER.debug("No drinks found for %s", date_str)
                    return True
                    
                drinks = activity.get("drinks", [])
                
                # Now remove each drink
                for drink in drinks:
                    drink_id = drink.get("drinkId")
                    measure_id = drink.get("measureId")
                    
                    if drink_id and measure_id:
                        try:
                            # Use the delete_drink function to remove this drink
                            await delete_drink(coordinator, drink_id, measure_id, date)
                            _LOGGER.debug("Removed drink %s (%s) from %s", 
                                         drink.get("drinkName", "Unknown"), 
                                         drink.get("measureName", "Unknown"),
                                         date_str)
                        except Exception as err:
                            _LOGGER.error("Error removing drink: %s", err)
                
                return True
        except Exception as err:
            _LOGGER.error("Error in remove_all_drinks_for_day: %s", err)
            return False

    async def async_log_drink_free_day(service_call) -> None:
        """Log a drink-free day to Drinkaware."""
        entry_id = service_call.data.get(ATTR_ENTRY_ID)
        account_name = service_call.data.get(ATTR_ACCOUNT_NAME, "Bruce")
        date = service_call.data.get(ATTR_DATE, datetime.now().date())
        remove_drinks = service_call.data.get("remove_drinks", False)
        
        coordinator = get_coordinator_by_name_or_id(hass, entry_id, account_name)
        if not coordinator:
            raise HomeAssistantError(
                "No matching Drinkaware integration found. Please specify a valid entry_id or account_name"
            )
            
        try:
            await log_drink_free_day(coordinator, date, remove_drinks)
            # Trigger refresh to update the sensors with new data
            await coordinator.async_refresh()
        except Exception as err:
            _LOGGER.error("Error logging drink-free day: %s", err)
            raise HomeAssistantError(f"Error logging drink-free day: {err}")
            
    async def async_log_drink(service_call) -> None:
        """Log a drink to Drinkaware."""
        entry_id = service_call.data.get(ATTR_ENTRY_ID)
        account_name = service_call.data.get(ATTR_ACCOUNT_NAME, "Bruce")
        drink_type = service_call.data[ATTR_DRINK_TYPE]
        drink_measure = service_call.data[ATTR_DRINK_MEASURE]
        abv = service_call.data[ATTR_DRINK_ABV]
        quantity = service_call.data[ATTR_DRINK_QUANTITY]
        date = service_call.data.get(ATTR_DATE, datetime.now().date())
        auto_remove_dfd = service_call.data.get("auto_remove_dfd", False)
        
        # Handle "custom" value for drink_type or measure_id
        if drink_type == "custom":
            raise HomeAssistantError(
                "When using a custom drink, enter the actual drink ID instead of selecting 'custom'"
            )
        if drink_measure == "custom":
            raise HomeAssistantError(
                "When using a custom measure, enter the actual measure ID instead of selecting 'custom'"
            )
        
        coordinator = get_coordinator_by_name_or_id(hass, entry_id, account_name)
        if not coordinator:
            raise HomeAssistantError(
                "No matching Drinkaware integration found. Please specify a valid entry_id or account_name"
            )
            
        try:
            await log_drink(coordinator, drink_type, drink_measure, abv, quantity, date, auto_remove_dfd)
            # Trigger refresh to update the sensors with new data
            await coordinator.async_refresh()
        except Exception as err:
            _LOGGER.error("Error logging drink: %s", err)
            raise HomeAssistantError(f"Error logging drink: {err}")

    async def async_delete_drink(service_call) -> None:
        """Delete a drink from Drinkaware."""
        entry_id = service_call.data.get(ATTR_ENTRY_ID)
        account_name = service_call.data.get(ATTR_ACCOUNT_NAME, "Bruce")
        drink_type = service_call.data[ATTR_DRINK_TYPE]
        drink_measure = service_call.data[ATTR_DRINK_MEASURE]
        date = service_call.data.get(ATTR_DATE, datetime.now().date())
        
        # Handle "custom" value for drink_type or measure_id
        if drink_type == "custom" or drink_measure == "custom":
            raise HomeAssistantError(
                "When using a custom drink/measure, enter the actual ID instead of selecting 'custom'"
            )
        
        coordinator = get_coordinator_by_name_or_id(hass, entry_id, account_name)
        if not coordinator:
            raise HomeAssistantError(
                "No matching Drinkaware integration found. Please specify a valid entry_id or account_name"
            )
            
        try:
            await delete_drink(coordinator, drink_type, drink_measure, date)
            # Trigger refresh to update the sensors with new data
            await coordinator.async_refresh()
        except Exception as err:
            _LOGGER.error("Error deleting drink: %s", err)
            raise HomeAssistantError(f"Error deleting drink: {err}")
            
    async def async_remove_drink_free_day(service_call) -> None:
        """Remove a drink-free day marking from Drinkaware."""
        entry_id = service_call.data.get(ATTR_ENTRY_ID)
        account_name = service_call.data.get(ATTR_ACCOUNT_NAME, "Bruce")
        date = service_call.data.get(ATTR_DATE, datetime.now().date())
        
        coordinator = get_coordinator_by_name_or_id(hass, entry_id, account_name)
        if not coordinator:
            raise HomeAssistantError(
                "No matching Drinkaware integration found. Please specify a valid entry_id or account_name"
            )
            
        try:
            await remove_drink_free_day(coordinator, date)
            # Trigger refresh to update the sensors with new data
            await coordinator.async_refresh()
        except Exception as err:
            _LOGGER.error("Error removing drink-free day: %s", err)
            raise HomeAssistantError(f"Error removing drink-free day: {err}")
            
    async def async_log_sleep_quality(service_call) -> None:
        """Log sleep quality to Drinkaware."""
        entry_id = service_call.data.get(ATTR_ENTRY_ID)
        account_name = service_call.data.get(ATTR_ACCOUNT_NAME, "Bruce")
        quality = service_call.data[ATTR_SLEEP_QUALITY]
        date = service_call.data.get(ATTR_DATE, datetime.now().date())
        
        coordinator = get_coordinator_by_name_or_id(hass, entry_id, account_name)
        if not coordinator:
            raise HomeAssistantError(
                "No matching Drinkaware integration found. Please specify a valid entry_id or account_name"
            )
            
        try:
            await log_sleep_quality(coordinator, quality, date)
            # Trigger refresh to update the sensors with new data
            await coordinator.async_refresh()
        except Exception as err:
            _LOGGER.error("Error logging sleep quality: %s", err)
            raise HomeAssistantError(f"Error logging sleep quality: {err}")

    async def async_refresh(service_call) -> None:
        """Refresh Drinkaware data."""
        entry_id = service_call.data.get(ATTR_ENTRY_ID)
        account_name = service_call.data.get(ATTR_ACCOUNT_NAME, "Bruce")
        
        coordinator = get_coordinator_by_name_or_id(hass, entry_id, account_name)
        if not coordinator:
            raise HomeAssistantError(
                "No matching Drinkaware integration found. Please specify a valid entry_id or account_name"
            )
            
        try:
            await coordinator.async_refresh()
            _LOGGER.info("Drinkaware data for %s refreshed successfully", coordinator.account_name)
        except Exception as err:
            _LOGGER.error("Error refreshing Drinkaware data: %s", err)
            raise HomeAssistantError(f"Error refreshing Drinkaware data: {err}")

    # Register services
    hass.services.async_register(
        DOMAIN, SERVICE_LOG_DRINK_FREE_DAY, async_log_drink_free_day, schema=DRINK_FREE_DAY_SCHEMA
    )
    
    hass.services.async_register(
        DOMAIN, SERVICE_LOG_DRINK, async_log_drink, schema=LOG_DRINK_SCHEMA
    )
    
    hass.services.async_register(
        DOMAIN, SERVICE_DELETE_DRINK, async_delete_drink, schema=DELETE_DRINK_SCHEMA
    )
    
    hass.services.async_register(
        DOMAIN, SERVICE_REMOVE_DRINK_FREE_DAY, async_remove_drink_free_day, schema=REMOVE_DRINK_FREE_DAY_SCHEMA
    )
    
    hass.services.async_register(
        DOMAIN, SERVICE_LOG_SLEEP_QUALITY, async_log_sleep_quality, schema=LOG_SLEEP_QUALITY_SCHEMA
    )
    
    hass.services.async_register(
        DOMAIN, SERVICE_REFRESH, async_refresh, schema=REFRESH_SCHEMA
    )

async def async_unload_services(hass: HomeAssistant) -> None:
    """Unload Drinkaware services."""
    hass.services.async_remove(DOMAIN, SERVICE_LOG_DRINK_FREE_DAY)
    hass.services.async_remove(DOMAIN, SERVICE_LOG_DRINK)
    hass.services.async_remove(DOMAIN, SERVICE_DELETE_DRINK)
    hass.services.async_remove(DOMAIN, SERVICE_REMOVE_DRINK_FREE_DAY)
    hass.services.async_remove(DOMAIN, SERVICE_LOG_SLEEP_QUALITY)
    hass.services.async_remove(DOMAIN, SERVICE_REFRESH)


async def log_drink(coordinator, drink_type, drink_measure, abv, quantity, date, auto_remove_dfd=False):
    """Log a drink to Drinkaware."""
    # Convert date to ISO format string
    date_str = date.strftime("%Y-%m-%d")
    
    # If auto_remove_dfd is True, check if day is marked as drink-free and remove that mark first
    if auto_remove_dfd:
        try:
            # Check if we need to remove a drink-free day by trying to remove it
            await remove_drink_free_day(coordinator, date)
            _LOGGER.info("Automatically removed drink-free day flag before adding drink")
        except Exception as err:
            # If removing the drink-free day fails, it probably wasn't set, so we can ignore the error
            _LOGGER.debug("Day was not marked as drink-free or error removing: %s", err)
    
    # Based on MITM logs, the API can use either PUT with quantity or POST with quantityAdjustment
    # PUT seems to be for setting an absolute value, POST for incremental changes
    url = f"{API_BASE_URL}/tracking/v1/activity/{date_str}"
    
    headers = {
        "Authorization": f"Bearer {coordinator.access_token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    
    # The payload for logging a drink - use PUT with quantity for setting an absolute value
    payload = {
        "drinkId": drink_type,
        "measureId": drink_measure,
        "quantity": quantity  # Sets the absolute quantity
    }
    
    # If user provided a custom ABV, include it
    if abv > 0:
        payload["abv"] = abv
    
    async with coordinator.session.put(url, headers=headers, json=payload) as resp:
        if resp.status != 200 and resp.status != 204:
            text = await resp.text()
            _LOGGER.error("Error logging drink: %s - %s", resp.status, text)
            raise Exception(f"Failed to log drink: {resp.status} - {text}")
        
        result = await resp.json()
        _LOGGER.info("Successfully logged drink for %s (quantity: %s)", date_str, result.get("quantity", 0))
        return True


async def delete_drink(coordinator, drink_type, drink_measure, date):
    """Delete a drink from Drinkaware.
    
    This function will completely delete the specified drink entry, not just reduce its quantity.
    """
    # Convert date to ISO format string
    date_str = date.strftime("%Y-%m-%d")
    
    # Based on the MITM logs, there are two ways to delete drinks:
    # 1. Use POST with quantityAdjustment: -1 to decrement
    # 2. Use DELETE on the specific drink ID and measure ID to completely remove it
    
    # We'll use method #2 which completely removes the drink
    url = f"{API_BASE_URL}/tracking/v1/activity/{date_str}/{drink_type}/{drink_measure}"
    
    headers = {
        "Authorization": f"Bearer {coordinator.access_token}",
        "Accept": "application/json",
    }
    
    async with coordinator.session.delete(url, headers=headers) as resp:
        if resp.status != 200 and resp.status != 204:
            text = await resp.text()
            _LOGGER.error("Error deleting drink: %s - %s", resp.status, text)
            raise Exception(f"Failed to delete drink: {resp.status} - {text}")
        
        _LOGGER.info("Successfully deleted drink for %s", date_str)
        return True


async def adjust_drink_quantity(coordinator, drink_type, drink_measure, quantity_adjustment, date):
    """Adjust the quantity of a drink by incrementing or decrementing.
    
    This is useful for adding or reducing drink quantities without knowing the current count.
    """
    # Convert date to ISO format string
    date_str = date.strftime("%Y-%m-%d")
    
    url = f"{API_BASE_URL}/tracking/v1/activity/{date_str}"
    
    headers = {
        "Authorization": f"Bearer {coordinator.access_token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    
    # The payload for adjusting a drink quantity
    payload = {
        "drinkId": drink_type,
        "measureId": drink_measure,
        "quantityAdjustment": quantity_adjustment  # Can be positive or negative
    }
    
    async with coordinator.session.post(url, headers=headers, json=payload) as resp:
        if resp.status != 200 and resp.status != 204:
            text = await resp.text()
            _LOGGER.error("Error adjusting drink quantity: %s - %s", resp.status, text)
            raise Exception(f"Failed to adjust drink quantity: {resp.status} - {text}")
        
        result = await resp.json()
        new_quantity = result.get("quantity", 0)
        _LOGGER.info("Successfully adjusted drink quantity for %s (new quantity: %s)", date_str, new_quantity)
        return True, new_quantity


async def log_drink_free_day(coordinator, date):
    """Log a drink-free day to Drinkaware."""
    # Convert date to ISO format string
    date_str = date.strftime("%Y-%m-%d")
    
    # Based on MITM logs, for drink-free day we need to PUT to the day endpoint
    url = f"{API_BASE_URL}/tracking/v1/activity/{date_str}/drinkfreeday"
    
    headers = {
        "Authorization": f"Bearer {coordinator.access_token}",
        "Accept": "application/json",
    }
    
    async with coordinator.session.put(url, headers=headers) as resp:
        if resp.status != 200 and resp.status != 204:
            text = await resp.text()
            _LOGGER.error("Error logging drink-free day: %s - %s", resp.status, text)
            raise Exception(f"Failed to log drink-free day: {resp.status} - {text}")
        
        _LOGGER.info("Successfully logged drink-free day for %s", date_str)
        return True


async def remove_drink_free_day(coordinator, date):
    """Remove a drink-free day marking from Drinkaware."""
    # Convert date to ISO format string
    date_str = date.strftime("%Y-%m-%d")
    
    # Based on MITM logs, for removing a drink-free day we use DELETE
    url = f"{API_BASE_URL}/tracking/v1/activity/{date_str}/drinkfreeday"
    
    headers = {
        "Authorization": f"Bearer {coordinator.access_token}",
        "Accept": "application/json",
    }
    
    async with coordinator.session.delete(url, headers=headers) as resp:
        if resp.status != 200 and resp.status != 204:
            text = await resp.text()
            _LOGGER.error("Error removing drink-free day: %s - %s", resp.status, text)
            raise Exception(f"Failed to remove drink-free day: {resp.status} - {text}")
        
        _LOGGER.info("Successfully removed drink-free day for %s", date_str)
        return True


async def log_sleep_quality(coordinator, quality, date):
    """Log sleep quality to Drinkaware."""
    # Convert date to ISO format string
    date_str = date.strftime("%Y-%m-%d")
    
    # For logging sleep quality we use PUT to the sleep endpoint
    url = f"{API_BASE_URL}/tracking/v1/activity/{date_str}/sleep"
    
    headers = {
        "Authorization": f"Bearer {coordinator.access_token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    
    # The payload for logging sleep quality
    payload = {
        "quality": quality
    }
    
    async with coordinator.session.put(url, headers=headers, json=payload) as resp:
        if resp.status != 200 and resp.status != 204:
            text = await resp.text()
            _LOGGER.error("Error logging sleep quality: %s - %s", resp.status, text)
            raise Exception(f"Failed to log sleep quality: {resp.status} - {text}")
        
        _LOGGER.info("Successfully logged sleep quality for %s", date_str)
        return True