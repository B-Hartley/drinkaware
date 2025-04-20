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

# Mapping of drink types to compatible measure types
DRINK_MEASURE_COMPATIBILITY = {
    # Beer/Lager/Ale
    "FAB60DBF-911F-4286-9C3E-0F0BCB40E3B7": [  # Lager
        "B59DCD68-96FF-4B4C-BA69-3707D085C407",  # Pint
        "174F45D7-745A-45F0-9D44-88DA1075CE79",  # Half pint
        "6B56A1FB-33A1-4E51-BED7-536751DE56BC",  # Small bottle/can (330ml)
        "0CB11B53-6E3C-4C47-A2E9-68BA40DFFE13",  # Bottle/can (440ml)
        "8F185B18-2A82-4D1A-A1F7-20E01D5E2FEC",  # Bottle (500ml)
        "03D87F35-A1DF-40EE-9398-FA1CA55DD894",  # Large bottle (660ml)
    ],
    "D4F06BD4-1F61-468B-AE86-C6CC2D56E021": [  # Beer
        "B59DCD68-96FF-4B4C-BA69-3707D085C407",  # Pint
        "174F45D7-745A-45F0-9D44-88DA1075CE79",  # Half pint
        "6B56A1FB-33A1-4E51-BED7-536751DE56BC",  # Small bottle/can (330ml)
        "0CB11B53-6E3C-4C47-A2E9-68BA40DFFE13",  # Bottle/can (440ml)
        "8F185B18-2A82-4D1A-A1F7-20E01D5E2FEC",  # Bottle (500ml)
        "03D87F35-A1DF-40EE-9398-FA1CA55DD894",  # Large bottle (660ml)
    ],
    "1F8DF28A-5F05-470E-833B-06C499965C99": [  # Ale/stout
        "B59DCD68-96FF-4B4C-BA69-3707D085C407",  # Pint
        "174F45D7-745A-45F0-9D44-88DA1075CE79",  # Half pint
        "6B56A1FB-33A1-4E51-BED7-536751DE56BC",  # Small bottle/can (330ml)
        "0CB11B53-6E3C-4C47-A2E9-68BA40DFFE13",  # Bottle/can (440ml)
        "8F185B18-2A82-4D1A-A1F7-20E01D5E2FEC",  # Bottle (500ml)
        "03D87F35-A1DF-40EE-9398-FA1CA55DD894",  # Large bottle (660ml)
    ],
    # Wine
    "E3DEDBFD-63CE-492D-8E3E-9C24010227D8": [  # White Wine
        "0E40AE5F-098D-4826-ADCA-298A6A14F514",  # Small wine glass (125ml)
        "E586C800-24CA-4942-837A-4CD2CBF8338A",  # Medium wine glass (175ml)
        "6450132A-F73F-414A-83BB-43C37B40272F",  # Large wine glass (250ml)
    ],
    "19E82B28-9AD5-4546-A966-13B27EC6E4FB": [  # Red Wine
        "0E40AE5F-098D-4826-ADCA-298A6A14F514",  # Small wine glass (125ml)
        "E586C800-24CA-4942-837A-4CD2CBF8338A",  # Medium wine glass (175ml)
        "6450132A-F73F-414A-83BB-43C37B40272F",  # Large wine glass (250ml)
    ],
    "FA3B43D0-A418-4F4D-8FC1-218E8DA81918": [  # Rosé Wine
        "0E40AE5F-098D-4826-ADCA-298A6A14F514",  # Small wine glass (125ml)
        "E586C800-24CA-4942-837A-4CD2CBF8338A",  # Medium wine glass (175ml)
        "6450132A-F73F-414A-83BB-43C37B40272F",  # Large wine glass (250ml)
    ],
    # Champagne/Prosecco
    "61C3F476-24D1-46DB-9FA0-613ED4082531": [  # Champagne
        "B6CFC69E-0E85-4F82-A109-155801BB7C79",  # Champagne glass (125ml)
        "A8B1FA3D-25A2-4685-92E9-DE9D19407CE3",  # Medium champagne glass (187ml)
    ],
    "5184149E-450E-4A63-92E5-19AD7F49FCD1": [  # Prosecco
        "B6CFC69E-0E85-4F82-A109-155801BB7C79",  # Champagne glass (125ml)
        "A8B1FA3D-25A2-4685-92E9-DE9D19407CE3",  # Medium champagne glass (187ml)
    ],
    # Spirits
    "0E3CA732-21D6-4631-A60C-155C2BB85C18": [  # Vodka
        "A83406D4-741F-49B4-B310-8B7DEB8B072F",  # Single spirit measure (25ml)
        "FCCC81A2-3BFF-45C0-832F-BCF73E81D0D1",  # Double spirit measure (50ml)
    ],
    "FECCEBB8-68D1-4BF1-B42F-7BB6C919B0F0": [  # Gin
        "A83406D4-741F-49B4-B310-8B7DEB8B072F",  # Single spirit measure (25ml)
        "FCCC81A2-3BFF-45C0-832F-BCF73E81D0D1",  # Double spirit measure (50ml)
    ],
    "32B22A73-D900-43E1-AAB6-8ADC27590B5D": [  # Tequila
        "A83406D4-741F-49B4-B310-8B7DEB8B072F",  # Single spirit measure (25ml)
        "FCCC81A2-3BFF-45C0-832F-BCF73E81D0D1",  # Double spirit measure (50ml)
    ],
    "780B45E2-26D6-4F55-A0C1-75868835D672": [  # Rum
        "A83406D4-741F-49B4-B310-8B7DEB8B072F",  # Single spirit measure (25ml)
        "FCCC81A2-3BFF-45C0-832F-BCF73E81D0D1",  # Double spirit measure (50ml)
    ],
    "2AAE4A2E-8C0A-40E1-BCDE-EB986111D2DE": [  # Whisk(e)y
        "A83406D4-741F-49B4-B310-8B7DEB8B072F",  # Single spirit measure (25ml)
        "FCCC81A2-3BFF-45C0-832F-BCF73E81D0D1",  # Double spirit measure (50ml)
    ],
    "E473445D-2B75-47DA-9978-24C80093B1D0": [  # Brandy
        "A83406D4-741F-49B4-B310-8B7DEB8B072F",  # Single spirit measure (25ml)
        "FCCC81A2-3BFF-45C0-832F-BCF73E81D0D1",  # Double spirit measure (50ml)
    ],
    "300546E3-DB89-49DC-B4B5-8ED96EB18C12": [  # Other Spirit
        "A83406D4-741F-49B4-B310-8B7DEB8B072F",  # Single spirit measure (25ml)
        "FCCC81A2-3BFF-45C0-832F-BCF73E81D0D1",  # Double spirit measure (50ml)
    ],
    # Port/Sherry
    "F8486573-6F92-4B63-BAEB-3E76B750E14D": [  # Port/Sherry
        "021703DD-248C-4A51-ACFD-0CE97540C8EC",  # Small port/sherry glass (75ml)
    ],
    # Cider
    "61AD633A-7366-4497-BD36-9078466F00FE": [  # Cider
        "B59DCD68-96FF-4B4C-BA69-3707D085C407",  # Pint
        "174F45D7-745A-45F0-9D44-88DA1075CE79",  # Half pint
        "6B56A1FB-33A1-4E51-BED7-536751DE56BC",  # Small bottle/can (330ml)
        "0CB11B53-6E3C-4C47-A2E9-68BA40DFFE13",  # Bottle/can (440ml)
        "8F185B18-2A82-4D1A-A1F7-20E01D5E2FEC",  # Bottle (500ml)
    ],
    # Alcopop
    "0B2A65CA-5EC4-46B6-9E4D-6E0DDC8D57B8": [  # Alcopop
        "6B56A1FB-33A1-4E51-BED7-536751DE56BC",  # Small bottle/can (330ml)
    ],
}

