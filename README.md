# Village Radio

Release Radar, but for your people.

Village Radio is an open-source toolkit for music communities. It automates the curation work that scene builders do by hand — keeping playlists fresh with new releases from artists you care about, not artists an algorithm thinks you should hear.

## How it works

You maintain a simple config file: a list of artists in your community, tracks you want pinned to the top, and all-time favorites to sprinkle in. Village Radio checks for new releases, builds the playlist, and pushes it to Spotify. Run it every Friday morning and your community always has something fresh to listen to.

**Pin what matters.** Your latest release stays at the top no matter how old it is. A homie's debut single gets the spotlight it deserves. Pinned tracks are sacred — they don't get rotated out.

**Sprinkle in the classics.** Draw from a pool of all-time favorites and scatter them through the playlist. New listeners discover the canon alongside the new.

**Platform-ready.** Starts with Spotify. Designed so Tidal, Qobuz, and whatever comes next can plug in without starting over.

## Plugins

Village Radio is a marketplace of community music tools. Install what you need.

| Plugin | Status | What it does |
|---|---|---|
| **village-radio** | Building | Community playlist automation |
| **newsletter** | Planned | Weekly digest from the same release data |
| **artist-ingest** | Planned | Batch-add artists from names, playlists, or festival lineups |

## Quick start

```
# Add the marketplace
claude plugin marketplace add manzanita-research/village-radio

# Install the playlist plugin
claude plugin install village-radio

# Set up Spotify auth (one-time)
/village-radio:setup

# See what this week's playlist would look like
/village-radio:dry-run

# Push it live
/village-radio:update
```

## Your config, your machine

Village Radio ships no secrets, no API keys, no personal data. Your config file lives wherever you want it. Spotify credentials stay in your shell environment. Tokens cache locally. The plugin is pure logic — given a config, fetch releases, build a playlist, push it.

## Automation

Set it up in Claude Cowork and it runs every Friday morning. Headless, no browser popups, just a summary of what changed: which artists had new releases, what got added, how the playlist looks this week.

## Built by

[Manzanita Research](https://github.com/manzanita-research) — instruments for musicians, not automations that replace them.
