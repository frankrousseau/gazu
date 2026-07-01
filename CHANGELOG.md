# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

- `context.all_assets_for_project` / `all_scenes_for_project` /
  `all_sequences_for_episode` no longer raise `AttributeError` when
  `user_context=True` (the missing `gazu.user` functions were added).
- `batch_comments` and `create_multiple_comments` no longer crash when a
  `progress_callback` is provided.
- `gazu.aio.check_status` no longer raises a raw decode error on a non-JSON
  400/401 response body.
- `extract_frame_from_preview` / `extract_tile_from_preview` no longer crash
  when called without a `file_path` (the response is returned without saving).
- `gazu.aio.AsyncKitsuClient.refresh_access_token` raises
  `NotAuthenticatedException` when no refresh token is set.
- `sort_by_name` tolerates entities whose `name` is `None`.
- `person.update_person` guards the `departments` handling against string IDs.
- `user.all_episodes_for_project` normalizes its `project` argument.
- Synchronisation is resilient to ids not present in the mapping tables
  (unmapped tasks/comments are skipped and logged instead of aborting).
- `playlist.add_entity_to_playlist` no longer mutates the playlist argument.

### Changed

- `gazu.scene` and `gazu.search` are now importable from the top-level package.
- `events` connections verify SSL certificates by default (`ssl_verify=True`).
- Deduplicated the avatar, sync id-map and JWT-refresh helpers.

### Security

- Removed root-level scratch scripts that contained hard-coded credentials.

### Documentation / CI

- Documented the `async` extra and the top-level auth helpers.
- Added the async, CLI and helper modules to the Sphinx reference.
- Added a (non-blocking) `pip-audit` job to CI.
