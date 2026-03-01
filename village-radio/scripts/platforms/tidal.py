"""Tidal platform implementation using tidalapi."""

import json
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

import tidalapi

from .base import Platform, Release, SearchResult


def _parse_tidal_date(date_obj) -> datetime:
    """Normalize Tidal's date to a datetime. Handles date and datetime objects."""
    if isinstance(date_obj, datetime):
        return date_obj
    if hasattr(date_obj, "year"):
        # date object
        return datetime(date_obj.year, date_obj.month, date_obj.day)
    raise ValueError(f"Unrecognized date format: {date_obj}")


class TidalPlatform(Platform):
    """Tidal implementation via tidalapi."""

    def __init__(self, rate_limit_delay: float = 0.5):
        self.rate_limit_delay = rate_limit_delay
        self.session: tidalapi.Session | None = None

    def authenticate(self) -> None:
        session = tidalapi.Session()

        # Try loading saved session first
        session_file = Path(os.environ.get("TIDAL_SESSION_FILE", ".tidal-session.json"))
        if session_file.exists():
            try:
                session.login_session_file(session_file)
                if session.check_login():
                    self.session = session
                    return
            except Exception:
                pass  # Fall through to fresh login

        # Fresh OAuth device flow
        try:
            session.login_oauth_simple()
        except Exception as e:
            print(f"Tidal auth failed: {e}", file=sys.stderr)
            print("Make sure you have a Tidal account and can reach link.tidal.com", file=sys.stderr)
            sys.exit(1)

        if not session.check_login():
            print("Tidal login was not completed.", file=sys.stderr)
            sys.exit(1)

        # Persist session for next run
        _save_session(session, session_file)
        self.session = session

    def get_artist_releases(
        self,
        artist_uri: str,
        lookback_days: int,
        include_groups: list[str],
    ) -> list[Release]:
        cutoff = datetime.now() - timedelta(days=lookback_days)
        artist = self.session.artist(artist_uri)
        releases = []

        # Map include_groups to tidalapi methods
        group_methods = {
            "album": artist.get_albums,
            "single": artist.get_ep_singles,
            "appears_on": artist.get_other,
        }

        for group in include_groups:
            fetch = group_methods.get(group)
            if not fetch:
                continue

            time.sleep(self.rate_limit_delay)
            try:
                albums = fetch()
            except Exception:
                continue

            for album in albums:
                release_date = _parse_tidal_date(album.available or album.tidal_release_date)
                if release_date < cutoff:
                    continue

                time.sleep(self.rate_limit_delay)
                try:
                    album_tracks = album.tracks()
                except Exception:
                    continue

                tracks = [
                    {"name": t.name, "uri": str(t.id)}
                    for t in album_tracks
                ]

                artist_name = album.artist.name if album.artist else ""

                releases.append(
                    Release(
                        name=album.name,
                        uri=str(album.id),
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
        playlist = self.session.playlist(playlist_uri)
        user_playlist = self.session.user.playlist(playlist_uri)

        # Clear existing tracks
        user_playlist.clear()

        # Add new tracks
        if track_uris:
            user_playlist.add(track_uris)

    def search_artist(self, query: str, limit: int = 5) -> list[SearchResult]:
        results = self.session.search(query, models=[tidalapi.artist.Artist], limit=limit)
        artists = results.get("artists", [])
        return [
            SearchResult(
                name=a.name,
                uri=str(a.id),
                genres=[],  # Tidal doesn't expose genres on artist search
                popularity=getattr(a, "popularity", 0) or 0,
            )
            for a in artists
        ]


def _save_session(session: tidalapi.Session, path: Path) -> None:
    """Persist Tidal session tokens to a JSON file."""
    data = {
        "token_type": session.token_type,
        "access_token": session.access_token,
        "refresh_token": session.refresh_token,
        "expiry_time": session.expiry_time.isoformat() if session.expiry_time else None,
    }
    path.write_text(json.dumps(data, indent=2))
