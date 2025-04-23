{
  "services": {
    "log_drink_free_day": {
      "name": "Log drink-free day",
      "description": "Mark a specific day as alcohol-free in your Drinkaware tracking",
      "fields": {
        "entry_id": {
          "name": "Config Entry ID",
          "description": "The Drinkaware integration to use"
        },
        "date": {
          "name": "Date",
          "description": "The date to mark as a drink-free day (defaults to today)"
        },
        "remove_drinks": {
          "name": "Remove Existing Drinks",
          "description": "Automatically remove any existing drinks for the day before marking it as drink-free"
        }
      }
    },
    "log_drink": {
      "name": "Log drink",
      "description": "Record a drink in your Drinkaware tracking",
      "fields": {
        "entry_id": {
          "name": "Config Entry ID",
          "description": "The Drinkaware integration to use"
        },
        "drink_id": {
          "name": "Standard Drink Type",
          "description": "Select a standard drink type from the list (use this OR custom drink ID)"
        },
        "custom_drink_id": {
          "name": "Custom Drink ID",
          "description": "Enter a custom drink ID (use this OR standard drink type)"
        },
        "measure_id": {
          "name": "Measure Type",
          "description": "The measure to use (make sure it's compatible with the selected drink type)"
        },
        "name": {
          "name": "Custom Name",
          "description": "Optional custom name for the drink (only works with custom ABV)"
        },
        "abv": {
          "name": "ABV",
          "description": "The alcohol percentage (optional, will use default if not specified)"
        },
        "quantity": {
          "name": "Quantity",
          "description": "The number of drinks of this type (defaults to 1)"
        },
        "date": {
          "name": "Date",
          "description": "The date to log the drink (defaults to today)"
        },
        "auto_remove_dfd": {
          "name": "Auto Remove Drink-Free Day",
          "description": "Automatically remove the drink-free day mark if present"
        }
      }
    },
    "delete_drink": {
      "name": "Delete drink",
      "description": "Remove a recorded drink from your Drinkaware tracking",
      "fields": {
        "entry_id": {
          "name": "Config Entry ID",
          "description": "The Drinkaware integration to use"
        },
        "drink_id": {
          "name": "Standard Drink Type",
          "description": "Select a standard drink type from the list (use this OR custom drink ID)"
        },
        "custom_drink_id": {
          "name": "Custom Drink ID",
          "description": "Enter a custom drink ID (use this OR standard drink type)"
        },
        "measure_id": {
          "name": "Measure Type",
          "description": "The measure of the drink to delete (must be compatible with the selected drink type)"
        },
        "date": {
          "name": "Date",
          "description": "The date the drink was logged (defaults to today)"
        }
      }
    },
    "remove_drink_free_day": {
      "name": "Remove drink-free day",
      "description": "Remove the drink-free day marking for a specific date",
      "fields": {
        "entry_id": {
          "name": "Config Entry ID",
          "description": "The Drinkaware integration to use"
        },
        "date": {
          "name": "Date",
          "description": "The date to remove the drink-free day marking (defaults to today)"
        }
      }
    },
    "log_sleep_quality": {
      "name": "Log sleep quality",
      "description": "Record sleep quality for a specific date",
      "fields": {
        "entry_id": {
          "name": "Config Entry ID",
          "description": "The Drinkaware integration to use"
        },
        "quality": {
          "name": "Sleep Quality",
          "description": "The quality of sleep to record"
        },
        "date": {
          "name": "Date",
          "description": "The date to log the sleep quality (defaults to today)"
        }
      }
    },
    "refresh": {
      "name": "Refresh data",
      "description": "Manually refresh data from the Drinkaware API",
      "fields": {
        "entry_id": {
          "name": "Config Entry ID",
          "description": "The Drinkaware integration to use (leave empty to refresh all integrations)"
        }
      }
    }
  },
  "entity": {
    "button": {
      "log_drink_free_day": {
        "name": "Log Drink Free Day",
        "state_attributes": {
          "friendly_name": "Log Drink Free Day"
        }
      }
    }
  }
}