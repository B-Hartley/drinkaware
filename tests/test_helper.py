"""Helper functions for Drinkaware integration tests."""
from unittest.mock import patch
import pytest
from homeassistant.helpers.entity_registry import async_get


def create_mock_entity(hass, entity_id, unique_id=None, platform="sensor"):
    """Create a mock entity entry in the registry."""
    entity_registry = async_get(hass)
    
    if unique_id is None:
        # Generate a unique_id based on entity_id
        unique_id = f"drinkaware_test_{entity_id.split('.')[-1]}"
    
    # Extract domain and name from entity_id
    domain, name = entity_id.split(".", 1)
    
    # Register the entity
    entity_registry.async_get_or_create(
        domain=domain,
        platform="drinkaware",
        unique_id=unique_id,
        suggested_object_id=name,
    )
    
    return entity_id


class TestEntityPlatform:
    """Helper class to simulate entity platform for testing."""
    
    def __init__(self, domain):
        """Initialize the test entity platform."""
        self.domain = domain
        self.entities = {}
    
    def add_entities(self, entities, update_before_add=False):
        """Add entities to the platform."""
        for entity in entities:
            self.entities[entity.entity_id] = entity
            if update_before_add and hasattr(entity, "async_update"):
                entity.async_update()


@pytest.fixture
def setup_platform(hass):
    """Set up a platform for adding entities."""
    async def _setup_platform(domain, platform_name=None, platform_id=None):
        """Set up a platform for testing."""
        if platform_name is None:
            platform_name = domain
        if platform_id is None:
            platform_id = domain
            
        platform = TestEntityPlatform(domain)
        
        with patch(f"homeassistant.helpers.entity_platform.EntityPlatform.async_schedule_add_entities"):
            await hass.config_entries.async_forward_entry_setup(
                next(iter(hass.config_entries.async_entries())), domain
            )
            
        return platform
    
    return _setup_platform