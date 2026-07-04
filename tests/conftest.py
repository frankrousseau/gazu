import pytest
import requests_mock

import gazu.client
import gazu.cache

from zou_route_gate import request_path, is_known_route


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


@pytest.fixture(autouse=True)
def assert_routes_exist_in_zou(monkeypatch):
    """
    Fail any test that mocks a path Zou does not actually serve.

    The suite mocks whatever URL gazu builds, so a wrong route passes on its
    own. This gate matches each mocked route against Zou's real route table
    (tests/fixtures/zou_routes.json). requests_mock intercepts below
    Session.send, so we hook route *registration* instead, which every
    mock.get/post/... and mock_route call goes through. See
    tests/zou_route_gate.py.
    """
    original = requests_mock.Mocker.register_uri

    def checked_register(self, *args, **kwargs):
        url = kwargs.get("url", args[1] if len(args) > 1 else None)
        if isinstance(url, str):
            path = request_path(url)
            if path is not None and not is_known_route(path):
                raise AssertionError(
                    f"{path} is not a route Zou serves. Fix the path (see "
                    "scripts/extract_zou_routes.py) or, if it is a known-broken "
                    "endpoint, add it to _ALLOWED_BROKEN in "
                    "tests/zou_route_gate.py."
                )
        return original(self, *args, **kwargs)

    monkeypatch.setattr(requests_mock.Mocker, "register_uri", checked_register)
