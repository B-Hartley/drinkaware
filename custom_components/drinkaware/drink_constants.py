"""
Constants related to drinks for the Drinkaware integration.
"""

# Drink IDs
DRINK_ID_LAGER = "FAB60DBF-911F-4286-9C3E-0F0BCB40E3B7"
DRINK_ID_BEER = "D4F06BD4-1F61-468B-AE86-C6CC2D56E021"
DRINK_ID_ALE_STOUT = "1F8DF28A-5F05-470E-833B-06C499965C99"
DRINK_ID_WHITE_WINE = "E3DEDBFD-63CE-492D-8E3E-9C24010227D8"
DRINK_ID_RED_WINE = "19E82B28-9AD5-4546-A966-13B27EC6E4FB"
DRINK_ID_ROSE_WINE = "FA3B43D0-A418-4F4D-8FC1-218E8DA81918"
DRINK_ID_CHAMPAGNE = "61C3F476-24D1-46DB-9FA0-613ED4082531"
DRINK_ID_PROSECCO = "5184149E-450E-4A63-92E5-19AD7F49FCD1"
DRINK_ID_VODKA = "0E3CA732-21D6-4631-A60C-155C2BB85C18"
DRINK_ID_GIN = "FECCEBB8-68D1-4BF1-B42F-7BB6C919B0F0"
DRINK_ID_TEQUILA = "32B22A73-D900-43E1-AAB6-8ADC27590B5D"
DRINK_ID_RUM = "780B45E2-26D6-4F55-A0C1-75868835D672"
DRINK_ID_WHISKEY = "2AAE4A2E-8C0A-40E1-BCDE-EB986111D2DE"
DRINK_ID_BRANDY = "E473445D-2B75-47DA-9978-24C80093B1D0"
DRINK_ID_OTHER_SPIRIT = "300546E3-DB89-49DC-B4B5-8ED96EB18C12"
DRINK_ID_PORT_SHERRY = "F8486573-6F92-4B63-BAEB-3E76B750E14D"
DRINK_ID_CIDER = "61AD633A-7366-4497-BD36-9078466F00FE"
DRINK_ID_ALCOPOP = "0B2A65CA-5EC4-46B6-9E4D-6E0DDC8D57B8"

# Measure IDs
MEASURE_ID_PINT = "B59DCD68-96FF-4B4C-BA69-3707D085C407"
MEASURE_ID_HALF_PINT = "174F45D7-745A-45F0-9D44-88DA1075CE79"
MEASURE_ID_SMALL_BOTTLE = "6B56A1FB-33A1-4E51-BED7-536751DE56BC"
MEASURE_ID_MEDIUM_BOTTLE = "0CB11B53-6E3C-4C47-A2E9-68BA40DFFE13"
MEASURE_ID_LARGE_BOTTLE = "8F185B18-2A82-4D1A-A1F7-20E01D5E2FEC"
MEASURE_ID_EXTRA_LARGE_BOTTLE = "03D87F35-A1DF-40EE-9398-FA1CA55DD894"
MEASURE_ID_SMALL_WINE = "0E40AE5F-098D-4826-ADCA-298A6A14F514"
MEASURE_ID_MEDIUM_WINE = "E586C800-24CA-4942-837A-4CD2CBF8338A"
MEASURE_ID_LARGE_WINE = "6450132A-F73F-414A-83BB-43C37B40272F"
MEASURE_ID_CHAMPAGNE = "B6CFC69E-0E85-4F82-A109-155801BB7C79"
MEASURE_ID_MEDIUM_CHAMPAGNE = "A8B1FA3D-25A2-4685-92E9-DE9D19407CE3"
MEASURE_ID_SINGLE_SPIRIT = "A83406D4-741F-49B4-B310-8B7DEB8B072F"
MEASURE_ID_DOUBLE_SPIRIT = "FCCC81A2-3BFF-45C0-832F-BCF73E81D0D1"
MEASURE_ID_PORT_SHERRY = "021703DD-248C-4A51-ACFD-0CE97540C8EC"

