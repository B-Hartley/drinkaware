"""
Utility functions for Drinkaware integration.
"""
import logging
from datetime import datetime

_LOGGER = logging.getLogger(__name__)

def get_entry_id_by_account_name(hass, account_name):
    """Get entry_id for a given account name."""
    # Check if we have an account name mapping
    if "account_name_map" not in hass.data["drinkaware"]:
        hass.data["drinkaware"]["account_name_map"] = {}
        
    # First check the mapping cache
    if account_name.lower() in hass.data["drinkaware"]["account_name_map"]:
        return hass.data["drinkaware"]["account_name_map"][account_name.lower()]
        
    # If not in cache, search through all entries
    for entry_id, coordinator in hass.data["drinkaware"].items():
        if entry_id == "account_name_map":
            continue  # Skip the mapping dictionary
        if hasattr(coordinator, 'account_name') and coordinator.account_name.lower() == account_name.lower():
            # Add to the mapping for future lookups
            hass.data["drinkaware"]["account_name_map"][account_name.lower()] = entry_id
            return entry_id
            
    # Not found
    return None

def get_default_account_name(hass):
    """Get the default account name to use for service calls.
        
    for entry_id, coordinator in hass.data["drinkaware"].items():
        if entry_id == "account_name_map":
            continue
        if hasattr(coordinator, 'account_name'):
            return coordinator.account_name
    
    return none
