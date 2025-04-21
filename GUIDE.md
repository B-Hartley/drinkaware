# Drinkaware Integration Guide

This comprehensive guide covers all aspects of using the Drinkaware integration for Home Assistant, including installation, configuration, available services, sensors, drink types, measures, and example automations.

## Table of Contents
1. [Installation](#installation)
2. [Configuration](#configuration)
3. [Available Sensors](#available-sensors)
4. [Services](#services)
5. [Available Drinks](#available-drinks)
6. [Measures](#measures)
7. [Custom Drinks](#custom-drinks)
8. [Example Scripts and Automations](#example-scripts-and-automations)
9. [Troubleshooting](#troubleshooting)
10. [Privacy and Security](#privacy-and-security)

## Installation

### Method 1: HACS (Recommended)

1. Make sure you have [HACS](https://hacs.xyz/) installed
2. Add this repository as a custom repository in HACS:
   - Go to HACS → Integrations → ⋮ (menu) → Custom Repositories
   - Add `https://github.com/B-Hartley/drinkaware` as a repository
   - Category: Integration
3. Click "Install" on the Drinkaware integration
4. Restart Home Assistant

### Method 2: Manual Installation

1. Download the latest release
2. Extract the `drinkaware` folder into your `custom_components` directory
3. Restart Home Assistant

## Configuration

The integration can be set up through the Home Assistant UI:

1. Go to **Settings** → **Devices & Services**
2. Click the **+ Add Integration** button
3. Search for "Drinkaware" and select it
4. Follow the configuration flow

### Authentication Method

This integration uses OAuth to authenticate with Drinkaware:

1. Enter a name for your Drinkaware account
2. Click the link to authorize Drinkaware
3. Log in with your Drinkaware credentials
4. After successful login, you'll be redirected to a page that won't load (this is normal)
5. **Important:** Open your browser's Developer Tools (press F12), go to the Network tab, find the callback URL, right-click and select "Copy URL"
6. Paste the copied URL in the next step of the setup process

**Note:** In the Network tab, look for a request with "callback" in the name. The URL should start with `uk.co.drinkaware.drinkaware://oauth/callback` and contain a code parameter.

## Available Sensors

The integration creates several sensors:

| Sensor | Description |
|--------|-------------|
| Risk Level | Your assessed risk level (Low, Increasing, High, or Possible Dependency) |
| Self Assessment Score | Your total score from the self-assessment |
| Drink Free Days | Total number of alcohol-free days tracked |
| Current Drink Free Streak | Your current streak of consecutive alcohol-free days |
| Days Tracked | Total number of days tracked in the app |
| Goals Achieved | Number of goals you've achieved |
| Current Goal Progress | Progress toward your current goal as a percentage |
| Weekly Units | Total units consumed in the past week |
| Last Drink Date | Date of your most recent recorded drink |
| Drinks Today | Number of drinks consumed today, with detailed list in attributes |

### Sensor Details and Attributes

Most sensors include additional data in their attributes. Here are some examples:

#### Risk Level Sensor
- **State:** Low Risk, Increasing Risk, High Risk, or Possible Dependency
- **Attributes:**
  - Individual scores for frequency, units, binge frequency, etc.
  - Assessment date

#### Weekly Units Sensor
- **State:** Total units for the past 7 days
- **Attributes:**
  - Daily breakdown with units, drinks, and drink-free status for each day
  - Information about the weekly calculation period

#### Drinks Today Sensor
- **State:** Number of drinks recorded today
- **Attributes:**
  - Today's total units
  - Drink-free day status
  - Detailed list of each drink with quantity, name, measure, and ABV
  - Available standard drinks and custom drinks (useful for service calls)
  - **`custom_drinks_reference`**: User-friendly list of custom drinks with their IDs

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
- `drink_id`: (Optional) The standard drink type to log from dropdown menu (use this OR custom_drink_id)
- `custom_drink_id`: (Optional) A custom drink ID from the Drinks Today sensor (use this OR drink_id)
- `measure_id`: (Required) The measure to use from dropdown menu
- `abv`: (Optional) The alcohol percentage (will use default if not specified)
- `name`: (Optional) Custom name for the drink (only works when specifying a custom ABV)
- `quantity`: (Optional) The number of drinks of this type (defaults to 1)
- `date`: (Optional) The date to log the drink (defaults to today)
- `auto_remove_dfd`: (Optional) Automatically remove the drink-free day mark if present (defaults to false)

**Example with standard drink:**
```yaml
service: drinkaware.log_drink
data:
  account_name: "Bruce"
  drink_id: "D4F06BD4-1F61-468B-AE86-C6CC2D56E021"  # Beer (select from dropdown)
  measure_id: "B59DCD68-96FF-4B4C-BA69-3707D085C407"  # Pint (select from dropdown)
  abv: 4.5
  name: "Local Craft IPA"  # Custom name (only works with custom ABV)
  quantity: 2
  date: "2025-04-18"
  auto_remove_dfd: true
```

**Example with custom drink ID:**
```yaml
service: drinkaware.log_drink
data:
  account_name: "Bruce"
  custom_drink_id: "12345678-ABCD-1234-5678-123456789ABC"  # Custom drink ID from Drinks Today sensor
  measure_id: "B59DCD68-96FF-4B4C-BA69-3707D085C407"  # Pint (select from dropdown)
  quantity: 1
  date: "2025-04-18"
  auto_remove_dfd: true
```

### Delete Drink (`drinkaware.delete_drink`)

Remove a recorded drink from your Drinkaware tracking.

**Parameters:**
- `account_name`: (Optional) The name of your Drinkaware account (as entered during setup)
- `entry_id`: (Optional) The Drinkaware config entry ID (only needed if account name is not specified)
- `drink_id`: (Optional) The standard drink type to delete from dropdown menu (use this OR custom_drink_id)
- `custom_drink_id`: (Optional) A custom drink ID from the Drinks Today sensor (use this OR drink_id)
- `measure_id`: (Required) The measure of the drink to delete from dropdown menu
- `date`: (Optional) The date the drink was logged (defaults to today)

**Example with standard drink:**
```yaml
service: drinkaware.delete_drink
data:
  account_name: "Bruce"
  drink_id: "D4F06BD4-1F61-468B-AE86-C6CC2D56E021"  # Beer (select from dropdown)
  measure_id: "B59DCD68-96FF-4B4C-BA69-3707D085C407"  # Pint (select from dropdown)
  date: "2025-04-18"
```

**Example with custom drink ID:**
```yaml
service: drinkaware.delete_drink
data:
  account_name: "Bruce"
  custom_drink_id: "12345678-ABCD-1234-5678-123456789ABC"  # Custom drink ID from Drinks Today sensor
  measure_id: "B59DCD68-96FF-4B4C-BA69-3707D085C407"  # Pint (select from dropdown)
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
- `account_name`: (Optional) The name of your Drinkaware account (as entered during setup) - leave empty to refresh all accounts
- `entry_id`: (Optional) The Drinkaware config entry ID (only needed if account name is not specified)

**Example:**
```yaml
service: drinkaware.refresh
data:
  account_name: "Bruce"
```

## Available Drinks

The following drink types are available in the Drinkaware API and can be selected from the dropdown menu when using services:

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

The following measures are available for different drink types and can be selected from the dropdown menu:

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

### Measure Compatibility

Not all measures are compatible with all drink types. For example, you can't log a pint of wine or a wine glass of beer. The service dropdown menus will automatically filter compatible options, but if you're entering IDs manually, ensure the measure is appropriate for the drink type.

## Custom Drinks

The Drinkaware integration supports both predefined drink types and custom drinks that may be created in the Drinkaware app.

### Understanding Custom Drinks

Custom drinks are created within the Drinkaware app and are assigned unique IDs that work just like the predefined drink types. From the perspective of Home Assistant, there's no functional difference between a predefined drink type and a custom drink - both are identified by UUIDs.

### Using Custom Drink IDs in Service Calls

Since version 0.3.0, you can directly use custom drink IDs in service calls:

1. When calling the `log_drink` or `delete_drink` service, select "Custom drink ID (enter manually)" from the "Select drink type" dropdown
2. Enter your custom drink ID in the "Custom Drink ID" field
3. Select the appropriate measure from the measures dropdown
4. Fill in the remaining fields as needed

### How to Find Custom Drink IDs

To find the ID of a custom drink:

1. Go to Developer Tools > States in Home Assistant
2. Find and select the Drinkaware "Drinks Today" sensor (it will be named like `sensor.drinkaware_[account_name]_drinks_today`)
3. In the **Attributes** section, look for:
   - `custom_drinks_reference` - A user-friendly list of custom drinks with their IDs
   - `available_custom_drinks` - A more detailed list with complete information

Each drink in the `custom_drinks_reference` list includes:
- `name` - The name of the drink
- `drink_id` - The ID you need to use in service calls
- `abv` - The alcohol percentage
- `measures` - Available measures with their IDs

### Creating Custom Drinks with Different ABV and Names

Since version 0.2.0, you can provide a custom name when logging a drink with a custom ABV. This allows you to create personalized drink names that will appear in your tracking:

```yaml
service: drinkaware.log_drink
data:
  account_name: "Bruce"
  drink_type_selector: "standard"
  drink_id: "FAB60DBF-911F-4286-9C3E-0F0BCB40E3B7"  # Lager
  measure_id: "B59DCD68-96FF-4B4C-BA69-3707D085C407"  # Pint
  abv: 5.2  # Different from default 4.0%
  name: "Craft IPA from Local Brewery"  # Custom name for this drink
  quantity: 1
```

This will create a custom version of Lager with 5.2% ABV and the name "Craft IPA from Local Brewery". The custom drink will be cached and can be used again. Note that:

- The custom name only works when also specifying a custom ABV
- The name appears in the Drinkaware app and in the "Drinks Today" sensor
- If you don't provide a name but do provide custom ABV, it will use the original drink name

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
          drink_type_selector: "standard"
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
          drink_type_selector: "standard"
          drink_id: "19E82B28-9AD5-4546-A966-13B27EC6E4FB"  # Red Wine
          measure_id: "E586C800-24CA-4942-837A-4CD2CBF8338A"  # Medium glass
          quantity: "{{ quantity }}"
          auto_remove_dfd: true
```

### Helper Script for Custom Drink

```yaml
script:
  log_custom_drink:
    alias: "Log a custom drink"
    description: "Log a custom drink to Drinkaware using its ID"
    fields:
      drink_id:
        description: "Custom drink ID"
        example: "12345678-ABCD-1234-5678-123456789ABC"
      measure_id:
        description: "Measure ID"
        example: "B59DCD68-96FF-4B4C-BA69-3707D085C407"
      quantity:
        description: "Number of drinks"
        example: 1
    sequence:
      - service: drinkaware.log_drink
        data:
          account_name: "Bruce"
          drink_type_selector: "custom"
          custom_drink_id: "{{ drink_id }}"
          measure_id: "{{ measure_id }}"
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

### Tracking Longest Drink-Free Streak

```yaml
automation:
  - alias: "Update Longest Drink-Free Streak Helper"
    trigger:
      - platform: state
        entity_id: sensor.drinkaware_bruce_drink_free_streak
    action:
      - condition: template
        value_template: >
          {{ states('sensor.drinkaware_bruce_drink_free_streak')|int > states('input_number.longest_drink_free_streak')|int }}
      - service: input_number.set_value
        target:
          entity_id: input_number.longest_drink_free_streak
        data:
          value: "{{ states('sensor.drinkaware_bruce_drink_free_streak') }}"
```

## Troubleshooting

### Authentication Issues

#### "Cannot find authorization code in URL"

**Problem:** During OAuth setup, you receive an error about missing authorization code.

**Solution:**
1. Make sure you're copying the URL from your browser's developer tools correctly:
   - Press F12 to open Developer Tools
   - Go to the Network tab
   - Look for a request with "callback" in the name (usually the one that's shown as canceled or redirected)
   - Right-click on this request and select "Copy URL"
   - The URL should start with `uk.co.drinkaware.drinkaware://` and contain a `code=` parameter
2. Make sure you're pasting the complete URL including all parameters

### API Issues

#### "Rate limit exceeded"

**Problem:** You see errors about exceeding rate limits.

**Solution:**
- The integration is making too many requests to the Drinkaware API
- The integration will automatically wait and retry after the suggested delay
- Consider spacing out your service calls or automations
- Reduce the frequency of automations that call Drinkaware services

#### "Failed to log drink-free day: Cannot set drink-free day if day has drinks added"

**Problem:** You're trying to set a drink-free day for a date that already has drinks logged.

**Solution:**
1. Set the `remove_drinks` parameter to `true` when calling the service:
   ```yaml
   service: drinkaware.log_drink_free_day
   data:
     account_name: "Bruce"
     date: "2025-04-18"
     remove_drinks: true
   ```
2. If that doesn't work, first manually remove all drinks for that day using the Drinkaware app or the `delete_drink` service

### Service Issues

#### "Extra keys not allowed" or "Required key not provided" when using services

**Problem:** When trying to use `log_drink` or `delete_drink` service, you get errors about extra keys or required keys.

**Solution:**
1. Make sure you're using the correct parameter names and structure:
   - For standard drinks: use `drink_type_selector: "standard"` and `drink_id: "UUID"`
   - For custom drinks: use `drink_type_selector: "custom"` and `custom_drink_id: "UUID"`
2. Don't provide both `drink_id` and `custom_drink_id` in the same service call
3. If using the YAML service editor, ensure all fields match exactly what's expected

#### Custom Drink IDs Not Working

**Problem:** When trying to use a custom drink ID, it doesn't work or gives errors.

**Solution:**
1. Verify you're using the correct UUID format for the drink ID
2. Make sure you've set `drink_type_selector: "custom"` and provided the ID in the `custom_drink_id` field
3. Refresh the Drinkaware data to ensure the custom drinks are up to date
4. Check if the custom drink exists in your Drinkaware account by looking at the "Drinks Today" sensor attributes
5. If the custom drink was recently created in the app, it might take time to appear in the integration

### Debug Logging

To enable detailed debug logging for the integration:

1. Add the following to your `configuration.yaml`:
   ```yaml
   logger:
     default: info
     logs:
       custom_components.drinkaware: debug
   ```
2. Restart Home Assistant
3. Check the logs for detailed information about any issues

## Privacy and Security

### Data Storage

This integration stores:
- OAuth tokens for authentication with the Drinkaware API
- Account name and email as provided during setup
- A cache of drinks and activities for improved performance

All data is stored locally in your Home Assistant instance and is not shared with third parties.

### API Communication

The integration communicates directly with the Drinkaware API using HTTPS. No data is sent to other servers or services.

### OAuth Security

The OAuth authentication flow uses industry-standard PKCE (Proof Key for Code Exchange) to ensure secure token exchange, protecting your Drinkaware credentials.

## Version History

- **0.3.0** - Added support for custom drink IDs in service UI
- **0.2.1** - Added validation for drink and measure compatibility
- **0.2.0** - Added ability to set custom names for drinks when specifying custom ABV
- **0.1.8** - Added dropdown menus for drink and measure selection in services
- **0.1.7** - Fixed issues with custom drink measure descriptions and drink-free day functionality
- **0.1.6** - Previous release		  