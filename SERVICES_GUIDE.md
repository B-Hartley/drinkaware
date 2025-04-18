# Drinkaware Integration Services

The Drinkaware integration provides services that allow you to log drink-free days, record drinks, and manually refresh data from the Drinkaware API.

## Available Services

### 1. Log Drink-Free Day (`drinkaware.log_drink_free_day`)

This service allows you to mark a specific day as alcohol-free in your Drinkaware tracking.

**Parameters:**
- `entry_id`: (Required) The Drinkaware config entry ID to use
- `date`: (Optional) The date to mark as a drink-free day (defaults to today)

**Example:**
```yaml
service: drinkaware.log_drink_free_day
data:
  entry_id: abc123
  date: "2025-04-18"
```

### 2. Log Drink (`drinkaware.log_drink`)

This service allows you to record a drink in your Drinkaware tracking.

**Parameters:**
- `entry_id`: (Required) The Drinkaware config entry ID to use
- `drink_id`: (Required) The drink type ID from Drinkaware API
- `measure_id`: (Required) The measure ID from Drinkaware API
- `abv`: (Optional) The alcohol percentage (will use default if not specified)
- `quantity`: (Optional) The number of drinks of this type (defaults to 1)
- `date`: (Optional) The date to log the drink (defaults to today)

**Example:**
```yaml
service: drinkaware.log_drink
data:
  entry_id: abc123
  drink_id: "FAB60DBF-911F-4286-9C3E-0F0BCB40E3B7"  # Lager
  measure_id: "B59DCD68-96FF-4B4C-BA69-3707D085C407"  # Pint
  abv: 4.5
  quantity: 2
  date: "2025-04-18"
```

### 3. Refresh Data (`drinkaware.refresh`)

This service allows you to manually refresh data from the Drinkaware API.

**Parameters:**
- `entry_id`: (Required) The Drinkaware config entry ID to use

**Example:**
```yaml
service: drinkaware.refresh
data:
  entry_id: abc123
```

## Finding Drink and Measure IDs

To use the `log_drink` service effectively, you need to know the correct `drink_id` and `measure_id` values. The Drinkaware API provides these IDs, and you can find common ones from the integration's logs.

Some common drink types and their IDs from the MITM logs:

### Drink Types (drink_id)
- Lager: `FAB60DBF-911F-4286-9C3E-0F0BCB40E3B7`
- Beer: `D4F06BD4-1F61-468B-AE86-C6CC2D56E021`
- Cider: `61AD633A-7366-4497-BD36-9078466F00FE`
- White Wine: `E3DEDBFD-63CE-492D-8E3E-9C24010227D8`
- Red Wine: `19E82B28-9AD5-4546-A966-13B27EC6E4FB`
- Vodka: `0E3CA732-21D6-4631-A60C-155C2BB85C18`
- Gin: `FECCEBB8-68D1-4BF1-B42F-7BB6C919B0F0`
- Tequila: `32B22A73-D900-43E1-AAB6-8ADC27590B5D`
- Rum: `780B45E2-26D6-4F55-A0C1-75868835D672`
- Whiskey: `2AAE4A2E-8C0A-40E1-BCDE-EB986111D2DE`
- Alcopop: `0B2A65CA-5EC4-46B6-9E4D-6E0DDC8D57B8`
- Champagne: `61C3F476-24D1-46DB-9FA0-613ED4082531`
- Prosecco: `5184149E-450E-4A63-92E5-19AD7F49FCD1`
- Port/Sherry: `F8486573-6F92-4B63-BAEB-3E76B750E14D`

### Measure Types (measure_id)
- Pint: `B59DCD68-96FF-4B4C-BA69-3707D085C407`
- Half pint: `174F45D7-745A-45F0-9D44-88DA1075CE79`
- Small bottle/can: `6B56A1FB-33A1-4E51-BED7-536751DE56BC`
- Bottle/can: `0CB11B53-6E3C-4C47-A2E9-68BA40DFFE13`
- Bottle: `8F185B18-2A82-4D1A-A1F7-20E01D5E2FEC`
- Large bottle: `03D87F35-A1DF-40EE-9398-FA1CA55DD894`
- Single measure (spirits): `A83406D4-741F-49B4-B310-8B7DEB8B072F`
- Double measure (spirits): `FCCC81A2-3BFF-45C0-832F-BCF73E81D0D1`
- Small glass (wine): `0E40AE5F-098D-4826-ADCA-298A6A14F514`
- Medium glass (wine): `E586C800-24CA-4942-837A-4CD2CBF8338A`
- Large glass (wine): `6450132A-F73F-414A-83BB-43C37B40272F`

## Using a Helper Script

Since the drink and measure IDs are not very user-friendly, you might want to create an automation or script that makes it easier to log drinks. Here's an example script that you can use:

```yaml
script:
  log_beer:
    alias: "Log a Beer"
    description: "Log a pint of beer to Drinkaware"
    fields:
      quantity:
        description: "Number of beers"
        example: 1
      abv:
        description: "Alcohol percentage"
        example: 4.5
    sequence:
      - service: drinkaware.log_drink
        data:
          entry_id: !secret drinkaware_entry_id
          drink_id: "D4F06BD4-1F61-468B-AE86-C6CC2D56E021"  # Beer
          measure_id: "B59DCD68-96FF-4B4C-BA69-3707D085C407"  # Pint
          quantity: "{{ quantity }}"
          abv: "{{ abv }}"
```

## Automations

You can integrate these services into automations to automatically track your drinking habits. For example:

### Mark Yesterday as Drink-Free if No Drinks Were Logged

```yaml
automation:
  - alias: "Mark yesterday as drink-free if no drinks logged"
    trigger:
      - platform: time
        at: "01:00:00"
    condition:
      # Add your own condition to check if no drinks were logged yesterday
      # This might involve checking a sensor or counter
    action:
      - service: drinkaware.log_drink_free_day
        data:
          entry_id: !secret drinkaware_entry_id
          date: "{{ (now() - timedelta(days=1)).strftime('%Y-%m-%d') }}"
```

### Refresh Drinkaware Data Periodically

```yaml
automation:
  - alias: "Refresh Drinkaware data hourly"
    trigger:
      - platform: time_pattern
        hours: "/1"
    action:
      - service: drinkaware.refresh
        data:
          entry_id: !secret drinkaware_entry_id
```

## Note on API Limitations

The Drinkaware API may have rate limiting in place, so avoid making too many service calls in a short period of time. If you encounter errors, check the Home Assistant logs for more information.