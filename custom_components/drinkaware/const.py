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

# Update intervals
SCAN_INTERVAL_HOURS = 1

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