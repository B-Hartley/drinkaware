"""
Dynamic service schema for Drinkaware integration.
"""
import logging
import voluptuous as vol
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import config_validation as cv
from homeassistant.const import ATTR_DATE, CONF_NAME

from .const import (
    DOMAIN,
    ATTR_ENTRY_ID,
    ATTR_ACCOUNT_NAME,
    ATTR_DRINK_TYPE,
    ATTR_DRINK_MEASURE,
    ATTR_DRINK_ABV,
    ATTR_DRINK_QUANTITY,
    ATTR_SLEEP_QUALITY,
)

from .drink_constants import (
    DEFAULT_ABV_VALUES,
    DRINK_MEASURE_COMPATIBILITY,
    MEASURE_DESCRIPTIONS,
    DRINK_NAMES,
)

_LOGGER = logging.getLogger(__name__)

@callback
def async_get_first_config_entry(hass: HomeAssistant) -> str:
    """Get the first available config entry ID."""
    entries = [
        entry_id for entry_id in hass.data[DOMAIN]
        if entry_id != "account_name_map"
    ]
    if entries:
        return entries[0]
    return ""

@callback
def async_get_available_drinks(hass: HomeAssistant):
    """Get all available drinks from all accounts."""
    drinks_data = {}
    custom_drinks = []

    # First gather drinks data from all accounts
    for entry_id, coordinator in hass.data[DOMAIN].items():
        if entry_id == "account_name_map":
            continue

        if hasattr(coordinator, 'drinks_cache') and coordinator.drinks_cache:
            # Combine standard drinks
            if "categories" in coordinator.drinks_cache:
                for category in coordinator.drinks_cache["categories"]:
                    for drink in category.get("drinks", []):
                        drink_id = drink.get("drinkId")
                        if drink_id:
                            drinks_data[drink_id] = drink

            # Add custom drinks from search results
            if "drinks" in coordinator.drinks_cache:
                for drink in coordinator.drinks_cache["drinks"]:
                    if "derivedDrinkId" in drink:
                        # This is likely a custom drink
                        custom_drinks.append({
                            **drink,
                            "account_name": coordinator.account_name
                        })

            # Also check the customDrinks array if it exists
            if "customDrinks" in coordinator.drinks_cache:
                for drink in coordinator.drinks_cache["customDrinks"]:
                    custom_drinks.append({
                        **drink,
                        "account_name": coordinator.account_name
                    })

            # Also check results array which is present in search results
            if "results" in coordinator.drinks_cache:
                for drink in coordinator.drinks_cache["results"]:
                    if "derivedDrinkId" in drink:
                        custom_drinks.append({
                            **drink,
                            "account_name": coordinator.account_name
                        })

    # Compile drink options
    drink_options = []

    # Add standard drinks first
    for drink_id, drink in sorted(drinks_data.items(), key=lambda x: x[1].get("title", "")):
        abv = drink.get("abv", 0)
        title = drink.get("title", "Unknown Drink")
        drink_options.append({
            "value": drink_id,
            "label": f"{title} ({abv}% ABV)"
        })

    # Then add any custom drinks
    for drink in sorted(custom_drinks, key=lambda x: x.get("title", "")):
        drink_id = drink.get("drinkId")
        abv = drink.get("abv", 0)
        title = drink.get("title", "Custom Drink")
        account_name = drink.get("account_name", "Unknown")

        if drink_id:
            drink_options.append({
                "value": drink_id,
                "label": f"{title} ({abv}% ABV) - Custom [{account_name}]"
            })

    return drink_options

@callback
def async_get_compatible_measures(hass: HomeAssistant, drink_id):
    """Get compatible measures for a specific drink."""
    # Get the list of compatible measure IDs for this drink
    compatible_measure_ids = DRINK_MEASURE_COMPATIBILITY.get(drink_id, [])

    # If we don't have specific compatibility info, return all measures
    if not compatible_measure_ids:
        return None  # Return None to use the default complete list

    # Create a list of all available measures
    measure_options = []

    # Define all known measures
    all_measures = [
        {"value": measure_id, "label": desc}
        for measure_id, desc in MEASURE_DESCRIPTIONS.items()
    ]

    # Filter measures by compatibility
    for measure in all_measures:
        if measure["value"] in compatible_measure_ids:
            measure_options.append(measure)

    return measure_options

@callback
def async_get_drink_free_day_schema(hass: HomeAssistant):
    """Get schema for drink free day service."""
    first_entry = async_get_first_config_entry(hass)

    schema_dict = {
        vol.Required(ATTR_ENTRY_ID, default=first_entry): cv.string,
        vol.Optional(ATTR_DATE): cv.date,
        vol.Optional("remove_drinks", default=False): cv.boolean,
    }
    return schema_dict

@callback
def async_get_remove_drink_free_day_schema(hass: HomeAssistant):
    """Get schema for remove drink free day service."""
    first_entry = async_get_first_config_entry(hass)

    schema_dict = {
        vol.Required(ATTR_ENTRY_ID, default=first_entry): cv.string,
        vol.Optional(ATTR_DATE): cv.date,
    }
    return schema_dict

@callback
def async_get_log_sleep_quality_schema(hass: HomeAssistant):
    """Get schema for log sleep quality service."""
    first_entry = async_get_first_config_entry(hass)

    schema_dict = {
        vol.Required(ATTR_ENTRY_ID, default=first_entry): cv.string,
        vol.Required(ATTR_SLEEP_QUALITY): vol.In(["poor", "average", "great"]),
        vol.Optional(ATTR_DATE): cv.date,
    }
    return schema_dict

