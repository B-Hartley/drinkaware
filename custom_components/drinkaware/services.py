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
    vol.Optional("remove_drinks", default=False): cv.boolean,
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
            # First refresh to get the latest data
            _LOGGER.info("Refreshing data before setting drink-free day")
            await coordinator.async_refresh()
            
            # Check if there are already drinks for this day
            has_drinks = False
            date_str = date.strftime("%Y-%m-%d")
            
            # Check existing drinks in the API data
            if coordinator.data and "summary" in coordinator.data:
                for day_data in coordinator.data["summary"]:
                    if day_data.get("date") == date_str and day_data.get("drinks", 0) > 0:
                        has_drinks = True
                        drink_count = day_data.get("drinks", 0)
                        _LOGGER.info(f"Found {drink_count} drinks for {date_str}")
                        break
            
            # If we have drinks and should remove them
            if has_drinks and remove_drinks:
                _LOGGER.info(f"Attempting to remove all drinks for {date_str} before marking as drink-free")
                
                # Get detailed information about what drinks are logged for the day
                url = f"{API_BASE_URL}/tracking/v1/activity/{date_str}"
                headers = {
                    "Authorization": f"Bearer {coordinator.access_token}",
                    "Accept": "application/json",
                }
                
                async with coordinator.session.get(url, headers=headers) as resp:
                    if resp.status != 200:
                        text = await resp.text()
                        _LOGGER.error(f"Error retrieving drinks for {date_str}: {resp.status} - {text}")
                        raise HomeAssistantError(f"Failed to retrieve drinks: {text}")
                    
                    activity = await resp.json()
                    drinks = activity.get("drinks", [])
                    _LOGGER.info(f"Found {len(drinks)} drinks to remove")
                    
                    # Remove each drink individually
                    for drink in drinks:
                        drink_id = drink.get("drinkId")
                        measure_id = drink.get("measureId")
                        drink_name = drink.get("drinkName", "Unknown")
                        
                        if drink_id and measure_id:
                            _LOGGER.info(f"Removing {drink_name} from {date_str}")
                            try:
                                # Use DELETE to completely remove the drink
                                delete_url = f"{API_BASE_URL}/tracking/v1/activity/{date_str}/{drink_id}/{measure_id}"
                                async with coordinator.session.delete(delete_url, headers=headers) as del_resp:
                                    if del_resp.status not in (200, 204):
                                        text = await del_resp.text()
                                        _LOGGER.warning(f"Error removing drink {drink_name}: {del_resp.status} - {text}")
                                    else:
                                        _LOGGER.info(f"Successfully removed {drink_name}")
                            except Exception as err:
                                _LOGGER.warning(f"Exception removing drink {drink_name}: {err}")
                
                # Verify all drinks were removed
                async with coordinator.session.get(url, headers=headers) as verify_resp:
                    if verify_resp.status == 200:
                        verify_data = await verify_resp.json()
                        remaining_drinks = verify_data.get("drinks", [])
                        
                        if remaining_drinks:
                            _LOGGER.warning(f"Still {len(remaining_drinks)} drinks remaining after removal")
                            raise HomeAssistantError(f"Could not remove all drinks for {date_str}. Please try again or remove drinks manually.")
                        else:
                            _LOGGER.info(f"Successfully verified all drinks removed for {date_str}")
            
            # Now try to log the drink-free day
            url = f"{API_BASE_URL}/tracking/v1/activity/{date_str}/drinkfreeday"
            headers = {
                "Authorization": f"Bearer {coordinator.access_token}",
                "Accept": "application/json",
            }
            
            async with coordinator.session.put(url, headers=headers) as resp:
                if resp.status not in (200, 204):
                    text = await resp.text()
                    _LOGGER.error(f"Error logging drink-free day: {resp.status} - {text}")
                    raise HomeAssistantError(f"Failed to log drink-free day: {resp.status} - {text}")
                
                _LOGGER.info(f"Successfully marked {date_str} as drink-free")
            
            # Final refresh to update the sensors with new data
            await coordinator.async_refresh()
        except Exception as err:
            _LOGGER.error(f"Error logging drink-free day: {err}")
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
            # If auto_remove_dfd is True, check if day is marked as drink-free and remove that mark first
            if auto_remove_dfd:
                try:
                    await remove_drink_free_day(coordinator, date)
                    _LOGGER.info("Automatically removed drink-free day flag before adding drink")
                except Exception as err:
                    # If removing the drink-free day fails, it probably wasn't set, so we can ignore the error
                    _LOGGER.debug(f"Day was not marked as drink-free or error removing: {err}")
            
            # Check if we're adding drinks or setting an exact quantity
            should_increment = True
            
            if quantity == 1:
                # For quantity=1, we might be adding a drink or setting it to exactly 1
                # Let's check if this drink already exists
                date_str = date.strftime("%Y-%m-%d")
                url = f"{API_BASE_URL}/tracking/v1/activity/{date_str}"
                
                headers = {
                    "Authorization": f"Bearer {coordinator.access_token}",
                    "Accept": "application/json",
                }
                
                async with coordinator.session.get(url, headers=headers) as resp:
                    if resp.status == 200:
                        activity = await resp.json()
                        drinks = activity.get("drinks", [])
                        
                        # Check if this drink type and measure already exists
                        for drink in drinks:
                            if (drink.get("drinkId") == drink_type and 
                                drink.get("measureId") == drink_measure):
                                # Already exists, so we should increment
                                should_increment = True
                                break
            elif quantity > 1:
                # If quantity > 1, we're explicitly setting a quantity
                should_increment = False
                
            if should_increment:
                # Use POST with quantityAdjustment to add a drink
                await add_drink(coordinator, drink_type, drink_measure, abv, date)
                _LOGGER.info(f"Added 1 drink using quantityAdjustment")
                
                # If quantity > 1, add additional drinks
                for _ in range(1, quantity):
                    await add_drink(coordinator, drink_type, drink_measure, abv, date)
                    _LOGGER.info(f"Added additional drink")
            else:
                # Use PUT with quantity to set an absolute value
                await set_drink_quantity(coordinator, drink_type, drink_measure, abv, quantity, date)
                _LOGGER.info(f"Set drink quantity to {quantity}")
            
            # Trigger refresh to update the sensors with new data
            await coordinator.async_refresh()
        except Exception as err:
            _LOGGER.error(f"Error logging drink: {err}")
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
            # First check if this drink exists and get its current quantity
            date_str = date.strftime("%Y-%m-%d")
            url = f"{API_BASE_URL}/tracking/v1/activity/{date_str}"
            
            headers = {
                "Authorization": f"Bearer {coordinator.access_token}",
                "Accept": "application/json",
            }
            
            current_quantity = 0
            drink_name = "Unknown Drink"
            
            async with coordinator.session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    activity = await resp.json()
                    drinks = activity.get("drinks", [])
                    
                    for drink in drinks:
                        if (drink.get("drinkId") == drink_type and 
                            drink.get("measureId") == drink_measure):
                            current_quantity = drink.get("quantity", 0)
                            drink_name = drink.get("name", "Unknown Drink")
                            break
            
            if current_quantity == 0:
                _LOGGER.warning(f"No drink of type {drink_type} found for {date_str}")
                raise HomeAssistantError(f"No matching drink found for {date_str}")
            
            # Delete the drink
            delete_url = f"{API_BASE_URL}/tracking/v1/activity/{date_str}/{drink_type}/{drink_measure}"
            
            async with coordinator.session.delete(delete_url, headers=headers) as resp:
                if resp.status not in (200, 204):
                    text = await resp.text()
                    _LOGGER.error(f"Error deleting drink: {resp.status} - {text}")
                    raise HomeAssistantError(f"Failed to delete drink: {resp.status} - {text}")
                
                _LOGGER.info(f"Successfully deleted {current_quantity}x {drink_name} for {date_str}")
            
            # Trigger refresh to update the sensors with new data
            await coordinator.async_refresh()
        except Exception as err:
            _LOGGER.error(f"Error deleting drink: {err}")
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


