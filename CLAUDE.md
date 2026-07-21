# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Gazu is a Python client for the Kitsu API (https://zou.cg-wire.com), a collaboration platform for animation and VFX studios. It provides functions for managing assets, shots, tasks, files, and other production data.

## Development Commands

```bash
# Install dependencies (dev mode)
# Optional extras: dev, test, lint, async, cli
pip install -e .[dev,test,lint]

# Run all tests
py.test

# Run a single test file
py.test tests/test_asset.py

# Run a specific test
py.test tests/test_asset.py::AssetTestCase::test_get_asset

# Run with coverage
py.test --cov=gazu

# Format code (black is in the `lint` extra; requires Python 3.10+)
black .

# Install pre-commit hooks
pre-commit install
```

The package targets Python 3.7+ (tested up to 3.14).

## Architecture

### Client System (`gazu/client.py`)
- `KitsuClient` class manages connections: host URL, authentication tokens, SSL settings
- `default_client` is a global singleton used when no client is specified
- All API functions accept an optional `client` parameter for multi-instance support
- HTTP methods (`get`, `post`, `put`, `delete`) handle authentication headers and token refresh automatically

### Module Structure
Each module in `gazu/` corresponds to a Kitsu entity type and follows consistent patterns:
- `all_*()` - Fetch all entities of a type
- `get_*()` / `get_*_by_name()` - Fetch single entity
- `new_*()` - Create entity
- `update_*()` - Update entity
- `remove_*()` - Delete entity

Key modules:
- `asset.py`, `shot.py`, `scene.py`, `edit.py`, `concept.py`, `entity.py` - Production entities
- `task.py` - Task management and comments
- `files.py` - File versioning and output files
- `person.py` - User and time tracking
- `user.py` - Data accessible to the currently logged user
- `casting.py` - Asset-to-shot linking
- `playlist.py` - Review playlists
- `sync.py` - Data synchronization between instances
- `project.py` / `project_template.py` - Project settings, data and templates
- `studio.py` - Studios and departments
- `search.py` - Cross-entity search
- `context.py` - Connected user data
- `helpers.py`, `sorting.py` - Shared utilities (id normalization, sorting)

### Command-line Interface (`gazu/cli.py`)
Exposed as the `gazu-cli` entry point (requires the `cli` extra, which pulls in `click`).

### Async Support (`gazu/aio.py`)
Async primitives for the Kitsu API built on `aiohttp` (requires the `async` extra).

### Caching (`gazu/cache.py`)
Decorator-based caching system: use `@cache` decorator on functions, control with `gazu.cache.enable()` / `gazu.cache.disable()`.

### Events (`gazu/events.py`)
Socket.IO-based event listener for real-time updates from Kitsu.

## Testing

Tests use `requests_mock` to mock HTTP calls. Key utilities in `tests/utils.py`:
- `fakeid(string)` - Generate deterministic UUIDs for testing
- `mock_route(mock, method, path, **kwargs)` - Helper to mock API routes
- `add_verify_file_callback(mock, dict_assert, url)` - Verify file upload contents

Test pattern:
```python
@requests_mock.Mocker()
def test_example(self, mock):
    mock_route(mock, "GET", "data/assets", text=[{"id": fakeid("asset")}])
    result = gazu.asset.all_assets()
    self.assertEqual(len(result), 1)
```

### Route contract gate

`tests/test_zou_routes.py` (with `tests/zou_route_gate.py`) fails any mocked request whose path+method does not exist in Zou's route snapshot. A mocked test passing is not proof the route is real — the gate is. When it rejects a path, verify against the zou blueprints (`../zou/zou/app/blueprints/*/__init__.py`) and fix the wrapper, not the gate.

### Entity routes, not noun routes, for writes

In Zou, several entity-noun sub-routes (`data/asset-types/{id}`, `data/assets/{id}/tasks`, …) are GET-only. Write wrappers for entities (asset/shot/sequence/episode/edit/concept) go through the generic routes: `PUT data/entities/{id}` for updates, `POST data/entities/{id}/tasks` for task creation, `data/entity-types/` for type CRUD. Follow the existing `update_asset`-style wrappers when adding new write operations.

## Code Style

- Follow PEP 8, enforced by Black with line-length 79
- All contributions follow the C4 contract (https://rfc.zeromq.org/spec:42/C4)

## PR Description Format

PRs use the bold two-paragraph structure (harmonized across cgwire repos 2026-07 — do not use `## Problems` / `## Solutions` headers):

```markdown
**Problem**
- bullet point describing each problem addressed by the PR

**Solution**
- bullet point describing each fix or change applied
```

Keep bullet points concise: the Problem section lists what was wrong, the Solution section what was done to fix it. One bullet per distinct issue/fix. No `🤖 Generated with` footer.