# Mapping of default ABV values for standard drinks
DEFAULT_ABV_VALUES = {
    "FAB60DBF-911F-4286-9C3E-0F0BCB40E3B7": 4.0,  # Lager
    "D4F06BD4-1F61-468B-AE86-C6CC2D56E021": 5.0,  # Beer
    "1F8DF28A-5F05-470E-833B-06C499965C99": 4.5,  # Ale/stout
    "E3DEDBFD-63CE-492D-8E3E-9C24010227D8": 13.0,  # White Wine
    "19E82B28-9AD5-4546-A966-13B27EC6E4FB": 13.0,  # Red Wine
    "FA3B43D0-A418-4F4D-8FC1-218E8DA81918": 13.0,  # Rosé Wine
    "61C3F476-24D1-46DB-9FA0-613ED4082531": 12.0,  # Champagne
    "5184149E-450E-4A63-92E5-19AD7F49FCD1": 12.0,  # Prosecco
    "0E3CA732-21D6-4631-A60C-155C2BB85C18": 40.0,  # Vodka
    "FECCEBB8-68D1-4BF1-B42F-7BB6C919B0F0": 40.0,  # Gin
    "32B22A73-D900-43E1-AAB6-8ADC27590B5D": 50.0,  # Tequila
    "780B45E2-26D6-4F55-A0C1-75868835D672": 40.0,  # Rum
    "2AAE4A2E-8C0A-40E1-BCDE-EB986111D2DE": 40.0,  # Whisk(e)y
    "E473445D-2B75-47DA-9978-24C80093B1D0": 40.0,  # Brandy
    "300546E3-DB89-49DC-B4B5-8ED96EB18C12": 40.0,  # Other Spirit
    "F8486573-6F92-4B63-BAEB-3E76B750E14D": 18.0,  # Port/Sherry
    "61AD633A-7366-4497-BD36-9078466F00FE": 4.5,  # Cider
    "0B2A65CA-5EC4-46B6-9E4D-6E0DDC8D57B8": 4.0,  # Alcopop
}

