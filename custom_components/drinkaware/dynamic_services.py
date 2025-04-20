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

_LOGGER = logging.getLogger(__name__)

@callback
def async_get_drink_free_day_schema(hass: HomeAssistant):
    """Get schema for drink free day service."""
    schema_dict = {
        vol.Optional(ATTR_ENTRY_ID): cv.string,
        vol.Optional(ATTR_ACCOUNT_NAME): cv.string,
        vol.Optional(ATTR_DATE): cv.date,
        vol.Optional("remove_drinks", default=False): cv.boolean,
    }
    return schema_dict

@callback
def async_get_remove_drink_free_day_schema(hass: HomeAssistant):
    """Get schema for remove drink free day service."""
    schema_dict = {
        vol.Optional(ATTR_ENTRY_ID): cv.string,
        vol.Optional(ATTR_ACCOUNT_NAME): cv.string,
        vol.Optional(ATTR_DATE): cv.date,
    }
    return schema_dict

@callback
def async_get_log_sleep_quality_schema(hass: HomeAssistant):
    """Get schema for log sleep quality service."""
    schema_dict = {
        vol.Optional(ATTR_ENTRY_ID): cv.string,
        vol.Optional(ATTR_ACCOUNT_NAME): cv.string,
        vol.Required(ATTR_SLEEP_QUALITY): vol.In(["poor", "average", "great"]),
        vol.Optional(ATTR_DATE): cv.date,
    }
    return schema_dict

@callback
def async_get_refresh_schema(hass: HomeAssistant):
    """Get schema for refresh service."""
    schema_dict = {
        vol.Optional(ATTR_ENTRY_ID): cv.string,
        vol.Optional(ATTR_ACCOUNT_NAME): cv.string,
    }
    return schema_dict

@callback
def async_get_log_drink_schema(hass: HomeAssistant):
    """Get schema for log drink service."""
    # We'll defer the dynamic options fetching to the services.yaml 
    # The dynamic options will be handled in the services.py file when processing the service call
    
    # This will use the static options from services.yaml but allow any string value
    # which gives us the flexibility to accept both dropdown selections and custom values
    schema_dict = {
        vol.Optional(ATTR_ENTRY_ID): cv.string,
        vol.Optional(ATTR_ACCOUNT_NAME): cv.string,
        vol.Required(ATTR_DRINK_TYPE): cv.string,
        vol.Required(ATTR_DRINK_MEASURE): cv.string,
        vol.Optional(ATTR_DRINK_ABV, default=0): vol.Coerce(float),
        vol.Optional(ATTR_DRINK_QUANTITY, default=1): vol.Coerce(int),
        vol.Optional(ATTR_DATE): cv.date,
        vol.Optional("auto_remove_dfd", default=False): cv.boolean,
    }
    return schema_dict

@callback
def async_get_delete_drink_schema(hass: HomeAssistant):
    """Get schema for delete drink service."""
    # Use simple string validation to allow for either dropdown selection or custom entry
    schema_dict = {
        vol.Optional(ATTR_ENTRY_ID): cv.string,
        vol.Optional(ATTR_ACCOUNT_NAME): cv.string,
        vol.Required(ATTR_DRINK_TYPE): cv.string,
        vol.Required(ATTR_DRINK_MEASURE): cv.string,
        vol.Optional(ATTR_DATE): cv.date,
    }
    return schema_dict