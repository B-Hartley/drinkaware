"""
Sensor platform for Drinkaware integration.
"""
import logging
from typing import Callable, Dict, Any, List, Optional
from datetime import datetime, timedelta

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE, 
    CONF_EMAIL
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from . import DrinkAwareDataUpdateCoordinator, DOMAIN
from .const import (
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
    RISK_LEVEL_INCREASING,
    RISK_LEVEL_HIGH,
    RISK_LEVEL_DEPENDENCY,
)

_LOGGER = logging.getLogger(__name__)

# Use constants for risk levels from the const.py file
RISK_LEVELS = {
    RISK_LEVEL_LOW: "Low Risk",
    RISK_LEVEL_INCREASING: "Increasing Risk",
    RISK_LEVEL_HIGH: "High Risk",
    RISK_LEVEL_DEPENDENCY: "Possible Dependency"
}

SENSOR_DESCRIPTIONS = [
    SensorEntityDescription(
        key=RISK_LEVEL,
        name="Risk Level",
        icon="mdi:alert-circle",
    ),
    SensorEntityDescription(
        key=TOTAL_SCORE,
        name="Self Assessment Score",
        icon="mdi:counter",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=DRINK_FREE_DAYS,
        name="Drink Free Days",
        icon="mdi:calendar-check",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=DRINK_FREE_STREAK,
        name="Current Drink Free Streak",
        icon="mdi:fire",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=DAYS_TRACKED,
        name="Days Tracked",
        icon="mdi:calendar-clock",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=GOALS_ACHIEVED,
        name="Goals Achieved",
        icon="mdi:trophy",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=GOAL_PROGRESS,
        name="Current Goal Progress",
        icon="mdi:progress-check",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
    ),
    SensorEntityDescription(
        key=WEEKLY_UNITS,
        name="Weekly Units",
        icon="mdi:cup",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=LAST_DRINK_DATE,
        name="Last Drink Date",
        icon="mdi:glass-wine",
        device_class=SensorDeviceClass.DATE,
    ),
    SensorEntityDescription(
        key="drinks_today",
        name="Drinks Today",
        icon="mdi:glass-cocktail",
        state_class=SensorStateClass.MEASUREMENT,
    ),
]

async def async_setup_platform(
    hass: HomeAssistant,
    config,
    async_add_entities: AddEntitiesCallback,
    discovery_info=None,
) -> None:
    """Set up the Drinkaware sensor platform."""
    if discovery_info is None:
        return
        
    coordinator = hass.data[DOMAIN]["coordinator"]
    
    entities = []
    for description in SENSOR_DESCRIPTIONS:
        entities.append(DrinkAwareSensor(coordinator, description))
        
    async_add_entities(entities, True)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Drinkaware sensor based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = []
    for description in SENSOR_DESCRIPTIONS:
        entities.append(DrinkAwareSensor(coordinator, description))
        
    async_add_entities(entities, True)


class DrinkAwareSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Drinkaware sensor."""

    def __init__(
        self, 
        coordinator: DrinkAwareDataUpdateCoordinator,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_name = f"Drinkaware {coordinator.account_name} {description.name}"
        self._attr_unique_id = f"drinkaware_{coordinator.entry_id}_{description.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.entry_id)},
            "name": f"Drinkaware {coordinator.account_name}",
            "manufacturer": "Drinkaware",
            "model": "Account",
            "sw_version": "1.0",
        }
        self._attributes = {}  # Initialize attributes dictionary
        
    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.coordinator.last_update_success and self.coordinator.data
        
    @property
    def native_value(self) -> StateType:
        """Return the state of the entity."""
        if not self.coordinator.data:
            return None
            
        key = self.entity_description.key
        
        if key == RISK_LEVEL and "assessment" in self.coordinator.data:
            risk_level = self.coordinator.data["assessment"].get("riskLevel")
            return RISK_LEVELS.get(risk_level, risk_level)
            
        elif key == TOTAL_SCORE and "assessment" in self.coordinator.data:
            return self.coordinator.data["assessment"].get("totalScore")
            
        elif key == DRINK_FREE_DAYS and "stats" in self.coordinator.data:
            return self.coordinator.data["stats"].get("drinkFreeDays", {}).get("total", 0)
            
        elif key == DRINK_FREE_STREAK and "stats" in self.coordinator.data:
            return self.coordinator.data["stats"].get("drinkFreeDays", {}).get("streakCurrent", 0)
            
        elif key == DAYS_TRACKED and "stats" in self.coordinator.data:
            return self.coordinator.data["stats"].get("daysTracked", {}).get("total", 0)
            
        elif key == GOALS_ACHIEVED and "stats" in self.coordinator.data:
            return self.coordinator.data["stats"].get("goalsAchieved", 0)
            
        elif key == GOAL_PROGRESS and "goals" in self.coordinator.data:
            for goal in self.coordinator.data["goals"]:
                if goal.get("type") == "drinkFreeDays":
                    if goal.get("target", 0) > 0:
                        return round((goal.get("progress", 0) / goal.get("target", 1)) * 100)
            return 0
            
        elif key == WEEKLY_UNITS and "summary" in self.coordinator.data:
            total_units = 0
            # Get current date in the same format as in the API (YYYY-MM-DD)
            today = datetime.now().strftime("%Y-%m-%d")
            # Calculate the date 6 days ago (which gives us 7 days including today)
            six_days_ago = (datetime.now() - timedelta(days=6)).strftime("%Y-%m-%d")
            
            # Filter and sum only the units from the last 7 days
            for day in self.coordinator.data["summary"]:
                day_date = day.get("date", "")
                # Include only dates that are within the last 7 days
                if day_date >= six_days_ago and day_date <= today:
                    total_units += day.get("units", 0)
            
            return round(total_units, 1)
            
        elif key == LAST_DRINK_DATE and "summary" in self.coordinator.data:
            last_drink_date = None
            for day in self.coordinator.data["summary"]:
                if not day.get("drinkFreeDay", True):
                    date_str = day.get("date")
                    if date_str:
                        try:
                            date = datetime.strptime(date_str, "%Y-%m-%d").date()
                            if last_drink_date is None or date > last_drink_date:
                                last_drink_date = date
                        except ValueError:
                            pass
            return last_drink_date
            
        elif key == "drinks_today" and "summary" in self.coordinator.data:
            today = datetime.now().strftime("%Y-%m-%d")
            for day in self.coordinator.data["summary"]:
                if day.get("date") == today:
                    return day.get("drinks", 0)
            return 0
            
        return None

    async def async_update(self):
        """Update the sensor."""
        # For the drinks_today sensor, ensure we have the latest daily detail data
        if self.entity_description.key == "drinks_today" and self.coordinator.last_update_success:
            today = datetime.now().strftime("%Y-%m-%d")
            
            # Check if we need to fetch drink details
            need_fetch = False
            if hasattr(self.coordinator, 'data') and self.coordinator.data:
                if "summary" in self.coordinator.data:
                    for day in self.coordinator.data["summary"]:
                        if day.get("date") == today and day.get("drinks", 0) > 0:
                            need_fetch = True
                            break
            
            # Fetch daily drink details if we need to
            if need_fetch:
                if not hasattr(self.coordinator, '_activity_cache'):
                    self.coordinator._activity_cache = {}
                
                # Refresh the activity data for today
                self.coordinator._activity_cache[today] = await self.coordinator._fetch_activity_for_day(today)
        
        # Update extra attributes
        self._update_attributes()
        await super().async_update()

    def _update_attributes(self):
        """Update the extra attributes dictionary."""
        self._attributes = {}  # Reset attributes
        
        # Add account information
        self._attributes["account_name"] = self.coordinator.account_name
        self._attributes["email"] = self.coordinator.email
        
        if not self.coordinator.data:
            return
            
        key = self.entity_description.key
        
        if key == RISK_LEVEL and "assessment" in self.coordinator.data:
            assessment = self.coordinator.data["assessment"]
            scores = {
                "Frequency": assessment.get("frequencyScore"),
                "Units": assessment.get("unitNumberScore"),
                "Binge Frequency": assessment.get("bingeFrequencyScore"),
                "Unable to Stop": assessment.get("unableToStopScore"),
                "Expectations": assessment.get("expectationScore"),
                "Morning Drinking": assessment.get("morningScore"),
                "Guilt": assessment.get("guiltScore"),
                "Memory Loss": assessment.get("memoryLossScore"),
                "Injury": assessment.get("injuryScore"),
                "Concerns from Others": assessment.get("relativeConcernedScore"),
            }
            self._attributes.update(scores)
            self._attributes["Assessment Date"] = assessment.get("created")
            
        elif key == DRINK_FREE_DAYS and "stats" in self.coordinator.data:
            self._attributes["Highest Streak"] = self.coordinator.data["stats"].get("drinkFreeDays", {}).get("streakHighest", 0)
            
        elif key == DAYS_TRACKED and "stats" in self.coordinator.data:
            self._attributes["Current Streak"] = self.coordinator.data["stats"].get("daysTracked", {}).get("streakCurrent", 0)
            self._attributes["Highest Streak"] = self.coordinator.data["stats"].get("daysTracked", {}).get("streakHighest", 0)
            self._attributes["Tracking Since"] = self.coordinator.data["stats"].get("trackingSince")
            
        elif key == GOAL_PROGRESS and "goals" in self.coordinator.data:
            for goal in self.coordinator.data["goals"]:
                if goal.get("type") == "drinkFreeDays":
                    self._attributes["Target"] = goal.get("target")
                    self._attributes["Progress"] = goal.get("progress")
                    self._attributes["Start Date"] = goal.get("startDate")
                    
        elif key == WEEKLY_UNITS and "summary" in self.coordinator.data:
            # Add drink details by day
            today = datetime.now().strftime("%Y-%m-%d")
            six_days_ago = (datetime.now() - timedelta(days=6)).strftime("%Y-%m-%d")
            
            for day in self.coordinator.data["summary"]:
                date = day.get("date")
                if date and date >= six_days_ago and date <= today:
                    self._attributes[date] = {
                        "Units": day.get("units", 0),
                        "Drinks": day.get("drinks", 0),
                        "Drink Free": day.get("drinkFreeDay", True)
                    }
            
            # Add additional information about the weekly calculation period
            self._attributes["Weekly Period"] = {
                "Start Date": six_days_ago,
                "End Date": today,
                "Days Included": 7
            }
               
        elif key == "drinks_today":
            today = datetime.now().strftime("%Y-%m-%d")
            
            # Initialize attributes with default values
            self._attributes["Today's Units"] = 0
            self._attributes["Drink Free Day"] = True
            self._attributes["Detailed Drinks"] = []
            
            # Check summary for high-level data
            if "summary" in self.coordinator.data:
                for day in self.coordinator.data["summary"]:
                    if day.get("date") == today:
                        self._attributes["Today's Units"] = day.get("units", 0)
                        self._attributes["Drink Free Day"] = day.get("drinkFreeDay", True)
                        break
            
            # Check for detailed drink information
            if hasattr(self.coordinator, '_activity_cache') and today in self.coordinator._activity_cache:
                detailed_activity = self.coordinator._activity_cache[today]
                drinks = detailed_activity.get("activity", [])
                if not drinks and "drinks" in detailed_activity:
                    drinks = detailed_activity.get("drinks", [])
                
                # Format each drink
                formatted_drinks = []
                for drink in drinks:
                    name = drink.get("name", "Unknown Drink")
                    quantity = drink.get("quantity", 0)
                    abv = drink.get("abv", 0)
                    drink_id = drink.get("drinkId", "")
                    measure_id = drink.get("measureId", "")
                    
                    # Get measure name from different possible locations
                    measure_name = drink.get("measureName", "")
                    if not measure_name:
                        if drink.get("measure"):
                            measure_size = drink.get("measure")
                            if measure_size == 0.025:
                                measure_name = "Single measure (25ml)"
                            elif measure_size == 0.050:
                                measure_name = "Double measure (50ml)"
                            elif measure_size == 0.125:
                                measure_name = "Small glass (125ml)"
                            elif measure_size == 0.175:
                                measure_name = "Medium glass (175ml)"
                            elif measure_size == 0.250:
                                measure_name = "Large glass (250ml)"
                            elif measure_size == 0.568:
                                measure_name = "Pint (568ml)"
                            else:
                                measure_name = f"{int(measure_size * 1000)}ml"
                    
                    formatted_drink = f"{quantity}x {name} ({measure_name}, {abv}% ABV) - Drink ID: {drink_id}, Measure ID: {measure_id}"
                    formatted_drinks.append(formatted_drink)
                
                self._attributes["Detailed Drinks"] = formatted_drinks
                
                # Also add raw data in a separate attribute
                self._attributes["Raw Drink Data"] = drinks
            
            # Add available drinks as attributes
            standard_drinks = []
            custom_drinks = []
            
            if hasattr(self.coordinator, 'drinks_cache') and self.coordinator.drinks_cache:
                # Add standard drinks
                if "categories" in self.coordinator.drinks_cache:
                    for category in self.coordinator.drinks_cache["categories"]:
                        category_name = category.get("title", "Unknown Category")
                        for drink in category.get("drinks", []):
                            standard_drinks.append({
                                "id": drink.get("drinkId"),
                                "category": category_name,
                                "title": drink.get("title"),
                                "abv": drink.get("abv"),
                                "measures": [
                                    {"id": m.get("measureId"), "title": m.get("title"), "size_ml": round(m.get("litres", 0) * 1000)}
                                    for m in drink.get("measures", [])
                                ]
                            })
                
                # Add custom drinks
                if "customDrinks" in self.coordinator.drinks_cache:
                    for drink in self.coordinator.drinks_cache["customDrinks"]:
                        custom_drinks.append({
                            "id": drink.get("drinkId"),
                            "title": drink.get("title"),
                            "abv": drink.get("abv"),
                            "measures": [
                                {"id": m.get("measureId"), "title": m.get("title"), "size_ml": round(m.get("litres", 0) * 1000)}
                                for m in drink.get("measures", [])
                            ]
                        })
                
                # Also check search results for custom drinks
                if "results" in self.coordinator.drinks_cache:
                    for drink in self.coordinator.drinks_cache["results"]:
                        if "derivedDrinkId" in drink:  # This indicates it's a custom drink
                            # Check if this drink is already in our custom_drinks list
                            drink_id = drink.get("drinkId")
                            existing_ids = [d.get("id") for d in custom_drinks]
                            if drink_id and drink_id not in existing_ids:
                                custom_drinks.append({
                                    "id": drink_id,
                                    "title": drink.get("title", "Custom Drink"),
                                    "abv": drink.get("abv", 0),
                                    "measure": {
                                        "id": drink.get("measureId"),
                                        "title": drink.get("measureName", "Unknown"),
                                        "size_ml": round(drink.get("measure", 0) * 1000)
                                    }
                                })
            
            # Create a more user-friendly version of the custom drinks
            user_friendly_custom_drinks = []
            for drink in custom_drinks:
                drink_id = drink.get("id", "")
                title = drink.get("title", "Unknown")
                abv = drink.get("abv", 0)
                
                # Create a user-friendly entry with the most important information
                user_friendly_drink = {
                    "name": title,
                    "drink_id": drink_id,
                    "abv": abv
                }
                
                # Add measures if available
                if "measures" in drink and drink["measures"]:
                    measure_list = []
                    for measure in drink["measures"]:
                        measure_list.append({
                            "name": measure.get("title", "Unknown"),
                            "measure_id": measure.get("id", ""),
                            "size_ml": measure.get("size_ml", 0)
                        })
                    user_friendly_drink["measures"] = measure_list
                elif "measure" in drink:
                    user_friendly_drink["measures"] = [{
                        "name": drink["measure"].get("title", "Unknown"),
                        "measure_id": drink["measure"].get("id", ""),
                        "size_ml": drink["measure"].get("size_ml", 0)
                    }]
                    
                user_friendly_custom_drinks.append(user_friendly_drink)
            
            self._attributes["available_standard_drinks"] = standard_drinks
            self._attributes["available_custom_drinks"] = custom_drinks
            self._attributes["custom_drinks_reference"] = user_friendly_custom_drinks
            
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes."""
        # Make sure attributes are updated
        if not self._attributes:
            self._update_attributes()
        return self._attributes