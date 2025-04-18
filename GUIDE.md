# Drinkaware Integration Guide

This comprehensive guide covers all aspects of using the Drinkaware integration, including available services, drink types, measures, and examples.

## Table of Contents
1. [Services](#services)
2. [Available Drinks](#available-drinks)
3. [Measures](#measures)
4. [Custom Drinks](#custom-drinks)
5. [Example Scripts and Automations](#example-scripts-and-automations)

## Services

The Drinkaware integration provides the following services:

### Log Drink-Free Day (`drinkaware.log_drink_free_day`)

Mark a specific day as alcohol-free in your Drinkaware tracking.

**Parameters:**
- `account_name`: (Optional) The name of your Drinkaware account (as entered during setup)
- `entry_id`: (Optional) The Drinkaware config entry ID (only needed if account name is not specified)
- `date`: (Optional) The date to mark as a drink-free day (defaults to today)
- `remove_drinks`: (Optional) Automatically remove any existing drinks for the day before marking it as drink-free (defaults to false)

**Example:**
```yaml
service: drinkaware.log_drink_free_day
data:
  account_name: "Bruce"
  date: "2025-04-18"
  remove_drinks: true
```

### Log Drink (`drinkaware.log_drink`)

Record a drink in your Drinkaware tracking.

**Parameters:**
- `account_name`: (Optional) The name of your Drinkaware account (as entered during setup)
- `entry_id`: (Optional) The Drinkaware config entry ID (only needed if account name is not specified)
- `drink_id`: (Required) The drink type ID from Drinkaware API
- `measure_id`: (Required) The measure ID from Drinkaware API
- `abv`: (Optional) The alcohol percentage (will use default if not specified)
- `quantity`: (Optional) The number of drinks of this type (defaults to 1)
- `date`: (Optional) The date to log the drink (defaults to today)
- `auto_remove_dfd`: (Optional) Automatically remove the drink-free day mark if present (defaults to false)

**Example:**
```yaml
service: drinkaware.log_drink
data:
  account_name: "Bruce"
  drink_id: "D4F06BD4-1F61-468B-AE86-C6CC2D56E021"  # Beer
  measure_id: "B59DCD68-96FF-4B4C-BA69-3707D085C407"  # Pint
  abv: 4.5
  quantity: 2
  date: "2025-04-18"
  auto_remove_dfd: true
```

### Delete Drink (`drinkaware.delete_drink`)

Remove a recorded drink from your Drinkaware tracking.

**Parameters:**
- `account_name`: (Optional) The name of your Drinkaware account (as entered during setup)
- `entry_id`: (Optional) The Drinkaware config entry ID (only needed if account name is not specified)
- `drink_id`: (Required) The drink type ID to delete
- `measure_id`: (Required) The measure ID of the drink to delete
- `date`: (Optional) The date the drink was logged (defaults to today)

**Example:**
```yaml
service: drinkaware.delete_drink
data:
  account_name: "Bruce"
  drink_id: "D4F06BD4-1F61-468B-AE86-C6CC2D56E021"  # Beer
  measure_id: "B59DCD68-96FF-4B4C-BA69-3707D085C407"  # Pint
  date: "2025-04-18"
```

### Remove Drink-Free Day (`drinkaware.remove_drink_free_day`)

Remove the drink-free day marking for a specific date.

**Parameters:**
- `account_name`: (Optional) The name of your Drinkaware account (as entered during setup)
- `entry_id`: (Optional) The Drinkaware config entry ID (only needed if account name is not specified)
- `date`: (Optional) The date to remove the drink-free day marking (defaults to today)

**Example:**
```yaml
service: drinkaware.remove_drink_free_day
data:
  account_name: "Bruce"
  date: "2025-04-18"
```

### Log Sleep Quality (`drinkaware.log_sleep_quality`)

Record sleep quality for a specific date.

**Parameters:**
- `account_name`: (Optional) The name of your Drinkaware account (as entered during setup)
- `entry_id`: (Optional) The Drinkaware config entry ID (only needed if account name is not specified)
- `quality`: (Required) The quality of sleep to record ("poor", "average", or "great")
- `date`: (Optional) The date to log the sleep quality (defaults to today)

**Example:**
```yaml
service: drinkaware.log_sleep_quality
data:
  account_name: "Bruce"
  quality: "average"
  date: "2025-04-18"
```

### Refresh Data (`drinkaware.refresh`)

Manually refresh data from the Drinkaware API.

**Parameters:**
- `account_name`: (Optional) The name of your Drinkaware account (as entered during setup)
- `entry_id`: (Optional) The Drinkaware config entry ID (only needed if account name is not specified)

**Example:**
```yaml
service: drinkaware.refresh
data:
  account_name: "Bruce"
```

## Available Drinks

The following drink types are available in the Drinkaware API:

### Beer
- Lager (`FAB60DBF-911F-4286-9C3E-0F0BCB40E3B7`): 4.0% ABV
- Beer (`D4F06BD4-1F61-468B-AE86-C6CC2D56E021`): 5.0% ABV
- Ale/stout (`1F8DF28A-5F05-470E-833B-06C499965C99`): 4.5% ABV

### Wine
- White Wine (`E3DEDBFD-63CE-492D-8E3E-9C24010227D8`): 13.0% ABV
- Red Wine (`19E82B28-9AD5-4546-A966-13B27EC6E4FB`): 13.0% ABV
- Rosé Wine (`FA3B43D0-A418-4F4D-8FC1-218E8DA81918`): 13.0% ABV
- Champagne (`61C3F476-24D1-46DB-9FA0-613ED4082531`): 12.0% ABV
- Prosecco (`5184149E-450E-4A63-92E5-19AD7F49FCD1`): 12.0% ABV

### Spirits
- Vodka (`0E3CA732-21D6-4631-A60C-155C2BB85C18`): 40.0% ABV
- Gin (`FECCEBB8-68D1-4BF1-B42F-7BB6C919B0F0`): 40.0% ABV
- Tequila (`32B22A73-D900-43E1-AAB6-8ADC27590B5D`): 50.0% ABV
- Rum (`780B45E2-26D6-4F55-A0C1-75868835D672`): 40.0% ABV
- Whisk(e)y (`2AAE4A2E-8C0A-40E1-BCDE-EB986111D2DE`): 40.0% ABV
- Brandy (`E473445D-2B75-47DA-9978-24C80093B1D0`): 40.0% ABV
- Other Spirit (`300546E3-DB89-49DC-B4B5-8ED96EB18C12`): 40.0% ABV

### Fortified Wines
- Port/Sherry (`F8486573-6F92-4B63-BAEB-3E76B750E14D`): 18.0% ABV

### Cider
- Cider (`61AD633A-7366-4497-BD36-9078466F00FE`): 4.5% ABV

### Alcopops
- Alcopop (`0B2A65CA-5EC4-46B6-9E4D-6E0DDC8D57B8`): 4.0% ABV

## Measures

The following measures are available for different drink types:

### Beer and Cider Measures
- Pint (`B59DCD68-96FF-4B4C-BA69-3707D085C407`): 568ml
- Half pint (`174F45D7-745A-45F0-9D44-88DA1075CE79`): 284ml
- Small bottle/can (`6B56A1FB-33A1-4E51-BED7-536751DE56BC`): 330ml
- Bottle/can (`0CB11B53-6E3C-4C47-A2E9-68BA40DFFE13`): 440ml
- Bottle (`8F185B18-2A82-4D1A-A1F7-20E01D5E2FEC`): 500ml
- Large bottle (`03D87F35-A1DF-40EE-9398-FA1CA55DD894`): 660ml

### Wine Measures
- Small glass (`0E40AE5F-098D-4826-ADCA-298A6A14F514`): 125ml
- Medium glass (`E586C800-24CA-4942-837A-4CD2CBF8338A`): 175ml
- Large glass (`6450132A-F73F-414A-83BB-43C37B40272F`): 250ml

### Champagne and Prosecco Measures
- Glass (`B6CFC69E-0E85-4F82-A109-155801BB7C79`): 125ml
- Medium glass (`A8B1FA3D-25A2-4685-92E9-DE9D19407CE3`): 187ml

### Spirit Measures
- Single measure (`A83406D4-741F-49B4-B310-8B7DEB8B072F`): 25ml
- Double measure (`FCCC81A2-3BFF-45C0-832F-BCF73E81D0D1`): 50ml

### Port/Sherry Measures
- Small glass (`021703DD-248C-4A51-ACFD-0CE97540C8EC`): 75ml

## Custom Drinks

The Drinkaware integration supports both predefined drink types and custom drinks that may be created in the Drinkaware app.

### Understanding Custom Drinks

Custom drinks are created within the Drinkaware app and are assigned unique IDs that work just like the predefined drink types. From the perspective of Home Assistant, there's no functional difference between a predefined drink type and a custom drink - both are identified by UUIDs.

### Some Known Custom Drinks

- Corona 330ml (`E44AE744-1318-4978-8C84-E143C2B0AE3B`): 4.5% ABV (derived from Lager)
- Wingman A.F. (`B515F736-F194-4ED4-A7A9-EA2D75CC51AD`): 0.5% ABV (derived from Lager)
- Tequila (`4DDB9B89-CCB5-471E-A03C-AC516AE4E821`): 45.0% ABV (custom version of standard Tequila)

### How to Find Custom Drink IDs

To find the ID of a custom drink:
- You'll need to use a network capture tool like MITM Proxy to inspect the traffic from the Drinkaware app
- Look for the `drinkId` parameter when a drink is added
- The "Drinks Today" sensor can also help by showing the raw drink data in its attributes

### Using Custom Drinks

If you have identified a custom drink ID:

```yaml
service: drinkaware.log_drink
data:
  account_name: "Bruce"
  drink_id: "1A2B3C4D-5E6F-7890-ABCD-EF1234567890"  # Your custom drink ID
  measure_id: "B59DCD68-96FF-4B4C-BA69-3707D085C407"  # Pint
  abv: 5.2  # Custom ABV if needed
  quantity: 1
```

## Example Scripts and Automations

### Helper Scripts for Common Drinks

```yaml
script:
  log_pint_of_beer:
    alias: "Log a pint of beer"
    description: "Log a pint of beer to Drinkaware"
    fields:
      quantity:
        description: "Number of beers"
        example: 1
      abv:
        description: "Alcohol percentage"
        example: 5.0
    sequence:
      - service: drinkaware.log_drink
        data:
          account_name: "Bruce"
          drink_id: "D4F06BD4-1F61-468B-AE86-C6CC2D56E021"  # Beer
          measure_id: "B59DCD68-96FF-4B4C-BA69-3707D085C407"  # Pint
          quantity: "{{ quantity }}"
          abv: "{{ abv }}"
          auto_remove_dfd: true
          
  log_glass_of_wine:
    alias: "Log a glass of red wine"
    description: "Log a medium glass of red wine to Drinkaware"
    fields:
      quantity:
        description: "Number of glasses"
        example: 1
    sequence:
      - service: drinkaware.log_drink
        data:
          account_name: "Bruce"
          drink_id: "19E82B28-9AD5-4546-A966-13B27EC6E4FB"  # Red Wine
          measure_id: "E586C800-24CA-4942-837A-4CD2CBF8338A"  # Medium glass
          quantity: "{{ quantity }}"
          auto_remove_dfd: true
```

### Automatic Drink-Free Day Marking

```yaml
automation:
  - alias: "Mark yesterday as drink-free if no drinks logged"
    trigger:
      - platform: time
        at: "01:00:00"
    condition:
      - condition: template
        value_template: >
          {% set yesterday = (now() - timedelta(days=1)).strftime('%Y-%m-%d') %}
          {% set has_drinks = false %}
          {% for day in state_attr('sensor.drinkaware_bruce_weekly_units', yesterday) %}
            {% if day.Drinks > 0 %}
              {% set has_drinks = true %}
            {% endif %}
          {% endfor %}
          {{ not has_drinks }}
    action:
      - service: drinkaware.log_drink_free_day
        data:
          account_name: "Bruce"
          date: "{{ (now() - timedelta(days=1)).strftime('%Y-%m-%d') }}"
```

### Regular Data Refresh

```yaml
automation:
  - alias: "Refresh Drinkaware data hourly"
    trigger:
      - platform: time_pattern
        hours: "/1"
    action:
      - service: drinkaware.refresh
        data:
          account_name: "Bruce"
```

### Notification When Approaching Weekly Limit

```yaml
automation:
  - alias: "Weekly unit limit warning"
    trigger:
      - platform: state
        entity_id: sensor.drinkaware_bruce_weekly_units
    condition:
      - condition: template
        value_template: "{{ states('sensor.drinkaware_bruce_weekly_units')|float > 12 }}"
    action:
      - service: notify.mobile_app
        data:
          title: "Alcohol Consumption Warning"
          message: "You have consumed {{ states('sensor.drinkaware_bruce_weekly_units') }} units this week, approaching the recommended limit."
```

## Note on API Limitations

The Drinkaware API may have rate limiting in place, so avoid making too many service calls in a short period of time. If you encounter errors like "Rate limit exceeded," the integration will automatically wait and retry after a brief delay.