async def add_drink(coordinator, drink_type, drink_measure, abv, date):
    """Add a single drink to Drinkaware using quantityAdjustment."""
    date_str = date.strftime("%Y-%m-%d")
    
    url = f"{API_BASE_URL}/tracking/v1/activity/{date_str}"
    
    headers = {
        "Authorization": f"Bearer {coordinator.access_token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    
    # The payload for incrementing a drink - use POST with quantityAdjustment
    payload = {
        "drinkId": drink_type,
        "measureId": drink_measure,
        "quantityAdjustment": 1  # Add one drink
    }
    
    # If user provided a custom ABV, include it
    if abv > 0:
        payload["abv"] = abv
    
    async with coordinator.session.post(url, headers=headers, json=payload) as resp:
        if resp.status not in (200, 204):
            text = await resp.text()
            _LOGGER.error(f"Error adding drink: {resp.status} - {text}")
            raise Exception(f"Failed to add drink: {resp.status} - {text}")
        
        result = await resp.json()
        _LOGGER.info(f"Successfully added drink for {date_str} (new quantity: {result.get('quantity', 0)})")
        return True, result.get("quantity", 0)

async def set_drink_quantity(coordinator, drink_type, drink_measure, abv, quantity, date):
    """Set the absolute quantity of a drink type for a specific day."""
    date_str = date.strftime("%Y-%m-%d")
    
    url = f"{API_BASE_URL}/tracking/v1/activity/{date_str}"
    
    headers = {
        "Authorization": f"Bearer {coordinator.access_token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    
    # The payload for setting a drink quantity - use PUT with quantity
    payload = {
        "drinkId": drink_type,
        "measureId": drink_measure,
        "quantity": quantity  # Set absolute quantity
    }
    
    # If user provided a custom ABV, include it
    if abv > 0:
        payload["abv"] = abv
    
    async with coordinator.session.put(url, headers=headers, json=payload) as resp:
        if resp.status not in (200, 204):
            text = await resp.text()
            _LOGGER.error(f"Error setting drink quantity: {resp.status} - {text}")
            raise Exception(f"Failed to set drink quantity: {resp.status} - {text}")
        
        result = await resp.json()
        _LOGGER.info(f"Successfully set drink quantity for {date_str} to {result.get('quantity', 0)}")
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
        if resp.status not in (200, 204):
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
        if resp.status not in (200, 204):
            text = await resp.text()
            _LOGGER.error("Error logging sleep quality: %s - %s", resp.status, text)
            raise Exception(f"Failed to log sleep quality: {resp.status} - {text}")
        
        _LOGGER.info("Successfully logged sleep quality for %s", date_str)
        return True