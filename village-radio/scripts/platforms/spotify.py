"""Spotify platform implementation using Spotipy."""

import os
import sys
import time
from datetime import datetime, timedelta

import spotipy
from spotipy.oauth2 import SpotifyOAuth

from .base import Platform, Release, SearchResult


def _parse_spotify_date(date_str: str) -> datetime:
    """Parse Spotify's variable-precision date strings."""
    for fmt in ("%Y-%m-%d", "%Y-%m", "%Y"):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    raise ValueError(f"Unrecognized date format: {date_str}")


def _uri_to_id(uri: str) -> str:
    """Extract Spotify ID from a URI like spotify:artist:abc123."""
    return uri.split(":")[-1]


class SpotifyPlatform(Platform):
    """Spotify implementation via Spotipy."""

    SCOPES = "playlist-modify-public playlist-modify-private"

    def __init__(self, rate_limit_delay: float = 0.5):
        self.rate_limit_delay = rate_limit_delay
        self.client: spotipy.Spotify | None = None

    def authenticate(self) -> None:
        required = ["SPOTIPY_CLIENT_ID", "SPOTIPY_CLIENT_SECRET", "SPOTIPY_REDIRECT_URI"]
        missing = [v for v in required if not os.environ.get(v)]
        if missing:
            print(f"Missing environment variables: {', '.join(missing)}", file=sys.stderr)
            print("Run /village-radio:setup for instructions.", file=sys.stderr)
            sys.exit(1)

        auth_manager = SpotifyOAuth(
            scope=self.SCOPES,
            open_browser=False,
        )

        try:
            self.client = spotipy.Spotify(auth_manager=auth_manager)
            # Verify auth works
            self.client.current_user()
        except Exception as e:
            print(f"Spotify auth failed: {e}", file=sys.stderr)
            print("Try deleting .cache and running /village-radio:setup again.", file=sys.stderr)
            sys.exit(1)

    def get_artist_releases(
        self,
        artist_uri: str,
        lookback_days: int,
        include_groups: list[str],
    ) -> list[Release]:
        cutoff = datetime.now() - timedelta(days=lookback_days)
        artist_id = _uri_to_id(artist_uri)
        releases = []

        for group in include_groups:
            time.sleep(self.rate_limit_delay)
            results = self.client.artist_albums(
                artist_id,
                album_type=group,
                limit=50,
            )

            for album in results.get("items", []):
                release_date = _parse_spotify_date(album["release_date"])
                if release_date < cutoff:
                    continue

                # Fetch tracks for this release
                time.sleep(self.rate_limit_delay)
                album_tracks = self.client.album_tracks(album["id"])
                tracks = [
                    {"name": t["name"], "uri": t["uri"]}
                    for t in album_tracks.get("items", [])
                ]

                artist_name = album["artists"][0]["name"] if album["artists"] else ""

                releases.append(
                    Release(
                        name=album["name"],
                        uri=album["uri"],
                        artist_name=artist_name,
                        artist_uri=artist_uri,
                        release_date=release_date,
                        release_type=group,
                        tracks=tracks,
                    )
                )

        return releases

    def replace_playlist(
        self,
        playlist_uri: str,
        track_uris: list[str],
    ) -> None:
        playlist_id = _uri_to_id(playlist_uri)
        # Spotify API accepts max 100 tracks per request
        self.client.playlist_replace_items(playlist_id, track_uris[:100])
        # Add remaining in batches if needed
        for i in range(100, len(track_uris), 100):
            batch = track_uris[i : i + 100]
            self.client.playlist_add_items(playlist_id, batch)

    def search_artist(self, query: str, limit: int = 5) -> list[SearchResult]:
        results = self.client.search(q=query, type="artist", limit=limit)
        artists = results.get("artists", {}).get("items", [])
        return [
            SearchResult(
                name=a["name"],
                uri=a["uri"],
                genres=a.get("genres", []),
                popularity=a.get("popularity", 0),
            )
            for a in artists
        ]
