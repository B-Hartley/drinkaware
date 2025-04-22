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

def update_last_used_account(account_name):
    """Update the last used account name."""
    global _LAST_USED_ACCOUNT
    _LAST_USED_ACCOUNT["name"] = account_name
    _LAST_USED_ACCOUNT["timestamp"] = datetime.now()

def get_default_account_name(hass):
    """Get the default account name to use for service calls.
    
    First tries the most recently used account, then falls back
    to the first configured account if necessary.
    """
    # Check if we have a recent account
    if _LAST_USED_ACCOUNT["name"] is not None:
        # Verify the account still exists
        entry_id = get_entry_id_by_account_name(hass, _LAST_USED_ACCOUNT["name"])
        if entry_id:
            return _LAST_USED_ACCOUNT["name"]
    
    # If no recent account or it doesn't exist anymore, return the first one
    for entry_id, coordinator in hass.data["drinkaware"].items():
        if entry_id == "account_name_map":
            continue
        if hasattr(coordinator, 'account_name'):
            return coordinator.account_name
    
    return ""