@callback
def async_get_refresh_schema(hass: HomeAssistant):
    """Get schema for refresh service."""
    first_entry = async_get_first_config_entry(hass)

    schema_dict = {
        vol.Optional(ATTR_ENTRY_ID, default=first_entry): cv.string,
    }
    return schema_dict

@callback
def async_get_log_drink_schema(hass: HomeAssistant):
    """Get schema for log drink service."""
    first_entry = async_get_first_config_entry(hass)

    # Create schema with dynamic options if available
    schema_dict = {
        vol.Required(ATTR_ENTRY_ID, default=first_entry): cv.string,
        # Remove the drink_type_selector, we'll infer from provided fields
        vol.Optional(ATTR_DRINK_TYPE): cv.string,
        vol.Optional("custom_drink_id"): cv.string,
        vol.Required(ATTR_DRINK_MEASURE): cv.string,
        vol.Optional(ATTR_DRINK_ABV): vol.Coerce(float),
        vol.Optional("name"): cv.string,  # Add optional custom name parameter
        vol.Optional(ATTR_DRINK_QUANTITY): vol.Coerce(int),
        vol.Optional(ATTR_DATE): cv.date,
        vol.Optional("auto_remove_dfd", default=False): cv.boolean,
    }

    # Updated validator to infer which type based on provided fields
    def validate_drink_id_inputs(value):
        """Infer drink type and validate inputs."""
        has_standard = ATTR_DRINK_TYPE in value and value[ATTR_DRINK_TYPE]
        has_custom = "custom_drink_id" in value and value["custom_drink_id"]

        # Auto-determine which type we're using
        if has_standard and not has_custom:
            # Using standard drink
            value["drink_type_selector"] = "standard"
        elif has_custom and not has_standard:
            # Using custom drink
            value["drink_type_selector"] = "custom"
        elif has_standard and has_custom:
            # Both provided, standard takes precedence
            value["drink_type_selector"] = "standard"
            del value["custom_drink_id"]
        else:
            # Neither provided
            raise vol.Invalid("Either standard drink type or custom drink ID must be provided")

        return value

    # Return the schema with validation
    return vol.Schema(vol.All(schema_dict, validate_drink_id_inputs, validate_drink_measure_compatibility))

@callback
def async_get_delete_drink_schema(hass: HomeAssistant):
    """Get schema for delete drink service."""
    first_entry = async_get_first_config_entry(hass)

    # Create schema with dynamic options if available
    schema_dict = {
        vol.Required(ATTR_ENTRY_ID, default=first_entry): cv.string,
        # Remove the drink_type_selector, we'll infer from provided fields
        vol.Optional(ATTR_DRINK_TYPE): cv.string,
        vol.Optional("custom_drink_id"): cv.string,
        vol.Required(ATTR_DRINK_MEASURE): cv.string,
        vol.Optional(ATTR_DATE): cv.date,
    }

    # Updated validator to infer which type based on provided fields
    def validate_drink_id_inputs(value):
        """Infer drink type and validate inputs."""
        has_standard = ATTR_DRINK_TYPE in value and value[ATTR_DRINK_TYPE]
        has_custom = "custom_drink_id" in value and value["custom_drink_id"]

        # Auto-determine which type we're using
        if has_standard and not has_custom:
            # Using standard drink
            value["drink_type_selector"] = "standard"
        elif has_custom and not has_standard:
            # Using custom drink
            value["drink_type_selector"] = "custom"
        elif has_standard and has_custom:
            # Both provided, standard takes precedence
            value["drink_type_selector"] = "standard"
            del value["custom_drink_id"]
        else:
            # Neither provided
            raise vol.Invalid("Either standard drink type or custom drink ID must be provided")

        return value

    # Return the schema with validation
    return vol.Schema(vol.All(schema_dict, validate_drink_id_inputs, validate_drink_measure_compatibility))

def validate_drink_measure_compatibility(value):
    """Validate that the drink and measure types are compatible."""
    # Determine which drink ID to use
    drink_id = None
    if value.get("drink_type_selector") == "standard":
        drink_id = value.get(ATTR_DRINK_TYPE)
    else:
        # For custom drinks, skip compatibility validation
        return value

    measure_id = value.get(ATTR_DRINK_MEASURE)

    # Skip validation if either is not provided
    if not drink_id or not measure_id:
        return value

    # Get compatible measure IDs for this drink
    compatible_measure_ids = DRINK_MEASURE_COMPATIBILITY.get(drink_id, [])

    # If we don't have compatibility info for this drink, assume it's compatible
    if not compatible_measure_ids:
        return value

    # Check if the measure is compatible
    if measure_id not in compatible_measure_ids:
        # Get human-readable measure description
        measure_description = MEASURE_DESCRIPTIONS.get(measure_id, "Unknown measure")

        # Get human-readable drink name
        drink_name = DRINK_NAMES.get(drink_id, "Unknown drink")

        # Get a list of compatible measure descriptions
        compatible_measures = []
        for m_id in compatible_measure_ids:
            if m_id in MEASURE_DESCRIPTIONS:
                compatible_measures.append(MEASURE_DESCRIPTIONS[m_id])
            else:
                compatible_measures.append(m_id)

        # Format the error message
        error_msg = f"Incompatible drink and measure combination: {drink_name} cannot be served in {measure_description}. "
        if compatible_measures:
            error_msg += f"Compatible measures for {drink_name} are: {', '.join(compatible_measures)}"

        raise vol.Invalid(error_msg)

    return value
