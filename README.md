# Drinkaware Integration for Home Assistant

This custom integration allows you to connect your Drinkaware account to Home Assistant, enabling you to track your alcohol consumption data, risk assessments, and goals as sensors within your smart home.
I have developed this for personal use and it is not authorised by DrinkAware so use at your own risk.  Hopefully they don't mind !

## Features

- Display your Drinkaware risk level assessment
- Track drink-free days and streaks
- Monitor weekly unit consumption
- Track goal progress
- View your self-assessment scores
- And more!

## Installation

### Method 1: HACS (Recommended)

1. Make sure you have [HACS](https://hacs.xyz/) installed
2. Add this repository as a custom repository in HACS:
   - Go to HACS → Integrations → ⋮ (menu) → Custom Repositories
   - Add `https://github.com/yourusername/hass-drinkaware` as a repository
   - Category: Integration
3. Click "Install" on the Drinkaware integration
4. Restart Home Assistant

### Method 2: Manual Installation

1. Download the latest release from the [Releases](https://github.com/yourusername/hass-drinkaware/releases) page
2. Extract the `drinkaware` folder from the release into your `custom_components` directory
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
6. Your browser might show an error like "Can't open this page" - this is normal!
7. **Important:** Copy the entire URL from your browser's address bar
   - If you can't see the full URL, open your browser's developer tools (F12), go to the Network tab, and look for the redirect URL
8. Paste the copied URL in the next step of the setup process

**Troubleshooting tip:** If you've previously logged into Drinkaware in your browser, you might need to clear your browser cookies for `login.drinkaware.co.uk` before starting this process.

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

## Services

The integration provides the following services to interact with your Drinkaware account:

### Log Drink-Free Day

Mark a specific day as alcohol-free in your Drinkaware tracking:

```yaml
service: drinkaware.log_drink_free_day
data:
  entry_id: YOUR_ENTRY_ID
  date: "2025-04-18"  # Optional, defaults to today
```

### Log Drink

Record a drink in your Drinkaware tracking:

```yaml
service: drinkaware.log_drink
data:
  entry_id: YOUR_ENTRY_ID
  drink_id: "FAB60DBF-911F-4286-9C3E-0F0BCB40E3B7"  # Lager
  measure_id: "B59DCD68-96FF-4B4C-BA69-3707D085C407"  # Pint
  abv: 4.5  # Optional
  quantity: 1  # Optional, defaults to 1
  date: "2025-04-18"  # Optional, defaults to today
```

### Refresh Data

Manually refresh data from the Drinkaware API:

```yaml
service: drinkaware.refresh
data:
  entry_id: YOUR_ENTRY_ID
```

For detailed information on available drink types and measures, as well as advanced usage examples, please refer to the `SERVICES_GUIDE.md` and `AVAILABLE_DRINKS.md` files.

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
          entry_id: !secret drinkaware_entry_id
          date: "{{ (now() - timedelta(days=1)).strftime('%Y-%m-%d') }}"
```

## Troubleshooting

### Common Issues

#### "Cannot find authorization code in URL"
- Make sure you're copying the entire URL after redirection
- Check for the `code=` parameter in the URL
- Try using your browser's developer tools to see the network requests

#### "Token refresh failed"
- Your authentication token may have expired
- Try removing the integration and setting it up again

#### "Rate limit exceeded"
- The integration is making too many requests to the Drinkaware API
- This should resolve automatically as the integration will wait before retrying

### Debug Logging

To enable debug logging for the integration:

1. Add the following to your `configuration.yaml`:
   ```yaml
   logger:
     default: info
     logs:
       custom_components.drinkaware: debug
   ```
2. Restart Home Assistant
3. Check the logs for detailed information about any issues

## Privacy

Your Drinkaware credentials and data are only stored locally in your Home Assistant instance. This integration communicates directly with the Drinkaware API and does not send your data to any third parties.

## Support

If you encounter any issues or have feature requests, please create an issue on the [GitHub repository](https://github.com/yourusername/hass-drinkaware/issues).

## License

This project is licensed under the MIT License - see the LICENSE file for details.
