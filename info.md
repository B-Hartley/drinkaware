# Drinkaware Integration

This integration allows you to monitor your Drinkaware app data in Home Assistant.

## Features

- **Risk Assessment**: View your current risk level and detailed assessment scores
- **Drink Tracking**: Monitor your drink-free days, streaks, and weekly unit consumption
- **Goal Tracking**: See your progress toward drink-free day goals
- **Statistics**: Track days monitored, goals achieved, and your last recorded drink
- **Custom Drinks**: Support for custom drink IDs from the Drinkaware app
- **Service Controls**: Log and delete drinks, mark drink-free days, and record sleep quality

## Setup

1. Add the integration through the Home Assistant UI
2. Authenticate with your Drinkaware account using OAuth
3. Complete the setup process by following the on-screen instructions

## Available Sensors

The integration provides several sensors including:
- Risk Level
- Self Assessment Score
- Drink Free Days
- Current Drink Free Streak
- Days Tracked
- Goals Achieved
- Current Goal Progress
- Weekly Units
- Last Drink Date
- Drinks Today (with detailed information in attributes)

## Using Custom Drink IDs

The integration supports using custom drink IDs for logging drinks:

1. Find custom drink IDs in the `custom_drinks_reference` attribute of the "Drinks Today" sensor
2. When using the `log_drink` or `delete_drink` service, select "Custom drink ID" option
3. Enter the custom drink ID in the appropriate field

## Screenshots

*Add your screenshots here*

## Need Help?

If you need assistance, please check the [TROUBLESHOOTING.md](https://github.com/B-Hartley/drinkaware/blob/main/TROUBLESHOOTING.md) file or open an issue on [GitHub](https://github.com/B-Hartley/drinkaware/issues).