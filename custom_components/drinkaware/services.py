"""
Services for Drinkaware integration.
"""
import logging
import asyncio
from datetime import datetime
import voluptuous as vol

from homeassistant.core import HomeAssistant
from homeassistant.const import ATTR_DATE
from homeassistant.exceptions import HomeAssistantError

from .const import (
    DOMAIN,
    API_BASE_URL,
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
)

from .drink_constants import (
    DEFAULT_ABV_VALUES,
    MEASURE_DESCRIPTIONS,
)

from .dynamic_services import (
    async_get_drink_free_day_schema,
    async_get_log_drink_schema,
    async_get_delete_drink_schema,
    async_get_remove_drink_free_day_schema,
    async_get_log_sleep_quality_schema,
    async_get_refresh_schema,
)

_LOGGER = logging.getLogger(__name__)


def validate_entry_id(value):
    """Validate that entry_id is provided."""
    if ATTR_ENTRY_ID not in value or not value[ATTR_ENTRY_ID]:
        raise vol.Invalid("Config Entry ID must be provided")

    # Remove account_name if it was provided (for backward compatibility)
    if "account_name" in value:
        value.pop("account_name")

    return value


def get_coordinator_by_entry_id(hass, entry_id):
    """Get coordinator by entry_id."""
    if entry_id and entry_id in hass.data[DOMAIN]:
        coordinator = hass.data[DOMAIN][entry_id]
        return coordinator

    # If we have only one entry and no specific entry_id was provided, return that
    if not entry_id:
        entries = [
            entry_id for entry_id in hass.data[DOMAIN]
            if entry_id != "account_name_map"
        ]
        if len(entries) == 1:
            coordinator = hass.data[DOMAIN][entries[0]]
            return coordinator

    return None


