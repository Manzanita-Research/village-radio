# Village Radio — Dev Instructions

## What this is

A marketplace of Claude Code plugins for music communities. The first plugin (`village-radio`) automates community playlist curation on Spotify.

## Repo structure

- Top level: marketplace metadata, shared config
- `village-radio/`: playlist automation plugin (Python + Spotipy)
- `newsletter/`: planned — weekly digest plugin
- `artist-ingest/`: planned — batch artist resolution plugin

## Key principle: config lives with the user

The repo ships no config, no secrets, no tokens. The user's radio config YAML lives at a path they choose. Spotify credentials come from env vars. OAuth tokens cache locally. The plugin is pure logic.

## Tooling

- Use `mise` for runtime management. The repo has `.mise.toml` at the root.
- Always use `mise exec --` or `mise run` to run commands in the right environment.
- Never install packages with bare `pip install` — use `mise exec -- pip install` or activate the venv first.
- Use `hush` to run tests and checks. It saves context by showing `✓`/`✗` summaries instead of full output.
  - `hush test` — run playlist builder tests
  - `hush lint` — syntax check
  - `hush all` — run everything
  - Always prefer `hush` over raw test commands unless you need to see full output for debugging.

## Python conventions

- Python 3.10+
- Dependencies: spotipy, pyyaml, ruamel.yaml
- Use dataclasses for config models
- Platform abstraction: `platforms/base.py` defines the interface, `platforms/spotify.py` implements it
- Type hints on public functions

## Testing

- Run tests with `hush test` (or `hush all` to include lint)
- Unit tests for playlist_builder (dedup, truncation, sprinkle distribution)
- Dry-run mode for integration testing against real Spotify/Tidal API
- Skill trigger evals via skill-creator
