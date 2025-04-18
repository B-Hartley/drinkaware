"""
Drinkaware integration for Home Assistant.
"""
import asyncio
import logging
from datetime import datetime, timedelta
import json
import aiohttp
import re

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)
from homeassistant.const import CONF_TOKEN
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.components.http import HomeAssistantView

from .const import (
    DOMAIN,
    SCAN_INTERVAL_HOURS,
    API_BASE_URL,
    OAUTH_TOKEN_URL,
    OAUTH_CLIENT_ID,
    ENDPOINT_SELF_ASSESSMENT,
    ENDPOINT_STATS,
    ENDPOINT_GOALS,
    ENDPOINT_SUMMARY,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]

async def async_setup(hass: HomeAssistant, config):
    """Set up the Drinkaware component."""
    # Just to initialize the domain in hass.data
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Drinkaware from a config entry."""
    # Get the OAuth token from the entry
    token_data = entry.data["token"]
    account_name = entry.data.get("account_name", "Default")
    email = entry.data.get("email", "unknown_user")
    
    # Create session
    session = async_get_clientsession(hass)
    
    # Create coordinator
    coordinator = DrinkAwareDataUpdateCoordinator(
        hass, session, token_data, entry.entry_id, account_name, email
    )
    
    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()
    
    # Store coordinator in hass.data
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator
    
    # Set up platforms - FIXED: Using async_forward_entry_setups instead of individual tasks
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
        
    # Set up entry refresh listener for token
    entry.async_on_unload(entry.add_update_listener(update_listener))
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
        
    return unload_ok

async def update_listener(hass, entry):
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)

class DrinkAwareDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Drinkaware data."""

    def __init__(self, hass, session, token_data, entry_id, account_name, email):
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{entry_id}",
            update_interval=timedelta(hours=SCAN_INTERVAL_HOURS),
        )
        self.session = session
        self.token_data = token_data
        self.access_token = token_data["access_token"]
        self.token_expiry = datetime.now() + timedelta(seconds=token_data.get("expires_in", 3600))
        self.refresh_token = token_data.get("refresh_token")
        self.entry_id = entry_id
        self.account_name = account_name
        self.email = email

    async def _async_update_data(self):
        """Fetch data from Drinkaware API."""
        # Check if token needs refreshing
        if datetime.now() >= self.token_expiry and self.refresh_token:
            await self._refresh_token()
            
        try:
            data = {}
            
            # Get self assessment data
            assessment = await self._fetch_self_assessment()
            if assessment and "assessments" in assessment and assessment["assessments"]:
                data["assessment"] = assessment["assessments"][0]
            
            # Add a small delay between API calls to prevent rate limiting
            await asyncio.sleep(1)
            
            # Get tracking stats
            stats = await self._fetch_stats()
            if stats:
                data["stats"] = stats
                
            # Add a small delay between API calls to prevent rate limiting
            await asyncio.sleep(1)
            
            # Get active goals
            goals = await self._fetch_goals()
            if goals and "goals" in goals:
                data["goals"] = goals["goals"]
                
            # Add a small delay between API calls to prevent rate limiting
            await asyncio.sleep(1)
            
            # Get recent drink summary
            summary = await self._fetch_summary()
            if summary and "activitySummaryDays" in summary:
                data["summary"] = summary["activitySummaryDays"]
                
            return data
            
        except Exception as err:
            _LOGGER.error("Error fetching data from Drinkaware: %s", err)
            # If we get an auth error, try to refresh token
            if "401" in str(err) and self.refresh_token:
                await self._refresh_token()
                # Retry the update after token refresh, but with a delay to prevent rate limiting
                await asyncio.sleep(2)
                return await self._async_update_data()
            return {}

    async def _refresh_token(self):
        """Refresh the OAuth token."""
        try:
            # Use the actual token URL from the CURL commands
            data = {
                "client_id": OAUTH_CLIENT_ID,
                "grant_type": "refresh_token",
                "refresh_token": self.refresh_token,
                # The mobile app may use this redirect URI even for refresh
                "redirect_uri": "uk.co.drinkaware.drinkaware://oauth/callback"
            }
            
            headers = {
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "User-Agent": "Home Assistant Drinkaware Integration/1.0"
            }
            
            _LOGGER.debug("Refreshing token with URL: %s", OAUTH_TOKEN_URL)
            
            async with self.session.post(OAUTH_TOKEN_URL, data=data, headers=headers) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    _LOGGER.error("Token refresh failed: %s", text)
                    # If refresh token is invalid, we might need to trigger reauth
                    if resp.status == 400 and "invalid_grant" in text.lower():
                        _LOGGER.warning("Invalid refresh token. User may need to re-authenticate.")
                    return
                    
                token_data = await resp.json()
                _LOGGER.debug("Token refresh response received")
                
                self.token_data = token_data
                self.access_token = token_data["access_token"]
                self.token_expiry = datetime.now() + timedelta(seconds=token_data.get("expires_in", 3600))
                
                if "refresh_token" in token_data:
                    self.refresh_token = token_data["refresh_token"]
                    
                # Update config entry with new token data
                config_entries = self.hass.config_entries
                entry = config_entries.async_get_entry(self.entry_id)
                
                if entry:
                    new_data = dict(entry.data)
                    new_data["token"] = token_data
                    self.hass.config_entries.async_update_entry(
                        entry, 
                        data=new_data
                    )
                    
                _LOGGER.debug("Successfully refreshed OAuth token")
                
        except Exception as err:
            _LOGGER.error("Error refreshing OAuth token: %s", err)

    async def _fetch_self_assessment(self):
        """Fetch self assessment data from Drinkaware API."""
        url = f"{API_BASE_URL}{ENDPOINT_SELF_ASSESSMENT}"
        params = {
            "page": 1,
            "resultsPerPage": 1
        }
        
        return await self._make_api_request(url, params)
        
    async def _fetch_stats(self):
        """Fetch tracking stats from Drinkaware API."""
        url = f"{API_BASE_URL}{ENDPOINT_STATS}"
        
        return await self._make_api_request(url)
        
    async def _fetch_goals(self):
        """Fetch goals from Drinkaware API."""
        url = f"{API_BASE_URL}{ENDPOINT_GOALS}"
        params = {
            "page": 1,
            "resultsPerPage": 6
        }
        
        return await self._make_api_request(url, params)
        
    async def _fetch_summary(self):
        """Fetch recent activity summary from Drinkaware API."""
        today = datetime.now()
        two_weeks_ago = today - timedelta(days=14)
        
        url = f"{API_BASE_URL}{ENDPOINT_SUMMARY}/{today.strftime('%Y-%m-%d')}/{two_weeks_ago.strftime('%Y-%m-%d')}"
        params = {
            "aggregation": "weekly"
        }
        
        return await self._make_api_request(url, params)
        
    async def _make_api_request(self, url, params=None):
        """Make authenticated request to Drinkaware API."""
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
            "User-Agent": "Home Assistant Drinkaware Integration/1.0"
        }
        
        try:
            async with self.session.get(url, params=params, headers=headers) as resp:
                if resp.status == 401:
                    # Token expired
                    _LOGGER.debug("API request returned 401, token may have expired")
                    raise Exception("401 Unauthorized - Token expired")
                    
                if resp.status == 429:
                    # Rate limit exceeded
                    text = await resp.text()
                    _LOGGER.warning("Rate limit exceeded: %s", text)
                    
                    # Extract retry-after time (the API suggests how many seconds to wait)
                    retry_after = 1  # Default to 1 second
                    try:
                        # Try to parse from the error message
                        match = re.search(r'Try again in (\d+) seconds', text)
                        if match:
                            retry_after = int(match.group(1))
                    except Exception:
                        pass
                    
                    # Wait for the suggested time and then retry
                    _LOGGER.info("Waiting %s seconds before retrying...", retry_after)
                    await asyncio.sleep(retry_after)
                    return await self._make_api_request(url, params)
                
                if resp.status != 200:
                    text = await resp.text()
                    _LOGGER.error("API request failed: %s - %s", resp.status, text)
                    return None
                    
                return await resp.json()
        except asyncio.TimeoutError:
            _LOGGER.error("Request to %s timed out", url)
            return None
        except Exception as err:
            _LOGGER.error("Error in API request to %s: %s", url, err)
            raise