@callback
def async_get_first_account_name(hass: HomeAssistant) -> str:
    """Get the first configured account name."""
    for entry_id, coordinator in hass.data[DOMAIN].items():
        if entry_id == "account_name_map":
            continue
        if hasattr(coordinator, 'account_name'):
            return coordinator.account_name
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
            
            # Add custom drinks - check both customDrinks and any other locations
            if "customDrinks" in coordinator.drinks_cache:
                for drink in coordinator.drinks_cache["customDrinks"]:
                    custom_drinks.append(drink)
                    
            # API might also return custom drinks directly in the drinks array
            if "drinks" in coordinator.drinks_cache:
                for drink in coordinator.drinks_cache["drinks"]:
                    # If it's not already in our standard drinks
                    if drink.get("drinkId") not in drinks_data:
                        custom_drinks.append(drink)
    
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
        if drink_id:
            drink_options.append({
                "value": drink_id,
                "label": f"{title} ({abv}% ABV) - Custom"
            })
    
    # Add "Custom" option at the end
    drink_options.append({
        "value": "custom",
        "label": "Custom Drink (Enter ID directly)"
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
        {"value": "B59DCD68-96FF-4B4C-BA69-3707D085C407", "label": "Pint (568ml)"},
        {"value": "174F45D7-745A-45F0-9D44-88DA1075CE79", "label": "Half pint (284ml)"},
        {"value": "6B56A1FB-33A1-4E51-BED7-536751DE56BC", "label": "Small bottle/can (330ml)"},
        {"value": "0CB11B53-6E3C-4C47-A2E9-68BA40DFFE13", "label": "Bottle/can (440ml)"},
        {"value": "8F185B18-2A82-4D1A-A1F7-20E01D5E2FEC", "label": "Bottle (500ml)"},
        {"value": "03D87F35-A1DF-40EE-9398-FA1CA55DD894", "label": "Large bottle (660ml)"},
        {"value": "0E40AE5F-098D-4826-ADCA-298A6A14F514", "label": "Small wine glass (125ml)"},
        {"value": "E586C800-24CA-4942-837A-4CD2CBF8338A", "label": "Medium wine glass (175ml)"},
        {"value": "6450132A-F73F-414A-83BB-43C37B40272F", "label": "Large wine glass (250ml)"},
        {"value": "B6CFC69E-0E85-4F82-A109-155801BB7C79", "label": "Champagne glass (125ml)"},
        {"value": "A8B1FA3D-25A2-4685-92E9-DE9D19407CE3", "label": "Medium champagne glass (187ml)"},
        {"value": "A83406D4-741F-49B4-B310-8B7DEB8B072F", "label": "Single spirit measure (25ml)"},
        {"value": "FCCC81A2-3BFF-45C0-832F-BCF73E81D0D1", "label": "Double spirit measure (50ml)"},
        {"value": "021703DD-248C-4A51-ACFD-0CE97540C8EC", "label": "Small port/sherry glass (75ml)"},
    ]
    
    # Filter measures by compatibility
    for measure in all_measures:
        if measure["value"] in compatible_measure_ids:
            measure_options.append(measure)
    
    # Add custom option
    measure_options.append({
        "value": "custom",
        "label": "Custom Measure (Enter ID directly)"
    })
    
    return measure_options

@callback
def async_get_drink_free_day_schema(hass: HomeAssistant):
    """Get schema for drink free day service."""
    first_account = async_get_first_account_name(hass)
    
    schema_dict = {
        vol.Required(ATTR_ACCOUNT_NAME, default=first_account): cv.string,
        vol.Optional(ATTR_ENTRY_ID): cv.string,
        vol.Optional(ATTR_DATE): cv.date,
        vol.Optional("remove_drinks", default=False): cv.boolean,
    }
    return schema_dict

@callback
def async_get_remove_drink_free_day_schema(hass: HomeAssistant):
    """Get schema for remove drink free day service."""
    first_account = async_get_first_account_name(hass)
    
    schema_dict = {
        vol.Required(ATTR_ACCOUNT_NAME, default=first_account): cv.string,
        vol.Optional(ATTR_ENTRY_ID): cv.string,
        vol.Optional(ATTR_DATE): cv.date,
    }
    return schema_dict

@callback
def async_get_log_sleep_quality_schema(hass: HomeAssistant):
    """Get schema for log sleep quality service."""
    first_account = async_get_first_account_name(hass)
    
    schema_dict = {
        vol.Required(ATTR_ACCOUNT_NAME, default=first_account): cv.string,
        vol.Optional(ATTR_ENTRY_ID): cv.string,
        vol.Required(ATTR_SLEEP_QUALITY): vol.In(["poor", "average", "great"]),
        vol.Optional(ATTR_DATE): cv.date,
    }
    return schema_dict

@callback
def async_get_refresh_schema(hass: HomeAssistant):
    """Get schema for refresh service."""
    schema_dict = {
        vol.Optional(ATTR_ACCOUNT_NAME): cv.string,
        vol.Optional(ATTR_ENTRY_ID): cv.string,
    }
    return schema_dict

@callback
def async_get_log_drink_schema(hass: HomeAssistant):
    """Get schema for log drink service."""
    first_account = async_get_first_account_name(hass)
    drink_options = async_get_available_drinks(hass)
    
    # Create schema with dynamic options if available
    schema_dict = {
        vol.Required(ATTR_ACCOUNT_NAME, default=first_account): cv.string,
        vol.Optional(ATTR_ENTRY_ID): cv.string,
        vol.Required(ATTR_DRINK_TYPE): cv.string,
        vol.Required(ATTR_DRINK_MEASURE): cv.string,
        vol.Optional(ATTR_DRINK_ABV): vol.Coerce(float),
        vol.Optional(ATTR_DRINK_QUANTITY): vol.Coerce(int),
        vol.Optional(ATTR_DATE): cv.date,
        vol.Optional("auto_remove_dfd", default=False): cv.boolean,
    }
    
    return schema_dict

@callback
def async_get_delete_drink_schema(hass: HomeAssistant):
    """Get schema for delete drink service."""
    first_account = async_get_first_account_name(hass)
    drink_options = async_get_available_drinks(hass)
    
    # Create schema with dynamic options if available
    schema_dict = {
        vol.Required(ATTR_ACCOUNT_NAME, default=first_account): cv.string,
        vol.Optional(ATTR_ENTRY_ID): cv.string,
        vol.Required(ATTR_DRINK_TYPE): cv.string,
        vol.Required(ATTR_DRINK_MEASURE): cv.string,
        vol.Optional(ATTR_DATE): cv.date,
    }
    
    return schema_dict