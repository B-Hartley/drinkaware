"""Test fixtures for Drinkaware integration tests."""
from unittest.mock import patch, MagicMock, AsyncMock
import pytest
import json
import os

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_TOKEN
from homeassistant.core import HomeAssistant

from custom_components.drinkaware.const import DOMAIN


@pytest.fixture
def mock_config_entry():
    """Create a mock config entry for testing."""
    return {
        "entry_id": "test_entry_id",
        "unique_id": "test@example.com",
        "title": "Drinkaware - Test Account",
        "data": {
            "token": {
                "access_token": "test_access_token",
                "refresh_token": "test_refresh_token",
                "expires_in": 3600,
            },
            "account_name": "Test Account",
            "email": "test@example.com",
            "user_id": "test_user_id",
        },
    }


@pytest.fixture
def load_fixture():
    """Load a fixture JSON file."""
    def _load_fixture(filename):
        """Load a fixture file."""
        fixtures_dir = os.path.join(os.path.dirname(__file__), "fixtures")
        file_path = os.path.join(fixtures_dir, filename)
        
        with open(file_path, "r") as file:
            return json.load(file)
    
    return _load_fixture


@pytest.fixture
def mock_api_responses():
    """Create mock responses for API calls."""
    mock_resp = AsyncMock()
    mock_resp.status = 200
    
    # Mock JSON responses based on URL pattern
    async def mock_json():
        """Return mock JSON based on the URL."""
        url = mock_api_responses.get.call_args[0][0]
        
        if "assessment" in url:
            return {"riskLevel": "low", "totalScore": 5}
        elif "stats" in url:
            return {
                "drinkFreeDays": {"total": 15, "streakCurrent": 3, "streakHighest": 5},
                "daysTracked": {"total": 30, "streakCurrent": 7, "streakHighest": 10},
                "goalsAchieved": 2
            }
        elif "goals" in url:
            return {"goals": [{"type": "drinkFreeDays", "target": 4, "progress": 3}]}
        elif "summary" in url:
            return {
                "activitySummaryDays": [
                    {"date": "2025-04-23", "drinks": 0, "units": 0, "drinkFreeDay": True},
                    {"date": "2025-04-22", "drinks": 0, "units": 0, "drinkFreeDay": True},
                    {"date": "2025-04-21", "drinks": 0, "units": 0, "drinkFreeDay": True},
                    {"date": "2025-04-20", "drinks": 2, "units": 4.5, "drinkFreeDay": False},
                    {"date": "2025-04-19", "drinks": 1, "units": 2.3, "drinkFreeDay": False},
                    {"date": "2025-04-18", "drinks": 0, "units": 0, "drinkFreeDay": True},
                    {"date": "2025-04-17", "drinks": 0, "units": 0, "drinkFreeDay": True}
                ]
            }
        elif "drinks" in url:
            return {
                "categories": [
                    {
                        "title": "Beer & Cider",
                        "drinks": [
                            {
                                "drinkId": "FAB60DBF-911F-4286-9C3E-0F0BCB40E3B7",
                                "title": "Lager",
                                "abv": 4.0,
                                "measures": [
                                    {"measureId": "B59DCD68-96FF-4B4C-BA69-3707D085C407", "title": "Pint", "litres": 0.568}
                                ]
                            }
                        ]
                    }
                ],
                "customDrinks": []
            }
        elif "activity" in url:
            return {
                "activity": [
                    {
                        "drinkId": "FAB60DBF-911F-4286-9C3E-0F0BCB40E3B7",
                        "measureId": "B59DCD68-96FF-4B4C-BA69-3707D085C407",
                        "quantity": 1,
                        "name": "Lager",
                        "abv": 4.0,
                        "measureName": "Pint"
                    }
                ]
            }
        else:
            return {"success": True}
    
    mock_resp.json = mock_json
    mock_resp.text = AsyncMock(return_value="Success")
    
    mock_api_responses = AsyncMock()
    mock_api_responses.get.return_value.__aenter__.return_value = mock_resp
    mock_api_responses.post.return_value.__aenter__.return_value = mock_resp
    mock_api_responses.put.return_value.__aenter__.return_value = mock_resp
    mock_api_responses.delete.return_value.__aenter__.return_value = mock_resp
    
    return mock_api_responses


@pytest.fixture
async def setup_integration(hass: HomeAssistant, mock_config_entry, mock_api_responses):
    """Set up the Drinkaware integration for testing."""
    # Create a ConfigEntry from the mock data
    config_entry = ConfigEntry(
        version=1,
        domain=DOMAIN,
        title=mock_config_entry["title"],
        data=mock_config_entry["data"],
        source="test",
        options={},
        entry_id=mock_config_entry["entry_id"],
        unique_id=mock_config_entry["unique_id"],
    )
    
    # Initialize the component data
    hass.data.setdefault(DOMAIN, {})
    
    # Create and set up a mock coordinator
    with patch("custom_components.drinkaware.DrinkAwareDataUpdateCoordinator", autospec=True) as mock_coordinator_class:
        coordinator = mock_coordinator_class.return_value
        coordinator.account_name = "Test Account"
        coordinator.email = "test@example.com"
        coordinator.entry_id = "test_entry_id"
        coordinator.access_token = "test_access_token"
        coordinator.refresh_token = "test_refresh_token"
        coordinator.last_update_success = True
        coordinator.session = mock_api_responses
        
        # Set up mock data
        coordinator.data = {
            "assessment": {"riskLevel": "low", "totalScore": 5},
            "stats": {
                "drinkFreeDays": {"total": 15, "streakCurrent": 3, "streakHighest": 5},
                "daysTracked": {"total": 30, "streakCurrent": 7, "streakHighest": 10},
                "trackingSince": "2025-03-21T00:00:00Z",
                "goalsAchieved": 2
            },
            "goals": [{"type": "drinkFreeDays", "target": 4, "progress": 3}],
            "summary": [
                {"date": "2025-04-23", "drinks": 0, "units": 0, "drinkFreeDay": True},
                {"date": "2025-04-22", "drinks": 0, "units": 0, "drinkFreeDay": True},
                {"date": "2025-04-21", "drinks": 0, "units": 0, "drinkFreeDay": True},
                {"date": "2025-04-20", "drinks": 2, "units": 4.5, "drinkFreeDay": False},
                {"date": "2025-04-19", "drinks": 1, "units": 2.3, "drinkFreeDay": False},
                {"date": "2025-04-18", "drinks": 0, "units": 0, "drinkFreeDay": True},
                {"date": "2025-04-17", "drinks": 0, "units": 0, "drinkFreeDay": True}
            ]
        }
        
        # Add mock drinks cache
        coordinator.drinks_cache = {
            "categories": [
                {
                    "title": "Beer & Cider",
                    "drinks": [
                        {
                            "drinkId": "FAB60DBF-911F-4286-9C3E-0F0BCB40E3B7",
                            "title": "Lager",
                            "abv": 4.0,
                            "measures": [
                                {"measureId": "B59DCD68-96FF-4B4C-BA69-3707D085C407", "title": "Pint", "litres": 0.568}
                            ]
                        }
                    ]
                }
            ],
            "customDrinks": []
        }
        
        # Store coordinator in hass data
        hass.data[DOMAIN][config_entry.entry_id] = coordinator
        
        # Mock setting up platforms
        with patch('homeassistant.config_entries.ConfigEntries.async_forward_entry_setup',
                  return_value=True) as mock_async_forward_entry_setup:
            
            from custom_components.drinkaware import async_setup_entry
            assert await async_setup_entry(hass, config_entry)
            
        return coordinator