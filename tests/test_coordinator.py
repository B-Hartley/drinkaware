"""Test the Drinkaware data update coordinator."""
from unittest.mock import patch, MagicMock, AsyncMock
import pytest
from datetime import datetime, timedelta
import aiohttp

from custom_components.drinkaware import DrinkAwareDataUpdateCoordinator
from custom_components.drinkaware.const import DOMAIN


@pytest.fixture
def mock_session():
    """Create a mock aiohttp session."""
    session = AsyncMock()
    
    # Mock response for API calls
    mock_resp = AsyncMock()
    mock_resp.status = 200
    mock_resp.json = AsyncMock(return_value={"success": True})
    mock_resp.text = AsyncMock(return_value="Success")
    
    # Configure session methods to return the mock response
    session.get.return_value.__aenter__.return_value = mock_resp
    session.post.return_value.__aenter__.return_value = mock_resp
    session.put.return_value.__aenter__.return_value = mock_resp
    session.delete.return_value.__aenter__.return_value = mock_resp
    
    return session


@pytest.fixture
def coordinator(hass, mock_session):
    """Create a mock coordinator."""
    token_data = {
        "access_token": "test_access_token",
        "refresh_token": "test_refresh_token",
        "expires_in": 3600,
    }
    
    return DrinkAwareDataUpdateCoordinator(
        hass,
        mock_session,
        token_data,
        "test_entry_id",
        "Test Account",
        "test@example.com"
    )


async def test_coordinator_initialization(coordinator):
    """Test coordinator initialization."""
    assert coordinator.access_token == "test_access_token"
    assert coordinator.refresh_token == "test_refresh_token"
    assert coordinator.account_name == "Test Account"
    assert coordinator.email == "test@example.com"
    assert coordinator._rate_limited is False
    assert coordinator.drinks_cache is None


@pytest.mark.parametrize(
    "status_code, expected_result",
    [
        (200, {"success": True}),  # Success
        (401, None),  # Unauthorized
        (500, None),  # Server error
    ],
)
async def test_make_api_request(coordinator, mock_session, status_code, expected_result):
    """Test the _make_api_request method."""
    # Configure the mock response
    mock_resp = AsyncMock()
    mock_resp.status = status_code
    if status_code == 200:
        mock_resp.json = AsyncMock(return_value={"success": True})
    mock_resp.text = AsyncMock(return_value="Error message")
    
    # Update the session get method to return our custom response
    mock_session.get.return_value.__aenter__.return_value = mock_resp
    
    # Call the method
    result = await coordinator._make_api_request("https://api.drinkaware.co.uk/test")
    
    # Check the result
    assert result == expected_result
    
    # Verify that the request was made with the correct headers
    mock_session.get.assert_called_once()
    call_kwargs = mock_session.get.call_args.kwargs
    assert "headers" in call_kwargs
    assert call_kwargs["headers"]["Authorization"] == "Bearer test_access_token"


async def test_rate_limit_handling(coordinator, mock_session):
    """Test handling of rate limiting."""
    # Configure the mock response for rate limiting
    rate_limit_resp = AsyncMock()
    rate_limit_resp.status = 429
    rate_limit_resp.text = AsyncMock(return_value="Try again in 2 seconds")
    
    # Configure the mock response for successful retry
    success_resp = AsyncMock()
    success_resp.status = 200
    success_resp.json = AsyncMock(return_value={"success": True})
    
    # Set up the session to return rate limit first, then success
    mock_session.get.return_value.__aenter__.side_effect = [rate_limit_resp, success_resp]
    
    # Mock sleep to avoid waiting in the test
    with patch("asyncio.sleep") as mock_sleep:
        # Call the method
        result = await coordinator._make_api_request("https://api.drinkaware.co.uk/test")
        
        # Check the result
        assert result == {"success": True}
        
        # Verify that sleep was called with the correct duration
        mock_sleep.assert_called_once_with(2)
        
        # Verify that the request was made twice
        assert mock_session.get.call_count == 2


async def test_refresh_token(coordinator, mock_session, hass):
    """Test token refresh functionality."""
    # Configure the mock response for token refresh
    refresh_resp = AsyncMock()
    refresh_resp.status = 200
    refresh_resp.json = AsyncMock(return_value={
        "access_token": "new_access_token",
        "refresh_token": "new_refresh_token",
        "expires_in": 3600,
    })
    
    # Set up the session to return the refresh response
    mock_session.post.return_value.__aenter__.return_value = refresh_resp
    
    # Mock the config entry
    entry = MagicMock()
    entry.entry_id = "test_entry_id"
    entry.data = {"token": coordinator.token_data}
    
    # Mock the config entries
    hass.config_entries = MagicMock()
    hass.config_entries.async_get_entry.return_value = entry
    
    # Call the refresh token method
    await coordinator._refresh_token()
    
    # Check that the token was updated
    assert coordinator.access_token == "new_access_token"
    assert coordinator.refresh_token == "new_refresh_token"
    
    # Verify that config entry was updated
    hass.config_entries.async_update_entry.assert_called_once()
    update_data = hass.config_entries.async_update_entry.call_args.kwargs["data"]
    assert update_data["token"]["access_token"] == "new_access_token"