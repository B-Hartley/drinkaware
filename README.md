# Drinkaware Integration for Home Assistant

This custom integration allows you to connect your Drinkaware account to Home Assistant, enabling you to track your alcohol consumption data, risk assessments, and goals as sensors within your smart home.
I have developed this for personal use and it is not affiliated with or authorized by DrinkAware, so use at your own risk.

## Features

- Display your Drinkaware risk level assessment
- Track drink-free days and streaks
- Monitor weekly unit consumption
- Track goal progress
- View your self-assessment scores
- See detailed list of drinks consumed today
- Log new drinks and drink-free days via services
- Remove logged drinks when needed

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

The integration offers two authentication methods:

#### OAuth Authentication (Recommended)

This method uses OAuth to authenticate with Drinkaware:

1. Enter a name for your Drinkaware account
2. Choose "Use OAuth" as the authentication method
3. Click the link to authorize Drinkaware
4. Log in with your Drinkaware credentials
5. After successful login, you'll be redirected to a URL that starts with `uk.co.drinkaware.drinkaware://`
6. **Important:** Copy the entire URL from your browser's address bar
7. Paste the copied URL in the next step of the setup process

#### Manual Token Entry

If you have technical knowledge and can extract tokens from the Drinkaware app:

1. Enter a name for your Drinkaware account
2. Choose "Enter token manually" as the authentication method
3. Extract a valid authentication token from the Drinkaware app (using tools like MITM Proxy)
4. Paste the token in the field provided

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

## Services

The integration provides the following services to interact with your Drinkaware account:

### Log Drink-Free Day

Mark a specific day as alcohol-free in your Drinkaware tracking:

```yaml
service: drinkaware.log_drink_free_day
data:
  account_name: "Bruce"  # Or use entry_id instead
  date: "2025-04-18"  # Optional, defaults to today
  remove_drinks: true  # Optional, removes existing drinks first
```

### Log Drink

Record a drink in your Drinkaware tracking:

```yaml
service: drinkaware.log_drink
data:
  account_name: "Bruce"  # Or use entry_id instead
  drink_id: "D4F06BD4-1F61-468B-AE86-C6CC2D56E021"  # Beer
  measure_id: "B59DCD68-96FF-4B4C-BA69-3707D085C407"  # Pint
  abv: 4.5  # Optional
  quantity: 1  # Optional, defaults to 1
  date: "2025-04-18"  # Optional, defaults to today
  auto_remove_dfd: true  # Optional, removes drink-free day mark if present
```

### Delete Drink

Remove a recorded drink from your tracking:

```yaml
service: drinkaware.delete_drink
data:
  account_name: "Bruce"  # Or use entry_id instead
  drink_id: "D4F06BD4-1F61-468B-AE86-C6CC2D56E021"  # Beer
  measure_id: "B59DCD68-96FF-4B4C-BA69-3707D085C407"  # Pint
  date: "2025-04-18"  # Optional, defaults to today
```

### Refresh Data

Manually refresh data from the Drinkaware API:

```yaml
service: drinkaware.refresh
data:
  account_name: "Bruce"  # Or use entry_id instead
```

For more detailed information on available drink types, measures, and advanced usage examples, please refer to the [GUIDE.md](GUIDE.md) file.

## Example Automation

Here's an example of how to use the services in an automation:

```yaml
automation:
  - alias: "Mark Yesterday as Drink-Free at Midnight"
    trigger:
      - platform: time
        at: "00:00:00"
    action:
      - service: drinkaware.log_drink_free_day
        data:
          account_name: "Bruce"
          date: "{{ (now() - timedelta(days=1)).strftime('%Y-%m-%d') }}"
          remove_drinks: true
```

## Troubleshooting

For common issues and troubleshooting tips, please see the [TROUBLESHOOTING.md](TROUBLESHOOTING.md) file.

## Privacy

Your Drinkaware credentials and data are only stored locally in your Home Assistant instance. This integration communicates directly with the Drinkaware API and does not send your data to any third parties.

## Support

If you encounter any issues or have feature requests, please create an issue on the [GitHub repository](https://github.com/B-Hartley/drinkaware/issues).

## Disclaimer

This integration is not officially affiliated with or endorsed by the Drinkaware Trust. It is an independent project developed for the Home Assistant community.

## License

This project is licensed under the MIT License - see the LICENSE file for details.