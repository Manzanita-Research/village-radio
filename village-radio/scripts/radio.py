#!/usr/bin/env python3
"""Village Radio — community playlist automation.

Usage:
    python radio.py --mode update --config ~/music/radio-config.yaml
    python radio.py --mode dry-run --config ~/music/radio-config.yaml
    python radio.py --mode setup
    python radio.py --mode add-artist --config ~/music/radio-config.yaml --artist "Bartees Strange"
"""

import argparse
import sys
from pathlib import Path

from config import load_config
from platforms.spotify import SpotifyPlatform
from playlist_builder import build_playlist


def cmd_update(args):
    """Fetch releases, build playlist, push to Spotify."""
    config = load_config(args.config)
    platform = SpotifyPlatform(rate_limit_delay=config.settings.rate_limit_delay)
    platform.authenticate()

    print(f"fetching releases for {len(config.artists)} artists...")
    releases = []
    for artist in config.artists:
        artist_releases = platform.get_artist_releases(
            artist.spotify_uri,
            config.settings.lookback_days,
            config.settings.include_groups,
        )
        releases.extend(artist_releases)
        if artist_releases:
            print(f"  {artist.name}: {len(artist_releases)} new release(s)")

    result = build_playlist(config, releases)
    _print_playlist(result)

    print(f"\npushing {result.total_count} tracks to {config.playlist.name}...")
    track_uris = [t.spotify_uri for t in result.tracks]
    platform.replace_playlist(config.playlist.spotify_uri, track_uris)
    print("done.")


def cmd_dry_run(args):
    """Fetch releases, build playlist, display without pushing."""
    config = load_config(args.config)
    platform = SpotifyPlatform(rate_limit_delay=config.settings.rate_limit_delay)
    platform.authenticate()

    print(f"fetching releases for {len(config.artists)} artists...")
    releases = []
    for artist in config.artists:
        artist_releases = platform.get_artist_releases(
            artist.spotify_uri,
            config.settings.lookback_days,
            config.settings.include_groups,
        )
        releases.extend(artist_releases)
        if artist_releases:
            print(f"  {artist.name}: {len(artist_releases)} new release(s)")

    result = build_playlist(config, releases)
    _print_playlist(result)
    print("\n(dry run — nothing was pushed)")


def cmd_setup(args):
    """Verify Spotify auth works."""
    platform = SpotifyPlatform()
    platform.authenticate()
    print("spotify auth is working.")

    if args.config:
        config = load_config(args.config)
        print(f"config loaded: {len(config.artists)} artists, {len(config.pinned)} pinned, {len(config.favorites)} favorites")


def cmd_add_artist(args):
    """Search for an artist and print results for confirmation."""
    if not args.artist:
        print("usage: radio.py --mode add-artist --artist 'Artist Name'", file=sys.stderr)
        sys.exit(1)

    platform = SpotifyPlatform()
    platform.authenticate()

    results = platform.search_artist(args.artist)
    if not results:
        print(f"no artists found for '{args.artist}'")
        sys.exit(1)

    print(f"search results for '{args.artist}':\n")
    for i, r in enumerate(results, 1):
        genres = ", ".join(r.genres[:3]) if r.genres else "no genres listed"
        print(f"  {i}. {r.name}")
        print(f"     uri: {r.uri}")
        print(f"     genres: {genres}")
        print(f"     popularity: {r.popularity}")
        print()

    # If a config path was given, show the YAML to append
    if args.config:
        top = results[0]
        print("to add the top result to your config, append:\n")
        print(f'  - name: "{top.name}"')
        print(f'    spotify_uri: "{top.uri}"')


def _print_playlist(result):
    """Print a human-readable playlist summary."""
    print(f"\n--- playlist ({result.total_count} tracks) ---\n")

    for i, track in enumerate(result.tracks, 1):
        prefix = ""
        if i <= result.pinned_count:
            prefix = " [pinned]"
        elif track in result.favorites_drawn:
            prefix = " [favorite]"
        artist = f" — {track.artist}" if track.artist else ""
        print(f"  {i:2d}. {track.name}{artist}{prefix}")

    print(f"\n{result.pinned_count} pinned, {len(result.favorites_drawn)} favorites, "
          f"{len(result.new_releases)} releases found")


def main():
    parser = argparse.ArgumentParser(description="Village Radio")
    parser.add_argument("--mode", required=True, choices=["update", "dry-run", "setup", "add-artist"])
    parser.add_argument("--config", type=Path, help="Path to radio config YAML")
    parser.add_argument("--artist", help="Artist name for add-artist mode")
    args = parser.parse_args()

    if args.mode in ("update", "dry-run") and not args.config:
        print("--config is required for update and dry-run modes", file=sys.stderr)
        sys.exit(1)

    commands = {
        "update": cmd_update,
        "dry-run": cmd_dry_run,
        "setup": cmd_setup,
        "add-artist": cmd_add_artist,
    }
    commands[args.mode](args)


if __name__ == "__main__":
    main()
