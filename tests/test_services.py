"""Test the Drinkaware services."""
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, date
import pytest

from homeassistant.exceptions import HomeAssistantError
from homeassistant.core import ServiceCall

from custom_components.drinkaware.const import (
    DOMAIN,
    SERVICE_LOG_DRINK_FREE_DAY,
    SERVICE_LOG_DRINK,
    SERVICE_DELETE_DRINK,
    SERVICE_REMOVE_DRINK_FREE_DAY,
    SERVICE_LOG_SLEEP_QUALITY,
    SERVICE_REFRESH,
)
from custom_components.drinkaware.services import (
    async_setup_services,
    async_unload_services,
    add_drink,
    set_drink_quantity,
    remove_drink_free_day,
    log_sleep_quality,
)
from custom_components.drinkaware.drink_constants import (
    DRINK_ID_LAGER,
    MEASURE_ID_PINT,
)


@pytest.fixture
def mock_coordinator():
    """Create a mock coordinator."""
    coordinator = AsyncMock()
    coordinator.account_name = "Test Account"
    coordinator.email = "test@example.com"
    coordinator.entry_id = "test_entry_id"
    coordinator.access_token = "test_access_token"
    coordinator.session = AsyncMock()
    
    # Mock response for session methods
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={"success": True})
    
    # Set up the session methods to return the mock response
    coordinator.session.get.return_value.__aenter__.return_value = mock_response
    coordinator.session.post.return_value.__aenter__.return_value = mock_response
    coordinator.session.put.return_value.__aenter__.return_value = mock_response
    coordinator.session.delete.return_value.__aenter__.return_value = mock_response
    
    # Set up data structure
    coordinator.data = {
        "summary": [
            {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "drinks": 2,
                "units": 4.0,
                "drinkFreeDay": False
            }
        ]
    }
    
    return coordinator


async def test_async_setup_services(hass, mock_coordinator):
    """Test setting up services."""
    # Setup mock data in hass
    hass.data[DOMAIN] = {"test_entry_id": mock_coordinator}
    
    # Set up services
    await async_setup_services(hass)
    
    # Check that services are registered
    assert hass.services.has_service(DOMAIN, SERVICE_LOG_DRINK_FREE_DAY)
    assert hass.services.has_service(DOMAIN, SERVICE_LOG_DRINK)
    assert hass.services.has_service(DOMAIN, SERVICE_DELETE_DRINK)
    assert hass.services.has_service(DOMAIN, SERVICE_REMOVE_DRINK_FREE_DAY)
    assert hass.services.has_service(DOMAIN, SERVICE_LOG_SLEEP_QUALITY)
    assert hass.services.has_service(DOMAIN, SERVICE_REFRESH)


async def test_async_unload_services(hass):
    """Test unloading services."""
    # First register services
    with patch("homeassistant.core.ServiceRegistry.async_register") as mock_register:
        await async_setup_services(hass)
    
    # Now unload services
    with patch("homeassistant.core.ServiceRegistry.async_remove") as mock_remove:
        await async_unload_services(hass)
        
        # Check that each service was removed
        assert mock_remove.call_count == 6
        mock_remove.assert_any_call(DOMAIN, SERVICE_LOG_DRINK_FREE_DAY)
        mock_remove.assert_any_call(DOMAIN, SERVICE_LOG_DRINK)
        mock_remove.assert_any_call(DOMAIN, SERVICE_DELETE_DRINK)
        mock_remove.assert_any_call(DOMAIN, SERVICE_REMOVE_DRINK_FREE_DAY)
        mock_remove.assert_any_call(DOMAIN, SERVICE_LOG_SLEEP_QUALITY)
        mock_remove.assert_any_call(DOMAIN, SERVICE_REFRESH)


