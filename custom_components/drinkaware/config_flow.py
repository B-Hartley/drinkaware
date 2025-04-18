"""
Config flow for Drinkaware integration.
"""
import logging
from typing import Any, Dict, Optional
import urllib.parse
import secrets
import hashlib
import base64
import aiohttp
import voluptuous as vol
import re

from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.network import get_url

from .const import (
    DOMAIN,
    API_BASE_URL,
    ENDPOINT_STATS,
)

_LOGGER = logging.getLogger(__name__)

# OAuth endpoints from the URL
OAUTH_CLIENT_ID = "fe14e7b9-d4e1-4967-8fce-617c6f48a055"
OAUTH_AUTHORIZATION_URL = "https://login.drinkaware.co.uk/login.drinkaware.co.uk/B2C_1A_JITMigraion_signup_signin/oauth2/v2.0/authorize"
OAUTH_TOKEN_URL = "https://login.drinkaware.co.uk/login.drinkaware.co.uk/B2C_1A_JITMigraion_signup_signin/oauth2/v2.0/token"
OAUTH_SCOPES = [
    "https://drinkawareproduction.onmicrosoft.com/712d0439-75b8-4dc7-a474-975bf5eced84/tracking.user.read",
    "https://drinkawareproduction.onmicrosoft.com/712d0439-75b8-4dc7-a474-975bf5eced84/tracking.user.write",
    "openid", "profile", "offline_access"
]

class DrinkAwareConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Drinkaware."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL
    
    def __init__(self):
        """Initialize the config flow."""
        self._session = None
        self._code_verifier = None
        self._auth_url = None
        self._user_id = None
        self._account_name = None

    async def async_step_user(self, user_input=None):
        """Handle a flow initiated by the user."""
        errors = {}
        
        if user_input is not None:
            # User has provided an account name
            self._account_name = user_input.get("account_name")
            # Continue to the auth method selection step
            return await self.async_step_auth_method()
                
        # Ask for account name first
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("account_name"): str,
            }),
            errors=errors,
            description_placeholders={
                "instructions": "Please enter a name for this Drinkaware account."
            },
        )

    async def async_step_auth_method(self, user_input=None):
        """Handle authentication method selection."""
        errors = {}
        
        if user_input is not None:
            # User has chosen an option
            if user_input.get("auth_method") == "oauth":
                self._session = async_get_clientsession(self.hass)
                # Generate PKCE code verifier and challenge
                self._code_verifier = secrets.token_urlsafe(64)[:128]
                code_challenge = self._generate_code_challenge(self._code_verifier)
                
                # Generate authorization URL
                self._auth_url = self._get_authorization_url(code_challenge)
                
                return await self.async_step_oauth_auth()
            else:
                return await self.async_step_manual_token()
                
        # Present user with choice of authentication methods
        return self.async_show_form(
            step_id="auth_method",
            data_schema=vol.Schema({
                vol.Required("auth_method", default="oauth"): vol.In({
                    "oauth": "Use OAuth (copy-paste code)",
                    "manual": "Enter token manually"
                })
            }),
            errors=errors,
        )

    async def async_step_oauth_auth(self, user_input=None):
        """Handle OAuth authorization step."""
        if user_input is None:
            return self.async_show_form(
                step_id="oauth_auth",
                description_placeholders={
                    "auth_url": self._auth_url,
                    "instructions": (
                        "1. Click the link below to authorize Drinkaware\n"
                        "2. Log in with your Drinkaware credentials\n"
                        "3. After successful login, you'll be redirected to a page that won't load (this is normal)\n"
                        "4. Copy the ENTIRE URL or redirect text from your browser or dev tools\n"
                        "5. Click Submit below and paste the full redirect URL in the next step"
                    )
                },
            )
        
        return await self.async_step_code()

    async def async_step_code(self, user_input=None):
        """Handle authorization code step."""
        errors = {}
        
        if user_input is not None:
            redirect_url = user_input.get("redirect_url", "")
            
            try:
                # Extract the code using regex pattern matching
                # This handles both regular URLs and custom protocol URIs
                code = self._extract_code_from_url(redirect_url)
                
                if code:
                    # Exchange code for token using PKCE flow with the mobile app redirect URI
                    redirect_uri = "uk.co.drinkaware.drinkaware://oauth/callback"
                    token_info = await self._exchange_code_for_token(code, redirect_uri)
                    
                    # Extract user info from token
                    user_info = self._parse_jwt(token_info["access_token"])
                    self._user_id = user_info.get("sub", "unknown")
                    email = user_info.get("email", "unknown")
                    
                    # Check if this account is already configured
                    await self.async_set_unique_id(self._user_id)
                    self._abort_if_unique_id_configured()
                    
                    # Test API connection with token
                    if await self._test_api_connection(token_info["access_token"]):
                        return self.async_create_entry(
                            title=f"Drinkaware - {self._account_name}",
                            data={
                                "token": token_info,
                                "account_name": self._account_name,
                                "user_id": self._user_id,
                                "email": email,
                            },
                        )
                    else:
                        errors["base"] = "connection_error"
                else:
                    errors["base"] = "no_code_in_url"
            except Exception as err:
                _LOGGER.error("Error during authentication: %s", err)
                errors["base"] = "auth_error"
                
        return self.async_show_form(
            step_id="code",
            data_schema=vol.Schema({
                vol.Required("redirect_url"): str,
            }),
            errors=errors,
            description_placeholders={
                "instructions": "Paste the entire redirect URL or text from your browser or dev tools"
            },
        )

    async def async_step_manual_token(self, user_input=None):
        """Handle manual token entry."""
        errors = {}
        
        if user_input is not None:
            self._session = async_get_clientsession(self.hass)
            
            token = user_input.get("token")
            
            try:
                # Extract user info from token
                user_info = self._parse_jwt(token)
                self._user_id = user_info.get("sub", "unknown")
                email = user_info.get("email", "unknown")
                
                # Check if this account is already configured
                await self.async_set_unique_id(self._user_id)
                self._abort_if_unique_id_configured()
                
                # Test API connection with token
                if await self._test_api_connection(token):
                    # Create a token_data structure 
                    token_data = {
                        "access_token": token,
                        "token_type": "Bearer",
                        "expires_in": 3600 * 24 * 30,  # Set a long expiry
                    }
                    
                    return self.async_create_entry(
                        title=f"Drinkaware - {self._account_name}",
                        data={
                            "token": token_data,
                            "account_name": self._account_name,
                            "user_id": self._user_id,
                            "email": email,
                        },
                    )
                else:
                    errors["base"] = "invalid_token"
            except Exception as err:
                _LOGGER.error("Error testing token: %s", err)
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="manual_token",
            data_schema=vol.Schema({
                vol.Required("token"): str,
            }),
            errors=errors,
            description_placeholders={
                "instructions": (
                    "Enter a valid authentication token from the Drinkaware app. "
                    "You can extract this using a tool like MITM Proxy to capture API "
                    "requests from the app. Look for the 'Authorization: Bearer' header "
                    "and copy everything after 'Bearer '."
                )
            },
        )

    def _generate_code_challenge(self, code_verifier):
        """Generate a code challenge for PKCE."""
        # Create a SHA256 hash of the verifier
        code_challenge_digest = hashlib.sha256(code_verifier.encode()).digest()
        # Base64 encode the hash and remove padding
        code_challenge = base64.urlsafe_b64encode(code_challenge_digest).decode().rstrip('=')
        return code_challenge
    
    def _get_authorization_url(self, code_challenge):
        """Get authorization URL with PKCE."""
        # Use the mobile app redirect URI
        redirect_uri = "uk.co.drinkaware.drinkaware://oauth/callback"
        
        params = {
            "client_id": OAUTH_CLIENT_ID,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": " ".join(OAUTH_SCOPES),
            "state": self.flow_id,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
        }
        
        query_string = urllib.parse.urlencode(params)
        return f"{OAUTH_AUTHORIZATION_URL}?{query_string}"

    async def _exchange_code_for_token(self, code, redirect_uri):
        """Exchange authorization code for tokens using PKCE."""
        data = {
            "client_id": OAUTH_CLIENT_ID,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "code_verifier": self._code_verifier,
        }
        
        headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "User-Agent": "Home Assistant Drinkaware Integration/1.0"
        }
        
        _LOGGER.debug("Exchanging code for token with data: %s", data)
        
        async with self._session.post(OAUTH_TOKEN_URL, data=data, headers=headers) as response:
            if response.status != 200:
                error_text = await response.text()
                _LOGGER.error("Token exchange failed with status %s: %s", response.status, error_text)
                raise Exception(f"Failed to get token: {response.status} - {error_text}")
                
            token_info = await response.json()
            _LOGGER.debug("Successfully obtained token")
            return token_info
            
    async def _test_api_connection(self, access_token):
        """Test connection to Drinkaware API with the token."""
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        }
        
        url = f"{API_BASE_URL}{ENDPOINT_STATS}"
        
        try:
            async with self._session.get(url, headers=headers) as resp:
                if resp.status != 200:
                    _LOGGER.error("API connection test failed with status %s: %s", 
                                 resp.status, await resp.text())
                return resp.status == 200
        except aiohttp.ClientError as err:
            _LOGGER.error("Error testing API connection: %s", err)
            return False
            
    def _extract_code_from_url(self, text):
        """Extract authorization code from URL or redirect text using regex."""
        # Try to find code parameter in a standard URL or custom URI
        code_match = re.search(r'[?&]code=([^&]+)', text)
        
        if code_match:
            return code_match.group(1)
            
        # If that didn't work, try another approach - look for the complete URI pattern
        uri_match = re.search(r'uk\.co\.drinkaware\.drinkaware://oauth/callback\?.*?code=([^&]+)', text)
        
        if uri_match:
            return uri_match.group(1)
            
        # If still not found, try a more generic approach
        code_match = re.search(r'code[=:]\s*([A-Za-z0-9._\-]+)', text)
        
        if code_match:
            return code_match.group(1)
            
        return None
        
    def _parse_jwt(self, token):
        """Parse JWT token to extract payload."""
        try:
            # JWT tokens have 3 parts separated by dots
            parts = token.split('.')
            if len(parts) != 3:
                return {}
                
            # Get the payload (middle part)
            import base64
            import json
            
            # Pad the base64 string if necessary
            payload = parts[1]
            payload += '=' * ((4 - len(payload) % 4) % 4)
            
            # Decode the payload
            decoded = base64.b64decode(payload)
            return json.loads(decoded)
        except Exception as e:
            _LOGGER.warning("Error parsing JWT token: %s", e)
            return {}