async def async_setup_services(hass: HomeAssistant) -> None:
    """Set up services for Drinkaware integration."""

    async def async_log_drink_free_day(service_call) -> None:
        """Log a drink-free day to Drinkaware."""
        entry_id = service_call.data.get(ATTR_ENTRY_ID)
        date = service_call.data.get(ATTR_DATE, datetime.now().date())
        remove_drinks = service_call.data.get("remove_drinks", False)

        coordinator = get_coordinator_by_entry_id(hass, entry_id)
        if not coordinator:
            raise HomeAssistantError(
                "No matching Drinkaware integration found. Please specify a valid config entry ID."
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
                _LOGGER.info(
                    f"Attempting to remove all drinks for {date_str} before marking as drink-free"
                )

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

                    # Handle different possible formats in the response
                    drinks = []
                    if "activity" in activity and activity["activity"]:
                        drinks = activity["activity"]
                    elif "drinks" in activity and activity["drinks"]:
                        drinks = activity["drinks"]

                    _LOGGER.info(f"Found {len(drinks)} drinks to remove")

                    if not drinks:
                        _LOGGER.warning("No drinks found in API response, but summary indicates drinks exist")

                    # Remove each drink individually
                    for drink in drinks:
                        drink_id = drink.get("drinkId")
                        measure_id = drink.get("measureId")
                        drink_name = drink.get("name", "Unknown")

                        if drink_id and measure_id:
                            _LOGGER.info(f"Removing {drink_name} from {date_str}")
                            try:
                                # Use DELETE to completely remove the drink
                                delete_url = (
                                    f"{API_BASE_URL}/tracking/v1/activity/{date_str}/{drink_id}/{measure_id}"
                                )
                                async with coordinator.session.delete(delete_url, headers=headers) as del_resp:
                                    if del_resp.status not in (200, 204):
                                        text = await del_resp.text()
                                        _LOGGER.warning(
                                            f"Error removing drink {drink_name}: {del_resp.status} - {text}"
                                        )
                                    else:
                                        _LOGGER.info(f"Successfully removed {drink_name}")

                                # Add a small delay to prevent rate limiting
                                await asyncio.sleep(0.5)  # Increased delay to ensure request completes
                            except Exception as err:
                                _LOGGER.warning(f"Exception removing drink {drink_name}: {err}")

                # Wait a bit to ensure all deletes are processed
                await asyncio.sleep(1.0)

                # Verify all drinks were removed
                async with coordinator.session.get(url, headers=headers) as verify_resp:
                    if verify_resp.status == 200:
                        verify_data = await verify_resp.json()

                        remaining_drinks = []
                        if "activity" in verify_data and verify_data["activity"]:
                            remaining_drinks = verify_data["activity"]
                        elif "drinks" in verify_data and verify_data["drinks"]:
                            remaining_drinks = verify_data["drinks"]

                        if remaining_drinks:
                            _LOGGER.warning(f"Still {len(remaining_drinks)} drinks remaining after removal")
                            # If there are still drinks, skip setting drink-free day
                            raise HomeAssistantError("Could not remove all drinks. Please try again.")
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
                    raise HomeAssistantError(
                        f"Failed to log drink-free day: {resp.status} - {text}"
                    )

                _LOGGER.info(f"Successfully marked {date_str} as drink-free")

            # Final refresh to update the sensors with new data
            await coordinator.async_refresh()
        except Exception as err:
            _LOGGER.error(f"Error logging drink-free day: {err}")
            raise HomeAssistantError(f"Error logging drink-free day: {err}")

    async def async_log_drink(service_call) -> None:
        """Log a drink to Drinkaware."""
        entry_id = service_call.data.get(ATTR_ENTRY_ID)

        # Get the inferred drink type selector from validation
        drink_type_selector = service_call.data.get("drink_type_selector", "standard")

        # Determine which drink ID to use based on the inferred selector
        if drink_type_selector == "standard":
            # Get drink ID from the dropdown
            drink_type = service_call.data.get(ATTR_DRINK_TYPE)
            if not drink_type:
                raise HomeAssistantError(
                    "No standard drink type selected. Please select a drink from the dropdown."
                )
        else:  # custom
            # Get drink ID from the custom input
            drink_type = service_call.data.get("custom_drink_id")
            if not drink_type:
                raise HomeAssistantError(
                    "No custom drink ID provided. Please enter a valid drink ID."
                )

        # Get measure ID
        drink_measure = service_call.data.get(ATTR_DRINK_MEASURE)
        if not drink_measure:
            raise HomeAssistantError("You must specify a measure_id")

        # Get other parameters
        abv = service_call.data.get(ATTR_DRINK_ABV)
        custom_name = service_call.data.get("name")  # Get optional custom name
        quantity = service_call.data.get(ATTR_DRINK_QUANTITY, 1)  # Default to 1 if not specified
        date = service_call.data.get(ATTR_DATE, datetime.now().date())
        auto_remove_dfd = service_call.data.get("auto_remove_dfd", False)  # Default to False

        coordinator = get_coordinator_by_entry_id(hass, entry_id)
        if not coordinator:
            raise HomeAssistantError(
                "No matching Drinkaware integration found. Please specify a valid config entry ID."
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
                        drinks = []

                        # Handle different possible response formats
                        if "activity" in activity and activity["activity"]:
                            drinks = activity["activity"]
                        elif "drinks" in activity and activity["drinks"]:
                            drinks = activity["drinks"]

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

            # Check if ABV is specified and if it differs from the default
            create_custom = False
            if abv is not None:
                # Only create a custom drink if the ABV differs from the default
                default_abv = DEFAULT_ABV_VALUES.get(drink_type)
                if default_abv is not None and abs(default_abv - abv) > 0.01:
                    create_custom = True
                    _LOGGER.info(
                        f"Creating custom drink: custom ABV {abv}% differs from default {default_abv}%"
                    )
                else:
                    _LOGGER.info(
                        f"Using standard drink: custom ABV {abv}% is the same as default {default_abv}%"
                    )
                    abv = None  # Don't create custom drink if ABV matches default

            if should_increment:
                # Use POST with quantityAdjustment to add a drink
                await add_drink(
                    coordinator, drink_type, drink_measure, abv if create_custom else None, date, custom_name
                )
                _LOGGER.info("Added 1 drink using quantityAdjustment")

                # If quantity > 1, add additional drinks
                for _ in range(1, quantity):
                    await add_drink(
                        coordinator, drink_type, drink_measure, abv if create_custom else None, date, custom_name
                    )
                    _LOGGER.info("Added additional drink")
            else:
                # Use PUT with quantity to set an absolute value
                await set_drink_quantity(
                    coordinator, drink_type, drink_measure, abv if create_custom else None, quantity, date, custom_name
                )
                _LOGGER.info(f"Set drink quantity to {quantity}")

            # Trigger refresh to update the sensors with new data
            await coordinator.async_refresh()
        except Exception as err:
            _LOGGER.error(f"Error logging drink: {err}")
            raise HomeAssistantError(f"Error logging drink: {err}")

    async def async_delete_drink(service_call) -> None:
        """Delete a drink from Drinkaware."""
        entry_id = service_call.data.get(ATTR_ENTRY_ID)

        # Get the inferred drink type selector from validation
        drink_type_selector = service_call.data.get("drink_type_selector", "standard")

        # Determine which drink ID to use based on the inferred selector
        if drink_type_selector == "standard":
            # Get drink ID from the dropdown
            drink_type = service_call.data.get(ATTR_DRINK_TYPE)
            if not drink_type:
                raise HomeAssistantError(
                    "No standard drink type selected. Please select a drink from the dropdown."
                )
        else:  # custom
            # Get drink ID from the custom input
            drink_type = service_call.data.get("custom_drink_id")
            if not drink_type:
                raise HomeAssistantError(
                    "No custom drink ID provided. Please enter a valid drink ID."
                )

        drink_measure = service_call.data[ATTR_DRINK_MEASURE]
        date = service_call.data.get(ATTR_DATE, datetime.now().date())

        coordinator = get_coordinator_by_entry_id(hass, entry_id)
        if not coordinator:
            raise HomeAssistantError(
                "No matching Drinkaware integration found. Please specify a valid config entry ID."
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
                    drinks = []

                    if "activity" in activity and activity["activity"]:
                        drinks = activity["activity"]
                    elif "drinks" in activity and activity["drinks"]:
                        drinks = activity["drinks"]

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
        date = service_call.data.get(ATTR_DATE, datetime.now().date())

        coordinator = get_coordinator_by_entry_id(hass, entry_id)
        if not coordinator:
            raise HomeAssistantError(
                "No matching Drinkaware integration found. Please specify a valid config entry ID."
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
        quality = service_call.data[ATTR_SLEEP_QUALITY]
        date = service_call.data.get(ATTR_DATE, datetime.now().date())

        coordinator = get_coordinator_by_entry_id(hass, entry_id)
        if not coordinator:
            raise HomeAssistantError(
                "No matching Drinkaware integration found. Please specify a valid config entry ID."
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

        # If no entry ID is specified, refresh all accounts
        if not entry_id:
            refresh_tasks = []
            for entry_id, coordinator in hass.data[DOMAIN].items():
                if entry_id == "account_name_map":
                    continue  # Skip the mapping dictionary
                refresh_tasks.append(coordinator.async_refresh())

            if refresh_tasks:
                _LOGGER.info("Refreshing data for all Drinkaware accounts")
                await asyncio.gather(*refresh_tasks, return_exceptions=True)
                _LOGGER.info("Refreshed all Drinkaware accounts")
            return

        # Otherwise, refresh the specified account
        coordinator = get_coordinator_by_entry_id(hass, entry_id)
        if not coordinator:
            raise HomeAssistantError(
                "No matching Drinkaware integration found. Please specify a valid config entry ID."
            )

        try:
            await coordinator.async_refresh()
            _LOGGER.info("Drinkaware data for %s refreshed successfully", coordinator.account_name)
        except Exception as err:
            _LOGGER.error("Error refreshing Drinkaware data: %s", err)
            raise HomeAssistantError(f"Error refreshing Drinkaware data: {err}")

    # Register services with validation
    drink_free_day_schema = vol.Schema(vol.All(
        async_get_drink_free_day_schema(hass),
        validate_entry_id
    ))

    log_drink_schema = vol.Schema(vol.All(
        async_get_log_drink_schema(hass),
        validate_entry_id
    ))

    delete_drink_schema = vol.Schema(vol.All(
        async_get_delete_drink_schema(hass),
        validate_entry_id
    ))

    remove_drink_free_day_schema = vol.Schema(vol.All(
        async_get_remove_drink_free_day_schema(hass),
        validate_entry_id
    ))

    log_sleep_quality_schema = vol.Schema(vol.All(
        async_get_log_sleep_quality_schema(hass),
        validate_entry_id
    ))

    refresh_schema = vol.Schema(
        async_get_refresh_schema(hass)
    )

    # Register services
    hass.services.async_register(
        DOMAIN,
        SERVICE_LOG_DRINK_FREE_DAY,
        async_log_drink_free_day,
        schema=drink_free_day_schema,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_LOG_DRINK,
        async_log_drink,
        schema=log_drink_schema,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_DELETE_DRINK,
        async_delete_drink,
        schema=delete_drink_schema,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_REMOVE_DRINK_FREE_DAY,
        async_remove_drink_free_day,
        schema=remove_drink_free_day_schema,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_LOG_SLEEP_QUALITY,
        async_log_sleep_quality,
        schema=log_sleep_quality_schema,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_REFRESH,
        async_refresh,
        schema=refresh_schema,
    )


async def async_unload_services(hass: HomeAssistant) -> None:
    """Unload Drinkaware services."""
    hass.services.async_remove(DOMAIN, SERVICE_LOG_DRINK_FREE_DAY)
    hass.services.async_remove(DOMAIN, SERVICE_LOG_DRINK)
    hass.services.async_remove(DOMAIN, SERVICE_DELETE_DRINK)
    hass.services.async_remove(DOMAIN, SERVICE_REMOVE_DRINK_FREE_DAY)
    hass.services.async_remove(DOMAIN, SERVICE_LOG_SLEEP_QUALITY)
    hass.services.async_remove(DOMAIN, SERVICE_REFRESH)


async def create_custom_drink(coordinator, drink_type, title, abv):
    """Create a custom drink with a specific ABV."""
    url = f"{API_BASE_URL}/drinks/v1/custom"

    headers = {
        "Authorization": f"Bearer {coordinator.access_token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    payload = {
        "derivedDrinkId": drink_type,
        "title": title,
        "abv": abv
    }

    try:
        async with coordinator.session.post(url, headers=headers, json=payload) as resp:
            if resp.status != 200:
                text = await resp.text()
                _LOGGER.error(f"Error creating custom drink: {resp.status} - {text}")
                raise Exception(f"Failed to create custom drink: {resp.status} - {text}")

            result = await resp.json()
            _LOGGER.info(f"Successfully created custom drink with ID: {result.get('drinkId')}")

            # Store measure descriptions for this custom drink
            try:
                # Extract measure information from the response
                custom_measures = result.get("measures", [])
                for measure in custom_measures:
                    measure_id = measure.get("measureId")
                    measure_title = measure.get("title")
                    # If the API returned a title for this measure, we'll use it
                    if measure_id and measure_title:
                        # We could update a global cache here if needed
                        pass
                    # Otherwise use our pre-defined descriptions
                    elif measure_id and measure_id in MEASURE_DESCRIPTIONS:
                        # We could log this for debugging
                        _LOGGER.debug(
                            f"Using predefined description for measure {measure_id}: "
                            f"{MEASURE_DESCRIPTIONS[measure_id]}"
                        )
            except Exception as err:
                _LOGGER.debug(f"Error processing measure descriptions: {err}")

            # Update the drinks cache with the new custom drink
            if not hasattr(coordinator, 'drinks_cache'):
                coordinator.drinks_cache = {}

            if "customDrinks" not in coordinator.drinks_cache:
                coordinator.drinks_cache["customDrinks"] = []

            # Check if this drink already exists in the cache
            existing_drink = False
            for i, drink in enumerate(coordinator.drinks_cache.get("customDrinks", [])):
                if drink.get("drinkId") == result.get("drinkId"):
                    # Update existing drink in the cache
                    coordinator.drinks_cache["customDrinks"][i] = result
                    existing_drink = True
                    break

            # If not found, add the new custom drink to the cache
            if not existing_drink:
                coordinator.drinks_cache["customDrinks"].append(result)

            _LOGGER.debug(f"Updated drinks cache with custom drink: {title} ({abv}% ABV)")

            return result.get("drinkId")
    except Exception as err:
        _LOGGER.error(f"Exception creating custom drink: {str(err)}")
        raise


async def add_drink(coordinator, drink_type, drink_measure, abv, date, custom_name=None):
    """Add a single drink to Drinkaware using quantityAdjustment."""
    date_str = date.strftime("%Y-%m-%d")

    # If custom ABV specified, create a custom drink first
    if abv:
        try:
            # Get original drink info to get the title
            # For simplicity, we'll use the drink_type as the title if we can't find the original
            title = custom_name if custom_name else "Custom Drink"
            if not custom_name and hasattr(coordinator, 'drinks_cache') and coordinator.drinks_cache:
                # Look in categories first
                if "categories" in coordinator.drinks_cache:
                    for category in coordinator.drinks_cache.get("categories", []):
                        for drink in category.get("drinks", []):
                            if drink.get("drinkId") == drink_type:
                                title = drink.get("title", "Custom Drink")
                                break
                # Also check customDrinks if present
                if "customDrinks" in coordinator.drinks_cache:
                    for drink in coordinator.drinks_cache.get("customDrinks", []):
                        if drink.get("drinkId") == drink_type:
                            title = drink.get("title", "Custom Drink")
                            break

            # Create custom drink
            custom_drink_id = await create_custom_drink(coordinator, drink_type, title, abv)
            # Use the custom drink ID instead of the original
            drink_type = custom_drink_id
        except Exception as err:
            _LOGGER.warning(
                f"Failed to create custom drink with ABV {abv}, using standard drink: {str(err)}"
            )

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

    async with coordinator.session.post(url, headers=headers, json=payload) as resp:
        if resp.status not in (200, 204):
            text = await resp.text()
            _LOGGER.error(f"Error adding drink: {resp.status} - {text}")
            raise Exception(f"Failed to add drink: {resp.status} - {text}")

        result = await resp.json()
        _LOGGER.info(f"Successfully added drink for {date_str} (new quantity: {result.get('quantity', 0)})")
        return True, result.get("quantity", 0)


async def set_drink_quantity(coordinator, drink_type, drink_measure, abv, quantity, date, custom_name=None):
    """Set the absolute quantity of a drink type for a specific day."""
    date_str = date.strftime("%Y-%m-%d")

    # If custom ABV specified, create a custom drink first
    if abv:
        try:
            # Get original drink info to get the title
            # For simplicity, we'll use the drink_type as the title if we can't find the original
            title = custom_name if custom_name else "Custom Drink"
            if not custom_name and hasattr(coordinator, 'drinks_cache') and coordinator.drinks_cache:
                # Check in categories
                if "categories" in coordinator.drinks_cache:
                    for category in coordinator.drinks_cache.get("categories", []):
                        for drink in category.get("drinks", []):
                            if drink.get("drinkId") == drink_type:
                                title = drink.get("title", "Custom Drink")
                                break
                # Also check customDrinks if present
                if "customDrinks" in coordinator.drinks_cache:
                    for drink in coordinator.drinks_cache.get("customDrinks", []):
                        if drink.get("drinkId") == drink_type:
                            title = drink.get("title", "Custom Drink")
                            break

            # Create custom drink
            custom_drink_id = await create_custom_drink(coordinator, drink_type, title, abv)
            # Use the custom drink ID instead of the original
            drink_type = custom_drink_id
        except Exception as err:
            _LOGGER.warning(
                f"Failed to create custom drink with ABV {abv}, using standard drink: {str(err)}"
            )

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