# Human-readable drink names
DRINK_NAMES = {
    DRINK_ID_LAGER: "Lager",
    DRINK_ID_BEER: "Beer",
    DRINK_ID_ALE_STOUT: "Ale/stout",
    DRINK_ID_WHITE_WINE: "White Wine",
    DRINK_ID_RED_WINE: "Red Wine",
    DRINK_ID_ROSE_WINE: "Rosé Wine",
    DRINK_ID_CHAMPAGNE: "Champagne",
    DRINK_ID_PROSECCO: "Prosecco",
    DRINK_ID_VODKA: "Vodka",
    DRINK_ID_GIN: "Gin",
    DRINK_ID_TEQUILA: "Tequila",
    DRINK_ID_RUM: "Rum",
    DRINK_ID_WHISKEY: "Whisk(e)y",
    DRINK_ID_BRANDY: "Brandy",
    DRINK_ID_OTHER_SPIRIT: "Other Spirit",
    DRINK_ID_PORT_SHERRY: "Port/Sherry",
    DRINK_ID_CIDER: "Cider",
    DRINK_ID_ALCOPOP: "Alcopop",
}

# Default ABV values for standard drinks
DEFAULT_ABV_VALUES = {
    DRINK_ID_LAGER: 4.0,
    DRINK_ID_BEER: 5.0,
    DRINK_ID_ALE_STOUT: 4.5,
    DRINK_ID_WHITE_WINE: 13.0,
    DRINK_ID_RED_WINE: 13.0,
    DRINK_ID_ROSE_WINE: 13.0,
    DRINK_ID_CHAMPAGNE: 12.0,
    DRINK_ID_PROSECCO: 12.0,
    DRINK_ID_VODKA: 40.0,
    DRINK_ID_GIN: 40.0,
    DRINK_ID_TEQUILA: 50.0,
    DRINK_ID_RUM: 40.0,
    DRINK_ID_WHISKEY: 40.0,
    DRINK_ID_BRANDY: 40.0,
    DRINK_ID_OTHER_SPIRIT: 40.0,
    DRINK_ID_PORT_SHERRY: 18.0,
    DRINK_ID_CIDER: 4.5,
    DRINK_ID_ALCOPOP: 4.0,
}

# Measure descriptions with volume amounts
MEASURE_DESCRIPTIONS = {
    MEASURE_ID_PINT: "Pint (568ml)",
    MEASURE_ID_HALF_PINT: "Half pint (284ml)",
    MEASURE_ID_SMALL_BOTTLE: "Small bottle/can (330ml)",
    MEASURE_ID_MEDIUM_BOTTLE: "Bottle/can (440ml)",
    MEASURE_ID_LARGE_BOTTLE: "Bottle (500ml)",
    MEASURE_ID_EXTRA_LARGE_BOTTLE: "Large bottle (660ml)",
    MEASURE_ID_SMALL_WINE: "Small wine glass (125ml)",
    MEASURE_ID_MEDIUM_WINE: "Medium wine glass (175ml)",
    MEASURE_ID_LARGE_WINE: "Large wine glass (250ml)",
    MEASURE_ID_CHAMPAGNE: "Champagne glass (125ml)",
    MEASURE_ID_MEDIUM_CHAMPAGNE: "Medium champagne glass (187ml)",
    MEASURE_ID_SINGLE_SPIRIT: "Single spirit measure (25ml)",
    MEASURE_ID_DOUBLE_SPIRIT: "Double spirit measure (50ml)",
    MEASURE_ID_PORT_SHERRY: "Small port/sherry glass (75ml)",
}

