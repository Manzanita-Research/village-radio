# Release Fetcher Agent

Fetches recent releases for all artists in the config. Used internally by the village-radio skill.

## Behavior

1. Load config from the user's path
2. For each artist, call the platform to get releases within `lookback_days`
3. Collect and return all releases for the playlist builder

This agent is invoked by the main skill, not directly by the user.
