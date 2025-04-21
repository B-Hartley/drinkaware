{
  "services": {
    "log_drink_free_day": {
      "name": "Log drink-free day",
      "description": "Mark a specific day as alcohol-free in your Drinkaware tracking",
      "fields": {
        "account_name": {
          "name": "Account Name",
          "description": "The name of your Drinkaware account (as entered during setup)"
        },
        "entry_id": {
          "name": "Config Entry ID",
          "description": "The Drinkaware config entry ID - only needed if account name is not specified"
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
        "account_name": {
          "name": "Account Name",
          "description": "The name of your Drinkaware account (as entered during setup)"
        },
        "entry_id": {
          "name": "Config Entry ID",
          "description": "The Drinkaware config entry ID - only needed if account name is not specified"
        },
        "drink_id": {
          "name": "Drink Type",
          "description": "The drink type to log. Select from standard options or enter a custom ID."
        },
        "measure_id": {
          "name": "Measure Type",
          "description": "The measure to use"
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
        "account_name": {
          "name": "Account Name",
          "description": "The name of your Drinkaware account (as entered during setup)"
        },
        "entry_id": {
          "name": "Config Entry ID",
          "description": "The Drinkaware config entry ID - only needed if account name is not specified"
        },
        "drink_id": {
          "name": "Drink Type",
          "description": "The drink type to delete. Select from standard options or enter a custom ID."
        },
        "measure_id": {
          "name": "Measure Type",
          "description": "The measure of the drink to delete"
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
        "account_name": {
          "name": "Account Name",
          "description": "The name of your Drinkaware account (as entered during setup)"
        },
        "entry_id": {
          "name": "Config Entry ID",
          "description": "The Drinkaware config entry ID - only needed if account name is not specified"
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
        "account_name": {
          "name": "Account Name",
          "description": "The name of your Drinkaware account (as entered during setup)"
        },
        "entry_id": {
          "name": "Config Entry ID",
          "description": "The Drinkaware config entry ID - only needed if account name is not specified"
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
        "account_name": {
          "name": "Account Name",
          "description": "The name of your Drinkaware account (as entered during setup) - leave empty to refresh all accounts"
        },
        "entry_id": {
          "name": "Config Entry ID",
          "description": "The Drinkaware config entry ID - only needed if account name is not specified"
        }
      }
    }
  }
}