async def test_log_drink_free_day_service(hass, mock_coordinator):
    """Test the log_drink_free_day service."""
    # Setup mock data in hass
    hass.data[DOMAIN] = {"test_entry_id": mock_coordinator}
    
    # Mock the coordinator functions
    with patch("custom_components.drinkaware.services.get_coordinator_by_entry_id", return_value=mock_coordinator):
        # Call the service
        await hass.services.async_call(
            DOMAIN,
            SERVICE_LOG_DRINK_FREE_DAY,
            {
                "entry_id": "test_entry_id",
                "date": "2025-04-18",
                "remove_drinks": True
            },
            blocking=True,
        )
        
    # Check that API calls were made
    assert mock_coordinator.async_refresh.call_count >= 1
    assert mock_coordinator.session.get.call_count >= 1
    assert mock_coordinator.session.put.call_count >= 1


async def test_log_drink_service(hass, mock_coordinator):
    """Test the log_drink service."""
    # Setup mock data in hass
    hass.data[DOMAIN] = {"test_entry_id": mock_coordinator}
    
    # Mock services functions
    with patch("custom_components.drinkaware.services.get_coordinator_by_entry_id", return_value=mock_coordinator), \
         patch("custom_components.drinkaware.services.add_drink", return_value=(True, 1)) as mock_add_drink:
        
        # Call the service
        await hass.services.async_call(
            DOMAIN,
            SERVICE_LOG_DRINK,
            {
                "entry_id": "test_entry_id",
                "drink_id": DRINK_ID_LAGER,
                "measure_id": MEASURE_ID_PINT,
                "quantity": 1,
                "date": "2025-04-18"
            },
            blocking=True,
        )
        
    # Check that API call was made
    assert mock_add_drink.called
    assert mock_coordinator.async_refresh.called


async def test_custom_abv_drink_service(hass, mock_coordinator):
    """Test the log_drink service with custom ABV."""
    # Setup mock data in hass
    hass.data[DOMAIN] = {"test_entry_id": mock_coordinator}
    
    # Mock services functions
    with patch("custom_components.drinkaware.services.get_coordinator_by_entry_id", return_value=mock_coordinator), \
         patch("custom_components.drinkaware.services.create_custom_drink", return_value="custom_drink_id") as mock_create, \
         patch("custom_components.drinkaware.services.add_drink", return_value=(True, 1)) as mock_add_drink:
        
        # Call the service
        await hass.services.async_call(
            DOMAIN,
            SERVICE_LOG_DRINK,
            {
                "entry_id": "test_entry_id",
                "drink_id": DRINK_ID_LAGER,
                "measure_id": MEASURE_ID_PINT,
                "abv": 5.5,  # Custom ABV
                "name": "Strong Lager",
                "quantity": 1,
                "date": "2025-04-18"
            },
            blocking=True,
        )
        
    # Check that API calls were made
    assert mock_create.called
    assert mock_add_drink.called
    assert mock_coordinator.async_refresh.called


async def test_delete_drink_service(hass, mock_coordinator):
    """Test the delete_drink service."""
    # Setup mock data in hass
    hass.data[DOMAIN] = {"test_entry_id": mock_coordinator}
    
    # Mock the coordinator functions and the get_coordinator_by_entry_id function
    with patch("custom_components.drinkaware.services.get_coordinator_by_entry_id", return_value=mock_coordinator):
        # Call the service
        await hass.services.async_call(
            DOMAIN,
            SERVICE_DELETE_DRINK,
            {
                "entry_id": "test_entry_id",
                "drink_id": DRINK_ID_LAGER,
                "measure_id": MEASURE_ID_PINT,
                "date": "2025-04-18"
            },
            blocking=True,
        )
        
    # Check that API calls were made
    assert mock_coordinator.session.get.call_count >= 1
    assert mock_coordinator.session.delete.call_count >= 1
    assert mock_coordinator.async_refresh.called


