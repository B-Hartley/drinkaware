"""
This is a placeholder file to add the mock function needed for testing.
Add this at the bottom of your custom_components/drinkaware/__init__.py file.
"""

# Add this function to the bottom of your __init__.py file for testing compatibility
async def async_forward_entry_setups(hass, config_entry, platforms):
    """Mock function for compatibility with older Home Assistant versions."""
    # In newer HA versions, this function exists in config_entries.py
    # In older versions, we need to add it to the integration code
    for platform in platforms:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(config_entry, platform)
        )
    return True