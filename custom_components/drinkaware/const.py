"""
Constants for the Drinkaware integration.
"""

DOMAIN = "drinkaware"

# OAuth Configuration
OAUTH_CLIENT_ID = "fe14e7b9-d4e1-4967-8fce-617c6f48a055"
# Use the exact URLs from the CURL commands
OAUTH_AUTHORIZATION_URL = "https://login.drinkaware.co.uk/login.drinkaware.co.uk/B2C_1A_JITMigraion_signup_signin/oauth2/v2.0/authorize"
OAUTH_TOKEN_URL = "https://login.drinkaware.co.uk/login.drinkaware.co.uk/B2C_1A_JITMigraion_signup_signin/oauth2/v2.0/token"

# API URLs
API_BASE_URL = "https://api.drinkaware.co.uk"

# API Endpoints
ENDPOINT_SELF_ASSESSMENT = "/tools/v1/selfassessment"
ENDPOINT_STATS = "/tracking/v1/stats"
ENDPOINT_GOALS = "/tracking/v1/goals"
ENDPOINT_SUMMARY = "/tracking/v1/summary"
ENDPOINT_DRINKS_GENERIC = "/drinks/v1/generic"
ENDPOINT_DRINKS_CUSTOM = "/drinks/v1/custom"
ENDPOINT_MESSAGES = "/messages/v1"
ENDPOINT_DAY = "/tracking/v1/activity"  # Updated path based on logs
ENDPOINT_DRINKS = "/tracking/v1/activity"  # Updated path based on logs

# Update intervals
SCAN_INTERVAL_HOURS = 1

# Service names
SERVICE_LOG_DRINK_FREE_DAY = "log_drink_free_day"
SERVICE_LOG_DRINK = "log_drink"
SERVICE_DELETE_DRINK = "delete_drink"
SERVICE_REMOVE_DRINK_FREE_DAY = "remove_drink_free_day"
SERVICE_LOG_SLEEP_QUALITY = "log_sleep_quality"
SERVICE_REFRESH = "refresh"
SERVICE_CREATE_CUSTOM_MEASURE = "create_custom_measure"

# Service attributes
ATTR_ENTRY_ID = "entry_id"
ATTR_ACCOUNT_NAME = "account_name"
ATTR_DRINK_TYPE = "drink_id"
ATTR_DRINK_MEASURE = "measure_id"
ATTR_DRINK_ABV = "abv"
ATTR_DRINK_QUANTITY = "quantity"
ATTR_SLEEP_QUALITY = "quality"
ATTR_MEASURE_SIZE = "measure_size"
ATTR_MEASURE_TITLE = "measure_title"

# Sensor names
RISK_LEVEL = "risk_level"
TOTAL_SCORE = "total_score"
DRINK_FREE_DAYS = "drink_free_days"
DRINK_FREE_STREAK = "drink_free_streak"
DAYS_TRACKED = "days_tracked"
GOALS_ACHIEVED = "goals_achieved"
GOAL_PROGRESS = "goal_progress"
WEEKLY_UNITS = "weekly_units"
LAST_DRINK_DATE = "last_drink_date"
SLEEP_QUALITY = "sleep_quality"

# Risk levels
RISK_LEVEL_LOW = "low"
RISK_LEVEL_INCREASING = "increasing"
RISK_LEVEL_HIGH = "high"
RISK_LEVEL_DEPENDENCY = "possible_dependency"

# Human-friendly risk levels
RISK_LEVELS = {
    RISK_LEVEL_LOW: "Low Risk",
    RISK_LEVEL_INCREASING: "Increasing Risk",
    RISK_LEVEL_HIGH: "High Risk",
    RISK_LEVEL_DEPENDENCY: "Possible Dependency"
}