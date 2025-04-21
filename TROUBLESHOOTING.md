# Drinkaware Integration: Troubleshooting Guide

This comprehensive troubleshooting guide covers common issues you might encounter with the Drinkaware integration and provides detailed solutions for each problem.

## Table of Contents
1. [Installation Issues](#installation-issues)
2. [Authentication Issues](#authentication-issues)
3. [Configuration Issues](#configuration-issues)
4. [Data Refresh Issues](#data-refresh-issues)
5. [Service Call Issues](#service-call-issues)
6. [Sensor Issues](#sensor-issues)
7. [API Limitations](#api-limitations)
8. [Debug Logging](#debug-logging)
9. [Common Error Codes](#common-error-codes)
10. [Updating the Integration](#updating-the-integration)

## Installation Issues

### Integration Not Found in HACS

**Problem:** The Drinkaware integration doesn't appear in HACS.

**Solution:**
1. Make sure you've added it as a custom repository:
   - Go to HACS → Integrations → ⋮ (menu) → Custom Repositories
   - Add `https://github.com/B-Hartley/drinkaware` as a repository
   - Category: Integration
2. Refresh HACS by clicking the refresh button in the top right
3. Search for "Drinkaware" again

### Custom Component File Structure Issues

**Problem:** After manual installation, the integration doesn't appear in Home Assistant.

**Solution:**
1. Check that the files are in the correct location:
   - Files should be in `custom_components/drinkaware/`
   - Ensure `__init__.py`, `config_flow.py`, etc. are directly in that folder
2. Verify the structure matches the repository structure
3. Restart Home Assistant completely (not just a UI refresh)
4. Check the Home Assistant logs for any errors related to loading the custom component

## Authentication Issues

### Cannot Find Authorization Code in URL

**Problem:** During OAuth setup, you receive an error about missing authorization code.

**Solution:**
1. Make sure you're copying the URL from your browser's developer tools correctly:
   - Press F12 to open Developer Tools
   - Go to the Network tab
   - Look for a request with "callback" in the name (usually the one that's shown as canceled or redirected)
   - Right-click on this request and select "Copy URL"
   - The URL should start with `uk.co.drinkaware.drinkaware://` and contain a `code=` parameter
2. Make sure you're pasting the complete URL including all parameters
3. If you can't find the callback request:
   - Make sure you've completed the login and reached the page that won't load
   - Try doing a search in the Network tab for "callback" or "code"
   - Try clearing your browser cache and starting the process again

### Token Refresh Failed or Invalid Refresh Token

**Problem:** The integration fails to refresh the OAuth token, showing errors in the logs.

**Solution:**
1. The OAuth token may have expired or been invalidated (tokens typically last 30-60 days)
2. Go to Settings → Devices & Services
3. Find Drinkaware and click "Configure"
4. Re-authenticate with your Drinkaware account
5. If the problem persists, try removing the integration completely and setting it up again

### Already Authenticated in Browser

**Problem:** When clicking the authorization link, it immediately redirects without showing a login page.

**Solution:**
1. You may already be logged into Drinkaware in your browser
2. Either log out of Drinkaware first, or:
3. Try opening the authorization link in an incognito/private browser window
4. Alternatively, clear cookies for the domain `login.drinkaware.co.uk`

## Configuration Issues

### Multiple Accounts Confusion

**Problem:** You have multiple Drinkaware accounts configured and they're getting confused.

**Solution:**
1. Make sure to give each account a unique and descriptive name during setup
2. When using services, always specify the correct `account_name` parameter
3. Use the `get_coordinator_by_name_or_id` function properly in your scripts/automations
4. If needed, you can find the entry_id for each account in your Home Assistant configuration files or by inspecting the entity attributes

### Entity Names Are Too Long

**Problem:** Entity names like `sensor.drinkaware_your_long_account_name_weekly_units` are unwieldy.

**Solution:**
1. Use shorter account names when setting up the integration
2. Create template sensors with shorter names:
   ```yaml
   template:
     - sensor:
         - name: "Weekly Units"
           state: "{{ states('sensor.drinkaware_your_long_account_name_weekly_units') }}"
           attributes:
             attribution: Drinkaware
   ```
3. Use entity_id overrides in customize.yaml:
   ```yaml
   sensor.drinkaware_your_long_account_name_weekly_units:
     friendly_name: Weekly Units
   ```

## Data Refresh Issues

### Data Not Updating Automatically

**Problem:** Sensors aren't updating with the latest information from the Drinkaware app.

**Solution:**
1. The integration refreshes data every hour by default
2. You can manually trigger a refresh:
   ```yaml
   service: drinkaware.refresh
   data:
     account_name: "YourAccountName"
   ```
3. Set up an automation to refresh more frequently if needed:
   ```yaml
   automation:
     - alias: "Refresh Drinkaware data every 30 minutes"
       trigger:
         - platform: time_pattern
           minutes: "/30"
       action:
         - service: drinkaware.refresh
           data:
             account_name: "YourAccountName"
   ```
4. Check the Home Assistant logs for any errors during refresh

### Changes Made in App Not Appearing

**Problem:** Drinks or settings changed in the Drinkaware app aren't reflecting in Home Assistant.

**Solution:**
1. Manual changes in the app may take time to propagate to the API
2. Force a refresh with the `drinkaware.refresh` service
3. If changes still don't appear, restart Home Assistant
4. Verify the changes are visible in the Drinkaware app itself
5. Enable debug logging to see what data is being received from the API

## Service Call Issues

### Using Custom Drink IDs

**Problem:** You're having trouble using custom drink IDs in service calls.

**Solution:**
1. Make sure you're using the correct format for the service call:
   ```yaml
   service: drinkaware.log_drink
   data:
     account_name: "YourAccountName"
     custom_drink_id: "12345678-ABCD-1234-5678-123456789ABC"
     measure_id: "B59DCD68-96FF-4B4C-BA69-3707D085C407"
   ```
2. Provide the custom drink ID in the `custom_drink_id` field
3. To find custom drink IDs, check the `custom_drinks_reference` attribute in the "Drinks Today" sensor
4. If you've just created a custom drink in the app, refresh the integration to update the available drinks

### Service Schema Validation Errors

**Problem:** When trying to use `log_drink` or `delete_drink` service, you get validation errors.

**Solution:**
1. Make sure you're using the correct parameter names and structure:
   - For standard drinks: use `drink_id: "UUID"`
   - For custom drinks: use `custom_drink_id: "UUID"`
2. Don't provide both `drink_id` and `custom_drink_id` in the same service call (the standard drink will take precedence if both are provided)
3. If using the YAML service editor, ensure all fields match exactly what's expected

### Can't See Dropdown Menus in Service UI

**Problem:** The service UI doesn't show dropdown menus for drink types and measures.

**Solution:**
1. Make sure you're running the latest version of the integration
2. Clear your browser cache or try a different browser
3. Restart Home Assistant
4. If you still don't see the dropdowns, try reinstalling the integration
5. Verify the services.yaml file is correctly installed in your custom_components directory

### Failed to Log Drink-Free Day When Drinks Exist

**Problem:** You try to set a drink-free day for a date that already has drinks logged.

**Solution:**
1. Set the `remove_drinks` parameter to `true` when calling the service:
   ```yaml
   service: drinkaware.log_drink_free_day
   data:
     account_name: "YourAccountName"
     date: "2025-04-18"
     remove_drinks: true
   ```
2. If that doesn't work, manually delete all drinks for that day first:
   ```yaml
   # First delete all drinks
   service: drinkaware.delete_drink
   data:
     account_name: "YourAccountName"
     drink_id: "D4F06BD4-1F61-468B-AE86-C6CC2D56E021"  # The ID of your drink
     measure_id: "B59DCD68-96FF-4B4C-BA69-3707D085C407"  # The measure ID
     date: "2025-04-18"
   
   # Then mark as drink-free
   service: drinkaware.log_drink_free_day
   data:
     account_name: "YourAccountName"
     date: "2025-04-18"
   ```
3. If problems persist, check the logs for detailed error information

### Unknown Measure ID or Incompatible Measure

**Problem:** You get errors about unknown measure IDs or incompatible measures.

**Solution:**
1. Not all measures are compatible with all drink types (e.g., you can't use wine glass measures with beer)
2. Verify you're using a compatible measure for the drink type
3. Check the DRINK_MEASURE_COMPATIBILITY in the integration code
4. Use the measure IDs listed in the documentation for standard drinks
5. For custom drinks, try to determine the original drink type and use compatible measures

## Sensor Issues

### Missing Sensor Data or Null Values

**Problem:** Some sensors show "unknown," "unavailable," or null values.

**Solution:**
1. The sensor may rely on data that isn't available in your Drinkaware account
2. For example, risk assessment data requires completing a self-assessment in the app
3. Check the sensor's attributes to see if there's any partial data
4. Verify the corresponding data is visible in the Drinkaware app
5. Force a refresh with the `drinkaware.refresh` service
6. If the problem persists, enable debug logging and check the logs

### Incorrect Weekly Units Calculation

**Problem:** The weekly units sensor doesn't match what's shown in the Drinkaware app.

**Solution:**
1. Check the date range being used for calculation:
   - The integration calculates units from the current day back 7 days
   - The app might use a different date range (e.g., Monday-Sunday)
2. Check the raw data in the sensor attributes to see daily breakdown
3. If some days are missing, force a refresh
4. If the discrepancy persists, check the logs when debug logging is enabled
5. Note that there can be slight differences due to rounding or calculation methods

### Drinks Today Sensor Not Showing Detailed Information

**Problem:** The "Drinks Today" sensor shows a count but no detailed drink information in attributes.

**Solution:**
1. Make sure you're running the latest version of the integration
2. Try manually refreshing the data
3. If drinks were just added, wait a few minutes for the data to update
4. Check if the detailed drink information is visible in the Drinkaware app
5. If you added drinks via the integration, verify the service call was successful
6. Enable debug logging to see what activity data is being fetched

### Custom Drinks Not Appearing in Sensor Attributes

**Problem:** Custom drinks you've created don't appear in sensor attributes.

**Solution:**
1. Force a refresh with the `drinkaware.refresh` service
2. Custom drinks should appear in the `available_custom_drinks` and `custom_drinks_reference` attributes of the "Drinks Today" sensor
3. If not appearing, try logging the custom drink in the Drinkaware app
4. Wait a few hours for the Drinkaware cache to update
5. In version 0.3.0+, the integration periodically refreshes the drinks cache
6. Check if the custom drink appears in the Drinkaware app itself

## API Limitations

### Rate Limit Exceeded

**Problem:** You see "Rate limit exceeded" errors in the logs.

**Solution:**
- The integration is making too many requests to the Drinkaware API
- The integration will automatically wait and retry after the suggested delay
- Consider spacing out your service calls or automations
- Reduce the frequency of automations that call Drinkaware services
- Implement a cooldown period between service calls:
  ```yaml
  automation:
    - alias: "Log drink with delay"
      trigger:
        - platform: event
          event_type: drink_logged
      action:
        - delay:
            seconds: 5
        - service: drinkaware.log_drink
          data:
            account_name: "YourAccountName"
            drink_type_selector: "standard"
            drink_id: "..."
            measure_id: "..."
  ```

### API Endpoint Errors

**Problem:** You see errors like "404 Not Found" or "400 Bad Request" for API endpoints.

**Solution:**
1. The API might have changed or the endpoint might be temporarily unavailable
2. Check if your integration version is the latest
3. Try restarting Home Assistant
4. If the problem persists, it might be an issue with the Drinkaware API itself
5. Check the GitHub issues page to see if others are experiencing the same problem
6. Consider reporting the issue if it seems like an integration bug

### Authentication Token Expired

**Problem:** You see "401 Unauthorized" errors in the logs about expired tokens.

**Solution:**
1. The integration should automatically refresh tokens when they expire
2. If auto-refresh fails, try reconfiguring the integration
3. If problems persist, check if your Drinkaware account is still active
4. Try logging out and back in to the Drinkaware app
5. As a last resort, delete and reinstall the integration

## Debug Logging

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

To access the logs:
- Go to Settings → System → Logs
- Look for entries with `custom_components.drinkaware`
- You can filter the logs by typing "drinkaware" in the search box

The debug logs will show:
- API requests and responses
- Token refresh attempts
- Data parsing results
- Service call processing

## Common Error Codes

Here are some common error codes you might see in the logs and what they mean:

- **400 (Bad Request)** - Usually means there's an issue with the parameters sent to the API
  - Check if you're using valid IDs for drinks and measures
  - Verify date formats are correct (YYYY-MM-DD)
  - Check if ABV values are within valid ranges

- **401 (Unauthorized)** - Authentication token is invalid or expired
  - The integration should automatically refresh tokens
  - Try reconfiguring the integration if problems persist

- **403 (Forbidden)** - The token doesn't have permission for the requested action
  - Check if your Drinkaware account has the necessary permissions
  - Try logging in to the Drinkaware app to verify account status

- **404 (Not Found)** - Resource not found, possibly wrong ID or date
  - Verify you're using a valid drink ID or measure ID
  - Check if the date format is correct
  - Ensure the date isn't too far in the past (the API may limit historical data)

- **429 (Too Many Requests)** - Rate limit exceeded
  - The integration will automatically retry after waiting
  - Reduce the frequency of your service calls
  - Space out automations that call Drinkaware services

## Updating the Integration

### Update Failed to Install

**Problem:** HACS shows errors when trying to update the integration.

**Solution:**
1. Try updating through HACS UI again
2. If that fails, try manually removing and reinstalling the integration
3. Check for conflicts with other custom components
4. Verify there's enough disk space on your Home Assistant instance
5. Check GitHub for any known issues with the latest version

### Breaking Changes After Update

**Problem:** After updating, automations or scripts stop working.

**Solution:**
1. Check the release notes for breaking changes
2. Since version 0.3.0, the service parameters have changed to use `drink_type_selector` and separate fields for standard and custom drinks
3. Update your scripts and automations to use the new parameter structure:
   ```yaml
   # Before (version 0.2.x and earlier):
   service: drinkaware.log_drink
   data:
     account_name: "YourAccountName"
     drink_id: "D4F06BD4-1F61-468B-AE86-C6CC2D56E021"
     measure_id: "B59DCD68-96FF-4B4C-BA69-3707D085C407"
   
   # After (version 0.3.0+):
   service: drinkaware.log_drink
   data:
     account_name: "YourAccountName"
     drink_type_selector: "standard"
     drink_id: "D4F06BD4-1F61-468B-AE86-C6CC2D56E021"
     measure_id: "B59DCD68-96FF-4B4C-BA69-3707D085C407"
   ```
4. For custom drink IDs, use this format:
   ```yaml
   service: drinkaware.log_drink
   data:
     account_name: "YourAccountName"
     drink_type_selector: "custom"
     custom_drink_id: "12345678-ABCD-1234-5678-123456789ABC"
     measure_id: "B59DCD68-96FF-4B4C-BA69-3707D085C407"
   ```
5. Clear your browser cache to ensure you're seeing the updated UI
6. Restart Home Assistant after updating

### Integration Missing After Update

**Problem:** The integration disappears after an update.

**Solution:**
1. Check if the integration appears in the "Integrations" page
2. Verify the files are still in the correct location (`custom_components/drinkaware/`)
3. Check the Home Assistant logs for errors loading the component
4. Try reinstalling through HACS
5. If all else fails, manually download and install the files

## Still Having Issues?

If you're still experiencing problems after trying these solutions:

1. Check the [GitHub repository](https://github.com/B-Hartley/drinkaware/issues) for similar issues
2. Create a new issue with the following information:
   - The error message from the logs
   - Steps to reproduce the issue
   - The version of Home Assistant you're using
   - The version of the Drinkaware integration
   - Any relevant configuration snippets (with sensitive information removed)

## Contact

For additional support, you can:
- Open an issue on GitHub: https://github.com/B-Hartley/drinkaware/issues
- Contact the developer via the repository
- Share your problem in the Home Assistant community forums

Remember that this is a community-developed integration not officially affiliated with Drinkaware, so response times may vary.