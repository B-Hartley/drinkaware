# Drinkaware Integration: Troubleshooting Guide

This guide covers common issues you might encounter with the Drinkaware integration and how to resolve them.

## Authentication Issues

### "Cannot find authorization code in URL"

**Problem:** During OAuth setup, you receive an error about missing authorization code.

**Solution:**
1. Make sure you're copying the **entire URL** after redirection
2. Look for the `code=` parameter in the URL
3. Try using your browser's developer tools to see the full network requests:
   - Press F12 to open Developer Tools
   - Go to the Network tab
   - Look for a redirect to `uk.co.drinkaware.drinkaware://`
   - Copy the entire URL from this redirect

**Additional tip:** If you've previously logged into Drinkaware in your browser, try clearing cookies for `login.drinkaware.co.uk` before starting the process.

### "Token refresh failed" or "Invalid refresh token"

**Problem:** The integration fails to refresh the OAuth token.

**Solution:**
1. The OAuth token may have expired or been invalidated
2. Go to Settings → Devices & Services
3. Find Drinkaware and click "Configure"
4. Re-authenticate with your Drinkaware account
5. If this happens repeatedly, try using the manual token entry method instead

## API Issues

### "Rate limit exceeded"

**Problem:** You see errors about exceeding rate limits.

**Solution:**
- The integration is making too many requests to the Drinkaware API
- The integration will automatically wait and retry after the suggested delay
- Consider spacing out your service calls or automations
- Reduce the frequency of automations that call Drinkaware services

### "Failed to log drink-free day: Cannot set drink-free day if day has drinks added"

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

### "Failed to set drink quantity" or "Failed to add drink"

**Problem:** You're unable to log a drink using the service.

**Solution:**
1. Verify the `drink_id` and `measure_id` are correct
2. Check the Home Assistant logs for detailed error messages
3. Try refreshing the data first with the `refresh` service
4. If using a custom drink, verify the ID is correct
5. If nothing else works, try logging the drink in the Drinkaware app

## Sensor Issues

### Stale or outdated data in sensors

**Problem:** Your sensors aren't showing the latest data.

**Solution:**
1. Manually trigger a data refresh:
   ```yaml
   service: drinkaware.refresh
   data:
     account_name: "Bruce"
   ```
2. Check if the Drinkaware app itself shows the correct data
3. If data is still missing, try restarting Home Assistant

### "Drinks Today" sensor not showing detailed drink information

**Problem:** The "Drinks Today" sensor shows a count but no detailed drink information in the attributes.

**Solution:**
1. Make sure you're running the latest version of the integration
2. Try manually refreshing the data
3. If drinks were just added, wait a few minutes for the data to update
4. Check the Home Assistant logs for any errors related to fetching activity data

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

## Common Error Codes

Here are some common error codes you might see in the logs and what they mean:

- **400 (Bad Request)** - Usually means there's an issue with the parameters sent to the API
- **401 (Unauthorized)** - Authentication token is invalid or expired
- **403 (Forbidden)** - The token doesn't have permission for the requested action
- **404 (Not Found)** - Resource not found, possibly wrong ID or date
- **429 (Too Many Requests)** - Rate limit exceeded, wait and try again later

## Still Having Issues?

If you're still experiencing problems after trying these solutions:

1. Check the [GitHub repository](https://github.com/B-Hartley/drinkaware/issues) for similar issues
2. Create a new issue with the following information:
   - The error message from the logs
   - Steps to reproduce the issue
   - The version of Home Assistant you're using
   - The version of the Drinkaware integration

## Contact

For additional support, you can:
- Open an issue on GitHub
- Contact the developer via the repository