# Mapping of drink types to compatible measure types
DRINK_MEASURE_COMPATIBILITY = {
    # Beer/Lager/Ale
    DRINK_ID_LAGER: [
        MEASURE_ID_PINT,
        MEASURE_ID_HALF_PINT,
        MEASURE_ID_SMALL_BOTTLE,
        MEASURE_ID_MEDIUM_BOTTLE,
        MEASURE_ID_LARGE_BOTTLE,
        MEASURE_ID_EXTRA_LARGE_BOTTLE,
    ],
    DRINK_ID_BEER: [
        MEASURE_ID_PINT,
        MEASURE_ID_HALF_PINT,
        MEASURE_ID_SMALL_BOTTLE,
        MEASURE_ID_MEDIUM_BOTTLE,
        MEASURE_ID_LARGE_BOTTLE,
        MEASURE_ID_EXTRA_LARGE_BOTTLE,
    ],
    DRINK_ID_ALE_STOUT: [
        MEASURE_ID_PINT,
        MEASURE_ID_HALF_PINT,
        MEASURE_ID_SMALL_BOTTLE,
        MEASURE_ID_MEDIUM_BOTTLE,
        MEASURE_ID_LARGE_BOTTLE,
        MEASURE_ID_EXTRA_LARGE_BOTTLE,
    ],
    # Wine
    DRINK_ID_WHITE_WINE: [
        MEASURE_ID_SMALL_WINE,
        MEASURE_ID_MEDIUM_WINE,
        MEASURE_ID_LARGE_WINE,
    ],
    DRINK_ID_RED_WINE: [
        MEASURE_ID_SMALL_WINE,
        MEASURE_ID_MEDIUM_WINE,
        MEASURE_ID_LARGE_WINE,
    ],
    DRINK_ID_ROSE_WINE: [
        MEASURE_ID_SMALL_WINE,
        MEASURE_ID_MEDIUM_WINE,
        MEASURE_ID_LARGE_WINE,
    ],
    # Champagne/Prosecco
    DRINK_ID_CHAMPAGNE: [
        MEASURE_ID_CHAMPAGNE,
        MEASURE_ID_MEDIUM_CHAMPAGNE,
    ],
    DRINK_ID_PROSECCO: [
        MEASURE_ID_CHAMPAGNE,
        MEASURE_ID_MEDIUM_CHAMPAGNE,
    ],
    # Spirits
    DRINK_ID_VODKA: [
        MEASURE_ID_SINGLE_SPIRIT,
        MEASURE_ID_DOUBLE_SPIRIT,
    ],
    DRINK_ID_GIN: [
        MEASURE_ID_SINGLE_SPIRIT,
        MEASURE_ID_DOUBLE_SPIRIT,
    ],
    DRINK_ID_TEQUILA: [
        MEASURE_ID_SINGLE_SPIRIT,
        MEASURE_ID_DOUBLE_SPIRIT,
    ],
    DRINK_ID_RUM: [
        MEASURE_ID_SINGLE_SPIRIT,
        MEASURE_ID_DOUBLE_SPIRIT,
    ],
    DRINK_ID_WHISKEY: [
        MEASURE_ID_SINGLE_SPIRIT,
        MEASURE_ID_DOUBLE_SPIRIT,
    ],
    DRINK_ID_BRANDY: [
        MEASURE_ID_SINGLE_SPIRIT,
        MEASURE_ID_DOUBLE_SPIRIT,
    ],
    DRINK_ID_OTHER_SPIRIT: [
        MEASURE_ID_SINGLE_SPIRIT,
        MEASURE_ID_DOUBLE_SPIRIT,
    ],
    # Port/Sherry
    DRINK_ID_PORT_SHERRY: [
        MEASURE_ID_PORT_SHERRY,
    ],
    # Cider
    DRINK_ID_CIDER: [
        MEASURE_ID_PINT,
        MEASURE_ID_HALF_PINT,
        MEASURE_ID_SMALL_BOTTLE,
        MEASURE_ID_MEDIUM_BOTTLE,
        MEASURE_ID_LARGE_BOTTLE,
    ],
    # Alcopop
    DRINK_ID_ALCOPOP: [
        MEASURE_ID_SMALL_BOTTLE,
    ],
}

