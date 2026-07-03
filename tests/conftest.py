import pytest
import gazu.client
import gazu.cache


@pytest.fixture(autouse=True)
def reset_client_state():
    """Save and restore the default client state around every test."""
    client = gazu.client.default_client
    original_host = client.host
    original_event_host = client.event_host
    original_tokens = client.tokens.copy()
    original_cache_enabled = gazu.cache.cache_settings["enabled"]
    yield
    client.host = original_host
    client.event_host = original_event_host
    client.tokens = original_tokens
    gazu.cache.cache_settings["enabled"] = original_cache_enabled
