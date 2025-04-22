"""Test the Drinkaware config flow."""
from unittest.mock import patch, MagicMock, AsyncMock
import pytest
from homeassistant import config_entries, data_entry_flow
from custom_components.drinkaware.const import DOMAIN


async def test_form_user(hass):
    """Test we get the user form."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == "form"
    assert result["errors"] == {}
    assert result["step_id"] == "user"


@pytest.mark.parametrize("account_name", ["Test Account", "Another Account"])
async def test_account_name_step(hass, account_name):
    """Test the account name step."""
    with patch(
        "custom_components.drinkaware.config_flow.DrinkAwareConfigFlow.async_step_auth_method",
        return_value={"type": "form", "step_id": "auth_method"},
    ) as mock_step:
        
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        
        # Proceed with account name
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {"account_name": account_name}
        )
        
        # Check that the auth_method step is called
        assert mock_step.called
        assert result["type"] == "form"
        assert result["step_id"] == "auth_method"


async def test_auth_method_step(hass):
    """Test the auth method selection step."""
    with patch(
        "custom_components.drinkaware.config_flow.DrinkAwareConfigFlow.async_step_oauth_auth",
        return_value={"type": "form", "step_id": "oauth_auth"},
    ) as mock_step:
        
        # Initialize the flow
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        
        # Proceed with account name
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {"account_name": "Test Account"}
        )
        
        # Select OAuth auth method
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {"auth_method": "oauth"}
        )
        
        # Check that the oauth_auth step is called
        assert mock_step.called
        assert result["type"] == "form"
        assert result["step_id"] == "oauth_auth"


async def test_oauth_auth_step(hass):
    """Test the OAuth authorization step."""
    with patch(
        "custom_components.drinkaware.config_flow.DrinkAwareConfigFlow._generate_code_challenge",
        return_value="test_code_challenge",
    ), patch(
        "custom_components.drinkaware.config_flow.DrinkAwareConfigFlow._get_authorization_url",
        return_value="https://test-auth-url.com",
    ), patch(
        "custom_components.drinkaware.config_flow.DrinkAwareConfigFlow.async_step_code",
        return_value={"type": "form", "step_id": "code"},
    ) as mock_step:
        
        # Initialize the flow
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        
        # Proceed with account name
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {"account_name": "Test Account"}
        )
        
        # Select OAuth auth method
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {"auth_method": "oauth"}
        )
        
        # Proceed to code step
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {}
        )
        
        # Check that the code step is called
        assert mock_step.called
        assert result["type"] == "form"
        assert result["step_id"] == "code"


async def test_code_step_success(hass):
    """Test the code input step with successful authentication."""
    with patch(
        "custom_components.drinkaware.config_flow.DrinkAwareConfigFlow._extract_code_from_url",
        return_value="test_code",
    ), patch(
        "custom_components.drinkaware.config_flow.DrinkAwareConfigFlow._exchange_code_for_token",
        return_value={
            "access_token": "test_access_token",
            "refresh_token": "test_refresh_token",
            "expires_in": 3600,
        },
    ), patch(
        "custom_components.drinkaware.config_flow.DrinkAwareConfigFlow._parse_jwt",
        return_value={"sub": "test_user_id", "email": "test@example.com"},
    ), patch(
        "custom_components.drinkaware.config_flow.DrinkAwareConfigFlow._test_api_connection",
        return_value=True,
    ):
        
        # Initialize the flow
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        
        # Proceed with account name
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {"account_name": "Test Account"}
        )
        
        # Select OAuth auth method
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {"auth_method": "oauth"}
        )
        
        # Proceed to code step
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {}
        )
        
        # Submit redirect URL
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {"redirect_url": "uk.co.drinkaware.drinkaware://oauth/callback?code=test_code"}
        )
        
        # Check that we have a create entry result
        assert result["type"] == "create_entry"
        assert result["title"] == "Drinkaware - Test Account"
        assert result["data"]["token"]["access_token"] == "test_access_token"
        assert result["data"]["account_name"] == "Test Account"
        assert result["data"]["user_id"] == "test_user_id"


async def test_code_step_failure(hass):
    """Test the code input step with failed authentication."""
    with patch(
        "custom_components.drinkaware.config_flow.DrinkAwareConfigFlow._extract_code_from_url",
        return_value=None,
    ):
        
        # Initialize the flow
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        
        # Proceed with account name
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {"account_name": "Test Account"}
        )
        
        # Select OAuth auth method
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {"auth_method": "oauth"}
        )
        
        # Proceed to code step
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {}
        )
        
        # Submit invalid redirect URL
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {"redirect_url": "invalid-url"}
        )
        
        # Check that we have an error
        assert result["type"] == "form"
        assert result["errors"]["base"] == "no_code_in_url"