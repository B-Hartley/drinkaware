"""
Sensor platform for Drinkaware integration.
"""
import logging
from typing import Dict, Any
from datetime import datetime, timedelta

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.const import PERCENTAGE
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

        # Use specialized handlers for different sensor types
        handler_method = getattr(self, f"_get_{key}_value", None)
        if handler_method:
            return handler_method()

        # Default return for unknown sensor types
        return None

    def _get_risk_level_value(self):
        """Get risk level sensor value."""
        if "assessment" not in self.coordinator.data:
            return None

        risk_level = self.coordinator.data["assessment"].get("riskLevel")
        return RISK_LEVELS.get(risk_level, risk_level)

    def _get_total_score_value(self):
        """Get total score sensor value."""
        if "assessment" not in self.coordinator.data:
            return None

        return self.coordinator.data["assessment"].get("totalScore")

    def _get_drink_free_days_value(self):
        """Get drink free days sensor value."""
        if "stats" not in self.coordinator.data:
            return None

        return self.coordinator.data["stats"].get("drinkFreeDays", {}).get("total", 0)

    def _get_drink_free_streak_value(self):
        """Get drink free streak sensor value."""
        if "stats" not in self.coordinator.data:
            return None

        return self.coordinator.data["stats"].get("drinkFreeDays", {}).get("streakCurrent", 0)

    def _get_days_tracked_value(self):
        """Get days tracked sensor value."""
        if "stats" not in self.coordinator.data:
            return None

        return self.coordinator.data["stats"].get("daysTracked", {}).get("total", 0)

    def _get_goals_achieved_value(self):
        """Get goals achieved sensor value."""
        if "stats" not in self.coordinator.data:
            return None

        return self.coordinator.data["stats"].get("goalsAchieved", 0)

    def _get_goal_progress_value(self):
        """Get goal progress sensor value."""
        if "goals" not in self.coordinator.data:
            return None

        for goal in self.coordinator.data["goals"]:
            if goal.get("type") == "drinkFreeDays":
                if goal.get("target", 0) > 0:
                    return round((goal.get("progress", 0) / goal.get("target", 1)) * 100)
        return 0

    def _get_weekly_units_value(self):
        """Get weekly units sensor value."""
        if "summary" not in self.coordinator.data:
            return None

        return self._calculate_weekly_units()

    def _calculate_weekly_units(self):
        """Calculate the total units consumed in the last 7 days."""
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

    def _get_last_drink_date_value(self):
        """Get last drink date sensor value."""
        if "summary" not in self.coordinator.data:
            return None

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

    def _get_drinks_today_value(self):
        """Get drinks today sensor value."""
        if "summary" not in self.coordinator.data:
            return None

        today = datetime.now().strftime("%Y-%m-%d")
        for day in self.coordinator.data["summary"]:
            if day.get("date") == today:
                return day.get("drinks", 0)
        return 0

    async def async_update(self):
        """Update the sensor."""
        # For the drinks_today sensor, ensure we have the latest daily detail data
        if self.entity_description.key == "drinks_today" and self.coordinator.last_update_success:
            await self._update_today_drink_details()

        # Update extra attributes
        self._update_attributes()
        await super().async_update()

    async def _update_today_drink_details(self):
        """Update drink details for today if needed."""
        today = datetime.now().strftime("%Y-%m-%d")

        # Check if we need to fetch drink details
        need_fetch = self._check_if_fetch_needed(today)

        # Fetch daily drink details if we need to
        if need_fetch:
            if not hasattr(self.coordinator, '_activity_cache'):
                self.coordinator._activity_cache = {}

            # Refresh the activity data for today
            self.coordinator._activity_cache[today] = await self.coordinator._fetch_activity_for_day(today)

    def _check_if_fetch_needed(self, today):
        """Check if we need to fetch detailed drink data for today."""
        if not hasattr(self.coordinator, 'data') or not self.coordinator.data:
            return False

        if "summary" in self.coordinator.data:
            for day in self.coordinator.data["summary"]:
                if day.get("date") == today and day.get("drinks", 0) > 0:
                    return True
        return False

    def _update_attributes(self):
        """Update the extra attributes dictionary."""
        self._attributes = {}  # Reset attributes

        # Add account information
        self._attributes["account_name"] = self.coordinator.account_name
        self._attributes["email"] = self.coordinator.email

        if not self.coordinator.data:
            return

        key = self.entity_description.key

        # Use specialized attribute handlers for different sensor types
        handler_method = getattr(self, f"_update_{key}_attributes", None)
        if handler_method:
            handler_method()

    def _update_risk_level_attributes(self):
        """Update attributes for risk level sensor."""
        if "assessment" not in self.coordinator.data:
            return

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

    def _update_drink_free_days_attributes(self):
        """Update attributes for drink free days sensor."""
        if "stats" not in self.coordinator.data:
            return

        self._attributes["Highest Streak"] = (
            self.coordinator.data["stats"].get("drinkFreeDays", {}).get("streakHighest", 0)
        )

    def _update_days_tracked_attributes(self):
        """Update attributes for days tracked sensor."""
        if "stats" not in self.coordinator.data:
            return

        self._attributes["Current Streak"] = (
            self.coordinator.data["stats"].get("daysTracked", {}).get("streakCurrent", 0)
        )
        self._attributes["Highest Streak"] = (
            self.coordinator.data["stats"].get("daysTracked", {}).get("streakHighest", 0)
        )
        self._attributes["Tracking Since"] = self.coordinator.data["stats"].get("trackingSince")

    def _update_goal_progress_attributes(self):
        """Update attributes for goal progress sensor."""
        if "goals" not in self.coordinator.data:
            return

        for goal in self.coordinator.data["goals"]:
            if goal.get("type") == "drinkFreeDays":
                self._attributes["Target"] = goal.get("target")
                self._attributes["Progress"] = goal.get("progress")
                self._attributes["Start Date"] = goal.get("startDate")

    def _update_weekly_units_attributes(self):
        """Update attributes for weekly units sensor."""
        if "summary" not in self.coordinator.data:
            return

        self._add_weekly_day_attributes()
        self._add_weekly_period_attributes()

    def _add_weekly_day_attributes(self):
        """Add individual day attributes for the weekly period."""
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

    def _add_weekly_period_attributes(self):
        """Add overall period information to weekly units attributes."""
        today = datetime.now().strftime("%Y-%m-%d")
        six_days_ago = (datetime.now() - timedelta(days=6)).strftime("%Y-%m-%d")

        # Add additional information about the weekly calculation period
        self._attributes["Weekly Period"] = {
            "Start Date": six_days_ago,
            "End Date": today,
            "Days Included": 7
        }

    def _update_drinks_today_attributes(self):
        """Update attributes for drinks today sensor."""
        today = datetime.now().strftime("%Y-%m-%d")

        # Initialize attributes with default values
        self._initialize_today_attributes()

        # Update with summary data if available
        self._update_today_summary_attributes(today)

        # Add detailed drink information if available
        self._update_today_detailed_attributes(today)

        # Add available drinks as attributes
        self._update_available_drinks_attributes()

    def _initialize_today_attributes(self):
        """Initialize today's attributes with default values."""
        self._attributes["Today's Units"] = 0
        self._attributes["Drink Free Day"] = True
        self._attributes["Detailed Drinks"] = []

    def _update_today_summary_attributes(self, today):
        """Update today's attributes with summary data."""
        if "summary" not in self.coordinator.data:
            return

        for day in self.coordinator.data["summary"]:
            if day.get("date") == today:
                self._attributes["Today's Units"] = day.get("units", 0)
                self._attributes["Drink Free Day"] = day.get("drinkFreeDay", True)
                break

    def _update_today_detailed_attributes(self, today):
        """Update with detailed drink information for today."""
        if not hasattr(self.coordinator, '_activity_cache') or today not in self.coordinator._activity_cache:
            return

        detailed_activity = self.coordinator._activity_cache[today]
        drinks = self._get_drinks_from_activity(detailed_activity)

        # Format each drink
        formatted_drinks = []
        for drink in drinks:
            formatted_drink = self._format_drink(drink)
            formatted_drinks.append(formatted_drink)

        self._attributes["Detailed Drinks"] = formatted_drinks

        # Also add raw data in a separate attribute
        self._attributes["Raw Drink Data"] = drinks

    def _get_drinks_from_activity(self, activity):
        """Extract drink data from activity response."""
        if "activity" in activity and activity["activity"]:
            return activity["activity"]
        if "drinks" in activity:
            return activity["drinks"]
        return []

    def _format_drink(self, drink):
        """Format a drink for display in attributes."""
        name = drink.get("name", "Unknown Drink")
        quantity = drink.get("quantity", 0)
        abv = drink.get("abv", 0)
        drink_id = drink.get("drinkId", "")
        measure_id = drink.get("measureId", "")

        measure_name = self._get_measure_name(drink)

        return (f"{quantity}x {name} ({measure_name}, {abv}% ABV) - "
                f"Drink ID: {drink_id}, Measure ID: {measure_id}")

    def _get_measure_name(self, drink):
        """Get the measure name from different possible locations in the drink data."""
        measure_name = drink.get("measureName", "")
        if measure_name:
            return measure_name

        if drink.get("measure"):
            measure_size = drink.get("measure")
            return self._format_measure_size(measure_size)

        return "Unknown measure"

    def _update_available_drinks_attributes(self):
        """Update attributes with available standard and custom drinks."""
        if not hasattr(self.coordinator, 'drinks_cache') or not self.coordinator.drinks_cache:
            return

        # Get standard and custom drinks
        standard_drinks = self._get_standard_drinks_from_categories()
        custom_drinks = self._get_custom_drinks()

        # Create a more user-friendly version of the custom drinks
        user_friendly_custom_drinks = self._create_user_friendly_custom_drinks(custom_drinks)

        # Add to attributes
        self._attributes["available_standard_drinks"] = standard_drinks
        self._attributes["available_custom_drinks"] = custom_drinks
        self._attributes["custom_drinks_reference"] = user_friendly_custom_drinks

    def _get_standard_drinks_from_categories(self):
        """Extract standard drinks from categories in the drinks cache."""
        standard_drinks = []

        if "categories" not in self.coordinator.drinks_cache:
            return standard_drinks

        for category in self.coordinator.drinks_cache["categories"]:
            category_name = category.get("title", "Unknown Category")
            for drink in category.get("drinks", []):
                standard_drinks.append({
                    "id": drink.get("drinkId"),
                    "category": category_name,
                    "title": drink.get("title"),
                    "abv": drink.get("abv"),
                    "measures": [
                        {
                            "id": m.get("measureId"),
                            "title": m.get("title"),
                            "size_ml": round(m.get("litres", 0) * 1000)
                        }
                        for m in drink.get("measures", [])
                    ]
                })
        return standard_drinks

    def _get_custom_drinks(self):
        """Get custom drinks from all possible sources in the drinks cache."""
        custom_drinks = []

        # Check customDrinks array
        if "customDrinks" in self.coordinator.drinks_cache:
            custom_drinks.extend(self.coordinator.drinks_cache["customDrinks"])

        # Check search results for custom drinks
        if "results" in self.coordinator.drinks_cache:
            for drink in self.coordinator.drinks_cache["results"]:
                if "derivedDrinkId" in drink:
                    # Check if this drink is already in our custom_drinks list
                    drink_id = drink.get("drinkId")
                    existing_ids = [d.get("drinkId") for d in custom_drinks]
                    if drink_id and drink_id not in existing_ids:
                        custom_drinks.append(drink)

        return custom_drinks

    def _create_user_friendly_custom_drinks(self, custom_drinks):
        """Create a more user-friendly representation of custom drinks."""
        user_friendly_drinks = []

        for drink in custom_drinks:
            drink_id = drink.get("drinkId", "")
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
                user_friendly_drink["measures"] = self._format_measures(drink["measures"])
            elif "measure" in drink:
                # Handle case when measure is a float or a dictionary
                measure_value = drink["measure"]
                if isinstance(measure_value, dict):
                    user_friendly_drink["measures"] = [{
                        "name": measure_value.get("title", "Unknown"),
                        "measure_id": measure_value.get("id", ""),
                        "size_ml": measure_value.get("size_ml", 0)
                    }]
                else:
                    # Handle case when measure is a float representing volume in liters
                    user_friendly_drink["measures"] = [{
                        "name": self._format_measure_size(measure_value),
                        "measure_id": drink.get("measureId", ""),
                        "size_ml": int(measure_value * 1000) if isinstance(measure_value, (float, int)) else 0
                    }]

            user_friendly_drinks.append(user_friendly_drink)

        return user_friendly_drinks

    def _format_measure_size(self, measure_size):
        """Format measure size into a readable string."""
        if not isinstance(measure_size, (float, int)):
            return "Unknown measure"

        measure_sizes = {
            0.025: "Single measure (25ml)",
            0.050: "Double measure (50ml)",
            0.125: "Small glass (125ml)",
            0.175: "Medium glass (175ml)",
            0.250: "Large glass (250ml)",
            0.568: "Pint (568ml)"
        }
        return measure_sizes.get(measure_size, f"{int(measure_size * 1000)}ml")

    def _format_measures(self, measures):
        """Format measure information for user-friendly display."""
        measure_list = []
        for measure in measures:
            measure_list.append({
                "name": measure.get("title", "Unknown"),
                "measure_id": measure.get("id", ""),
                "size_ml": measure.get("size_ml", 0)
            })
        return measure_list

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes."""
        # Make sure attributes are updated
        if not self._attributes:
            self._update_attributes()
        return self._attributes
