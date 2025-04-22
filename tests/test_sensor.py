"""Test the Drinkaware sensor platform."""
from unittest.mock import patch, MagicMock, AsyncMock
import pytest
from datetime import datetime, timedelta

from homeassistant.const import PERCENTAGE
from homeassistant.components.sensor import (
    SensorEntityDescription,
    SensorDeviceClass,
    SensorStateClass,
)

from custom_components.drinkaware.const import (
    DOMAIN,
    RISK_LEVEL,
    TOTAL_SCORE,
    DRINK_FREE_DAYS,
    DRINK_FREE_STREAK,
    DAYS_TRACKED,
    GOALS_ACHIEVED,
    GOAL_PROGRESS,
    WEEKLY_UNITS,
    LAST_DRINK_DATE,
    SLEEP_QUALITY,
    RISK_LEVEL_LOW,
)
from custom_components.drinkaware.sensor import DrinkAwareSensor


async def test_sensors_setup(hass, setup_integration, load_fixture):
    """Test sensor setup."""
    # Check that the sensors were registered
    entity_registry = hass.helpers.entity_registry.async_get(hass)
    
    # Get all registered sensors for this domain
    entities = [
        entity_id for entity_id in entity_registry.entities
        if entity_id.startswith("sensor.drinkaware")
    ]
    
    # There should be 10 sensors (risk_level, total_score, etc.)
    assert len(entities) == 10


@pytest.mark.parametrize(
    "entity_id, expected_state", 
    [
        ("sensor.drinkaware_test_account_risk_level", "Low Risk"),
        ("sensor.drinkaware_test_account_self_assessment_score", 5),
        ("sensor.drinkaware_test_account_drink_free_days", 15),
        ("sensor.drinkaware_test_account_current_drink_free_streak", 3),
        ("sensor.drinkaware_test_account_days_tracked", 30),
        ("sensor.drinkaware_test_account_goals_achieved", 2),
        ("sensor.drinkaware_test_account_current_goal_progress", 75),
        ("sensor.drinkaware_test_account_weekly_units", 13.6),  # Sum of units from activitySummaryDays
    ]
)
async def test_sensor_states(hass, setup_integration, entity_id, expected_state):
    """Test the states of individual sensors."""
    # Get the state of the sensor
    state = hass.states.get(entity_id)
    
    # Check that it exists
    assert state is not None
    
    # Check the state value
    if entity_id == "sensor.drinkaware_test_account_weekly_units":
        # For floating point values, use an approximate comparison
        assert abs(float(state.state) - expected_state) < 0.1
    else:
        assert state.state == str(expected_state)


async def test_drink_free_days_attributes(hass, setup_integration):
    """Test attributes of the drink_free_days sensor."""
    # Get the state of the sensor
    state = hass.states.get("sensor.drinkaware_test_account_drink_free_days")
    
    # Check the attributes
    assert state.attributes["Highest Streak"] == 5


async def test_days_tracked_attributes(hass, setup_integration):
    """Test attributes of the days_tracked sensor."""
    # Get the state of the sensor
    state = hass.states.get("sensor.drinkaware_test_account_days_tracked")
    
    # Check the attributes
    assert state.attributes["Current Streak"] == 7
    assert state.attributes["Highest Streak"] == 10
    assert "Tracking Since" in state.attributes


async def test_weekly_units_attributes(hass, setup_integration):
    """Test attributes of the weekly_units sensor."""
    # Get the state of the sensor
    state = hass.states.get("sensor.drinkaware_test_account_weekly_units")
    
    # Check the attributes
    assert "Weekly Period" in state.attributes
    weekly_period = state.attributes["Weekly Period"]
    assert "Start Date" in weekly_period
    assert "End Date" in weekly_period
    assert weekly_period["Days Included"] == 7
    
    # Check that we have daily breakdown
    today = datetime.now().strftime("%Y-%m-%d")
    assert today in state.attributes


async def test_drinks_today_sensor(hass, setup_integration, load_fixture, mock_api_responses):
    """Test the drinks_today sensor."""
    # Set up a specific response for today's activity
    today = datetime.now().strftime("%Y-%m-%d")
    mock_resp = AsyncMock()
    mock_resp.status = 200
    mock_resp.json = AsyncMock(return_value=load_fixture("activity.json"))
    
    # Configure the API response for today's activity
    mock_api_responses.get.side_effect = lambda url, **kwargs: mock_resp if f"/activity/{today}" in url else mock_api_responses.get.return_value
    
    # Get the sensor entity
    entity_id = "sensor.drinkaware_test_account_drinks_today"
    await hass.services.async_call(
        "homeassistant", "update_entity", {"entity_id": entity_id}, blocking=True
    )
    
    # Get the state of the sensor
    state = hass.states.get(entity_id)
    
    # Check the state
    assert state is not None
    assert state.state == "2"  # 2 drinks in the activity.json fixture
    
    # Check attributes
    assert "Today's Units" in state.attributes
    assert "Detailed Drinks" in state.attributes
    assert len(state.attributes["Detailed Drinks"]) == 2


async def test_sensor_unit_of_measurement(hass, setup_integration):
    """Test that sensors have the correct unit of measurement."""
    # Goal progress should have percentage unit
    state = hass.states.get("sensor.drinkaware_test_account_current_goal_progress")
    assert state.attributes["unit_of_measurement"] == PERCENTAGE


async def test_sensor_device_class(hass, setup_integration):
    """Test that sensors have the correct device class."""
    # Last drink date should have date device class
    state = hass.states.get("sensor.drinkaware_test_account_last_drink_date")
    assert state.attributes["device_class"] == SensorDeviceClass.DATE


async def test_sensor_state_class(hass, setup_integration):
    """Test that sensors have the correct state class."""
    # Drink free days should have measurement state class
    state = hass.states.get("sensor.drinkaware_test_account_drink_free_days")
    assert state.attributes["state_class"] == SensorStateClass.MEASUREMENT


def test_sensor_entity_creation():
    """Test the creation of a DrinkAwareSensor entity."""
    # Create a mock coordinator
    coordinator = MagicMock()
    coordinator.account_name = "Test Account"
    coordinator.entry_id = "test_entry_id"
    coordinator.email = "test@example.com"
    coordinator.last_update_success = True
    coordinator.data = {
        "assessment": {
            "riskLevel": RISK_LEVEL_LOW,
            "totalScore": 5
        }
    }
    
    # Create a sensor description
    description = SensorEntityDescription(
        key=RISK_LEVEL,
        name="Risk Level",
        icon="mdi:alert-circle",
    )
    
    # Create the sensor entity
    sensor = DrinkAwareSensor(coordinator, description)
    
    # Check that it's set up correctly
    assert sensor.name == "Drinkaware Test Account Risk Level"
    assert sensor.unique_id == f"drinkaware_test_entry_id_{RISK_LEVEL}"
    assert sensor.device_info["identifiers"] == {(DOMAIN, "test_entry_id")}
    assert sensor.native_value == "Low Risk"
    assert sensor.available is True