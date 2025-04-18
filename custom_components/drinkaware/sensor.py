"""
Sensor platform for Drinkaware integration.
"""
import logging
from typing import Callable, Dict, Any, List, Optional
from datetime import datetime

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

_LOGGER = logging.getLogger(__name__)

RISK_LEVELS = {
    "low": "Low Risk",
    "increasing": "Increasing Risk",
    "high": "High Risk",
    "possible_dependency": "Possible Dependency"
}

SENSOR_DESCRIPTIONS = [
    SensorEntityDescription(
        key="risk_level",
        name="Risk Level",
        icon="mdi:alert-circle",
    ),
    SensorEntityDescription(
        key="total_score",
        name="Self Assessment Score",
        icon="mdi:counter",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="drink_free_days",
        name="Drink Free Days",
        icon="mdi:calendar-check",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="drink_free_streak",
        name="Current Drink Free Streak",
        icon="mdi:fire",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="days_tracked",
        name="Days Tracked",
        icon="mdi:calendar-clock",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="goals_achieved",
        name="Goals Achieved",
        icon="mdi:trophy",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="goal_progress",
        name="Current Goal Progress",
        icon="mdi:progress-check",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
    ),
    SensorEntityDescription(
        key="weekly_units",
        name="Weekly Units",
        icon="mdi:cup",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="last_drink_date",
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
        
        if key == "risk_level" and "assessment" in self.coordinator.data:
            risk_level = self.coordinator.data["assessment"].get("riskLevel")
            return RISK_LEVELS.get(risk_level, risk_level)
            
        elif key == "total_score" and "assessment" in self.coordinator.data:
            return self.coordinator.data["assessment"].get("totalScore")
            
        elif key == "drink_free_days" and "stats" in self.coordinator.data:
            return self.coordinator.data["stats"].get("drinkFreeDays", {}).get("total", 0)
            
        elif key == "drink_free_streak" and "stats" in self.coordinator.data:
            return self.coordinator.data["stats"].get("drinkFreeDays", {}).get("streakCurrent", 0)
            
        elif key == "days_tracked" and "stats" in self.coordinator.data:
            return self.coordinator.data["stats"].get("daysTracked", {}).get("total", 0)
            
        elif key == "goals_achieved" and "stats" in self.coordinator.data:
            return self.coordinator.data["stats"].get("goalsAchieved", 0)
            
        elif key == "goal_progress" and "goals" in self.coordinator.data:
            for goal in self.coordinator.data["goals"]:
                if goal.get("type") == "drinkFreeDays":
                    if goal.get("target", 0) > 0:
                        return round((goal.get("progress", 0) / goal.get("target", 1)) * 100)
            return 0
            
        elif key == "weekly_units" and "summary" in self.coordinator.data:
            total_units = 0
            for day in self.coordinator.data["summary"]:
                total_units += day.get("units", 0)
            return round(total_units, 1)
            
        elif key == "last_drink_date" and "summary" in self.coordinator.data:
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
        
        await super().async_update()

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes."""
        attrs = {}
        
        # Add account information
        attrs["account_name"] = self.coordinator.account_name
        attrs["email"] = self.coordinator.email
        
        if not self.coordinator.data:
            return attrs
            
        key = self.entity_description.key
        
        if key == "risk_level" and "assessment" in self.coordinator.data:
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
            attrs.update(scores)
            attrs["Assessment Date"] = assessment.get("created")
            
        elif key == "drink_free_days" and "stats" in self.coordinator.data:
            attrs["Highest Streak"] = self.coordinator.data["stats"].get("drinkFreeDays", {}).get("streakHighest", 0)
            
        elif key == "days_tracked" and "stats" in self.coordinator.data:
            attrs["Current Streak"] = self.coordinator.data["stats"].get("daysTracked", {}).get("streakCurrent", 0)
            attrs["Highest Streak"] = self.coordinator.data["stats"].get("daysTracked", {}).get("streakHighest", 0)
            attrs["Tracking Since"] = self.coordinator.data["stats"].get("trackingSince")
            
        elif key == "goal_progress" and "goals" in self.coordinator.data:
            for goal in self.coordinator.data["goals"]:
                if goal.get("type") == "drinkFreeDays":
                    attrs["Target"] = goal.get("target")
                    attrs["Progress"] = goal.get("progress")
                    attrs["Start Date"] = goal.get("startDate")
                    
        elif key == "weekly_units" and "summary" in self.coordinator.data:
            # Add drink details by day
            for day in self.coordinator.data["summary"]:
                date = day.get("date")
                if date:
                    attrs[date] = {
                        "Units": day.get("units", 0),
                        "Drinks": day.get("drinks", 0),
                        "Drink Free": day.get("drinkFreeDay", True)
                    }
        
        elif key == "drinks_today":
            today = datetime.now().strftime("%Y-%m-%d")
            
            # Initialize attributes with default values
            attrs["Today's Units"] = 0
            attrs["Drink Free Day"] = True
            attrs["Detailed Drinks"] = []
            
            # Check summary for high-level data
            if "summary" in self.coordinator.data:
                for day in self.coordinator.data["summary"]:
                    if day.get("date") == today:
                        attrs["Today's Units"] = day.get("units", 0)
                        attrs["Drink Free Day"] = day.get("drinkFreeDay", True)
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
                    
                    formatted_drink = f"{quantity}x {name} ({measure_name}, {abv}% ABV)"
                    formatted_drinks.append(formatted_drink)
                
                attrs["Detailed Drinks"] = formatted_drinks
                
                # Also add raw data in a separate attribute
                attrs["Raw Drink Data"] = drinks
                
        return attrs