#!/usr/bin/env python3
"""
Utility script to set up test fixtures for the Drinkaware integration tests.
This creates the necessary fixture files in the tests/fixtures directory.
"""
import os
import json

# Create the fixtures directory if it doesn't exist
fixtures_dir = os.path.join("tests", "fixtures")
os.makedirs(fixtures_dir, exist_ok=True)

# Define the fixture data
fixtures = {
    "activity.json": {
        "activity": [
            {
                "drinkId": "FAB60DBF-911F-4286-9C3E-0F0BCB40E3B7",
                "measureId": "B59DCD68-96FF-4B4C-BA69-3707D085C407",
                "quantity": 1,
                "name": "Lager",
                "abv": 4.0,
                "measureName": "Pint"
            },
            {
                "drinkId": "E3DEDBFD-63CE-492D-8E3E-9C24010227D8",
                "measureId": "E586C800-24CA-4942-837A-4CD2CBF8338A",
                "quantity": 1,
                "name": "White Wine",
                "abv": 13.0,
                "measureName": "Medium glass"
            }
        ],
        "sleep": {
            "quality": "average"
        }
    },
    "assessment.json": {
        "assessments": [
            {
                "riskLevel": "low",
                "totalScore": 5,
                "frequencyScore": 1,
                "unitNumberScore": 1,
                "bingeFrequencyScore": 0,
                "unableToStopScore": 0,
                "expectationScore": 1,
                "morningScore": 0,
                "guiltScore": 1,
                "memoryLossScore": 0,
                "injuryScore": 0,
                "relativeConcernedScore": 1,
                "created": "2025-04-01T10:00:00Z"
            }
        ]
    },
    "drinks.json": {
        "categories": [
            {
                "title": "Beer & Cider",
                "drinks": [
                    {
                        "drinkId": "FAB60DBF-911F-4286-9C3E-0F0BCB40E3B7",
                        "title": "Lager",
                        "abv": 4.0,
                        "measures": [
                            {
                                "measureId": "B59DCD68-96FF-4B4C-BA69-3707D085C407",
                                "title": "Pint",
                                "litres": 0.568
                            },
                            {
                                "measureId": "174F45D7-745A-45F0-9D44-88DA1075CE79",
                                "title": "Half pint",
                                "litres": 0.284
                            }
                        ]
                    },
                    {
                        "drinkId": "61AD633A-7366-4497-BD36-9078466F00FE",
                        "title": "Cider",
                        "abv": 4.5,
                        "measures": [
                            {
                                "measureId": "B59DCD68-96FF-4B4C-BA69-3707D085C407",
                                "title": "Pint",
                                "litres": 0.568
                            },
                            {
                                "measureId": "174F45D7-745A-45F0-9D44-88DA1075CE79",
                                "title": "Half pint",
                                "litres": 0.284
                            }
                        ]
                    }
                ]
            },
            {
                "title": "Wine",
                "drinks": [
                    {
                        "drinkId": "E3DEDBFD-63CE-492D-8E3E-9C24010227D8",
                        "title": "White Wine",
                        "abv": 13.0,
                        "measures": [
                            {
                                "measureId": "0E40AE5F-098D-4826-ADCA-298A6A14F514",
                                "title": "Small glass",
                                "litres": 0.125
                            },
                            {
                                "measureId": "E586C800-24CA-4942-837A-4CD2CBF8338A",
                                "title": "Medium glass",
                                "litres": 0.175
                            },
                            {
                                "measureId": "6450132A-F73F-414A-83BB-43C37B40272F",
                                "title": "Large glass",
                                "litres": 0.25
                            }
                        ]
                    }
                ]
            },
            {
                "title": "Spirits",
                "drinks": [
                    {
                        "drinkId": "0E3CA732-21D6-4631-A60C-155C2BB85C18",
                        "title": "Vodka",
                        "abv": 40.0,
                        "measures": [
                            {
                                "measureId": "A83406D4-741F-49B4-B310-8B7DEB8B072F",
                                "title": "Single",
                                "litres": 0.025
                            },
                            {
                                "measureId": "FCCC81A2-3BFF-45C0-832F-BCF73E81D0D1",
                                "title": "Double",
                                "litres": 0.05
                            }
                        ]
                    }
                ]
            }
        ],
        "customDrinks": [
            {
                "drinkId": "12345678-ABCD-1234-5678-123456789ABC",
                "title": "Custom IPA",
                "abv": 6.5,
                "derivedDrinkId": "D4F06BD4-1F61-468B-AE86-C6CC2D56E021",
                "measures": [
                    {
                        "measureId": "B59DCD68-96FF-4B4C-BA69-3707D085C407",
                        "title": "Pint",
                        "litres": 0.568
                    }
                ]
            }
        ],
        "results": [
            {
                "drinkId": "87654321-ABCD-1234-5678-123456789ABC",
                "title": "Craft Beer",
                "abv": 5.5,
                "derivedDrinkId": "D4F06BD4-1F61-468B-AE86-C6CC2D56E021",
                "measureId": "B59DCD68-96FF-4B4C-BA69-3707D085C407",
                "measureName": "Pint",
                "measure": 0.568
            }
        ]
    },
    "goals.json": {
        "goals": [
            {
                "type": "drinkFreeDays",
                "target": 4,
                "progress": 3,
                "startDate": "2025-04-15T00:00:00Z"
            }
        ]
    },
    "stats.json": {
        "drinkFreeDays": {
            "total": 15,
            "streakCurrent": 3,
            "streakHighest": 5
        },
        "daysTracked": {
            "total": 30,
            "streakCurrent": 7,
            "streakHighest": 10
        },
        "trackingSince": "2025-03-21T00:00:00Z",
        "goalsAchieved": 2
    },
    "summary.json": {
        "activitySummaryDays": [
            {
                "date": "2025-04-22",
                "drinks": 0,
                "units": 0,
                "drinkFreeDay": True
            },
            {
                "date": "2025-04-21",
                "drinks": 0,
                "units": 0,
                "drinkFreeDay": True
            },
            {
                "date": "2025-04-20",
                "drinks": 0,
                "units": 0,
                "drinkFreeDay": True
            },
            {
                "date": "2025-04-19",
                "drinks": 2,
                "units": 4.5,
                "drinkFreeDay": False
            },
            {
                "date": "2025-04-18",
                "drinks": 1,
                "units": 2.3,
                "drinkFreeDay": False
            },
            {
                "date": "2025-04-17",
                "drinks": 0,
                "units": 0,
                "drinkFreeDay": True
            },
            {
                "date": "2025-04-16",
                "drinks": 0,
                "units": 0,
                "drinkFreeDay": True
            },
            {
                "date": "2025-04-15",
                "drinks": 3,
                "units": 6.8,
                "drinkFreeDay": False
            }
        ]
    }
}

# Write the fixture files
for filename, data in fixtures.items():
    filepath = os.path.join(fixtures_dir, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print(f"Created {filepath}")

print("All test fixtures created successfully!")