async def test_remove_drink_free_day_service(hass, mock_coordinator):
    """Test the remove_drink_free_day service."""
    # Setup mock data in hass
    hass.data[DOMAIN] = {"test_entry_id": mock_coordinator}
    
    # Mock the coordinator functions
    with patch("custom_components.drinkaware.services.get_coordinator_by_entry_id", return_value=mock_coordinator), \
         patch("custom_components.drinkaware.services.remove_drink_free_day", return_value=True) as mock_remove:
        
        # Call the service
        await hass.services.async_call(
            DOMAIN,
            SERVICE_REMOVE_DRINK_FREE_DAY,
            {
                "entry_id": "test_entry_id",
                "date": "2025-04-18"
            },
            blocking=True,
        )
        
    # Check that the function was called
    assert mock_remove.called
    assert mock_coordinator.async_refresh.called


async def test_log_sleep_quality_service(hass, mock_coordinator):
    """Test the log_sleep_quality service."""
    # Setup mock data in hass
    hass.data[DOMAIN] = {"test_entry_id": mock_coordinator}
    
    # Mock the coordinator functions
    with patch("custom_components.drinkaware.services.get_coordinator_by_entry_id", return_value=mock_coordinator), \
         patch("custom_components.drinkaware.services.log_sleep_quality", return_value=True) as mock_log:
        
        # Call the service
        await hass.services.async_call(
            DOMAIN,
            SERVICE_LOG_SLEEP_QUALITY,
            {
                "entry_id": "test_entry_id",
                "quality": "average",
                "date": "2025-04-18"
            },
            blocking=True,
        )
        
    # Check that the function was called
    assert mock_log.called
    assert mock_coordinator.async_refresh.called


async def test_refresh_service(hass, mock_coordinator):
    """Test the refresh service."""
    # Setup mock data in hass
    hass.data[DOMAIN] = {"test_entry_id": mock_coordinator, "other_entry_id": mock_coordinator}
    
    # Mock the coordinator functions
    with patch("custom_components.drinkaware.services.get_coordinator_by_entry_id", return_value=mock_coordinator):
        # Call the service for a specific entry
        await hass.services.async_call(
            DOMAIN,
            SERVICE_REFRESH,
            {
                "entry_id": "test_entry_id"
            },
            blocking=True,
        )
        
        # Check that refresh was called
        assert mock_coordinator.async_refresh.call_count == 1
        
        # Reset call count
        mock_coordinator.async_refresh.reset_mock()
        
        # Call the service for all entries
        await hass.services.async_call(
            DOMAIN,
            SERVICE_REFRESH,
            {},
            blocking=True,
        )
        
        # Check that refresh was called for each entry
        # There are 2 entries but one is accessed twice because get_coordinator_by_entry_id is mocked
        # So the call count is 1
        assert mock_coordinator.async_refresh.call_count == 1


async def test_add_drink_function(mock_coordinator):
    """Test the add_drink function."""
    # Call the function
    result = await add_drink(
        mock_coordinator,
        DRINK_ID_LAGER,
        MEASURE_ID_PINT,
        None,  # No custom ABV
        date.today()
    )
    
    # Check the result
    assert result[0] is True  # Success
    
    # Check that API call was made
    assert mock_coordinator.session.post.call_count == 1


async def test_set_drink_quantity_function(mock_coordinator):
    """Test the set_drink_quantity function."""
    # Call the function
    result = await set_drink_quantity(
        mock_coordinator,
        DRINK_ID_LAGER,
        MEASURE_ID_PINT,
        None,  # No custom ABV
        2,  # quantity
        date.today()
    )
    
    # Check the result
    assert result is True
    
    # Check that API call was made
    assert mock_coordinator.session.put.call_count == 1


async def test_remove_drink_free_day_function(mock_coordinator):
    """Test the remove_drink_free_day function."""
    # Call the function
    result = await remove_drink_free_day(
        mock_coordinator,
        date.today()
    )
    
    # Check the result
    assert result is True
    
    # Check that API call was made
    assert mock_coordinator.session.delete.call_count == 1


async def test_log_sleep_quality_function(mock_coordinator):
    """Test the log_sleep_quality function."""
    # Call the function
    result = await log_sleep_quality(
        mock_coordinator,
        "average",
        date.today()
    )
    
    # Check the result
    assert result is True
    
    # Check that API call was made
    assert mock_coordinator.session.put.call_count == 1