# Options for service schema drink selection
DRINK_OPTIONS = [
    {"label": f"Lager (4.0% ABV)", "value": DRINK_ID_LAGER},
    {"label": f"Beer (5.0% ABV)", "value": DRINK_ID_BEER},
    {"label": f"Ale/stout (4.5% ABV)", "value": DRINK_ID_ALE_STOUT},
    {"label": f"White Wine (13.0% ABV)", "value": DRINK_ID_WHITE_WINE},
    {"label": f"Red Wine (13.0% ABV)", "value": DRINK_ID_RED_WINE},
    {"label": f"Rosé Wine (13.0% ABV)", "value": DRINK_ID_ROSE_WINE},
    {"label": f"Champagne (12.0% ABV)", "value": DRINK_ID_CHAMPAGNE},
    {"label": f"Prosecco (12.0% ABV)", "value": DRINK_ID_PROSECCO},
    {"label": f"Vodka (40.0% ABV)", "value": DRINK_ID_VODKA},
    {"label": f"Gin (40.0% ABV)", "value": DRINK_ID_GIN},
    {"label": f"Tequila (50.0% ABV)", "value": DRINK_ID_TEQUILA},
    {"label": f"Rum (40.0% ABV)", "value": DRINK_ID_RUM},
    {"label": f"Whisk(e)y (40.0% ABV)", "value": DRINK_ID_WHISKEY},
    {"label": f"Brandy (40.0% ABV)", "value": DRINK_ID_BRANDY},
    {"label": f"Other Spirit (40.0% ABV)", "value": DRINK_ID_OTHER_SPIRIT},
    {"label": f"Port/Sherry (18.0% ABV)", "value": DRINK_ID_PORT_SHERRY},
    {"label": f"Cider (4.5% ABV)", "value": DRINK_ID_CIDER},
    {"label": f"Alcopop (4.0% ABV)", "value": DRINK_ID_ALCOPOP},
    {"label": "Custom Drink ID", "value": "custom"},
]

# Options for service schema measure selection
MEASURE_OPTIONS = [
    {"label": "Pint (568ml) - For beer, lager, ale, cider", "value": MEASURE_ID_PINT},
    {"label": "Half pint (284ml) - For beer, lager, ale, cider", "value": MEASURE_ID_HALF_PINT},
    {"label": "Small bottle/can (330ml) - For beer, lager, ale, cider, alcopop", "value": MEASURE_ID_SMALL_BOTTLE},
    {"label": "Bottle/can (440ml) - For beer, lager, ale, cider", "value": MEASURE_ID_MEDIUM_BOTTLE},
    {"label": "Bottle (500ml) - For beer, lager, ale, cider", "value": MEASURE_ID_LARGE_BOTTLE},
    {"label": "Large bottle (660ml) - For beer, lager, ale", "value": MEASURE_ID_EXTRA_LARGE_BOTTLE},
    {"label": "Small wine glass (125ml) - For wine", "value": MEASURE_ID_SMALL_WINE},
    {"label": "Medium wine glass (175ml) - For wine", "value": MEASURE_ID_MEDIUM_WINE},
    {"label": "Large wine glass (250ml) - For wine", "value": MEASURE_ID_LARGE_WINE},
    {"label": "Champagne glass (125ml) - For champagne, prosecco", "value": MEASURE_ID_CHAMPAGNE},
    {"label": "Medium champagne glass (187ml) - For champagne, prosecco", "value": MEASURE_ID_MEDIUM_CHAMPAGNE},
    {"label": "Single spirit measure (25ml) - For spirits", "value": MEASURE_ID_SINGLE_SPIRIT},
    {"label": "Double spirit measure (50ml) - For spirits", "value": MEASURE_ID_DOUBLE_SPIRIT},
    {"label": "Small port/sherry glass (75ml) - For port/sherry", "value": MEASURE_ID_PORT_SHERRY},
    {"label": "Custom measure ID", "value": "custom"},
]