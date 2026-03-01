"""Config loading and data model for Village Radio."""

from dataclasses import dataclass, field
from pathlib import Path

import yaml


SUPPORTED_PLATFORMS = ("spotify", "tidal")


@dataclass
class Artist:
    name: str
    spotify_uri: str = ""
    tidal_uri: str = ""
    bandcamp_url: str = ""


@dataclass
class Track:
    name: str
    spotify_uri: str = ""
    tidal_uri: str = ""
    artist: str = ""

    def uri_for(self, platform: str) -> str:
        """Return the URI for a given platform."""
        return getattr(self, f"{platform}_uri", "")


@dataclass
class PlaylistConfig:
    spotify_uri: str = ""
    tidal_uri: str = ""
    name: str = "Village Radio"

    def uri_for(self, platform: str) -> str:
        """Return the playlist URI for a given platform."""
        return getattr(self, f"{platform}_uri", "")


@dataclass
class Settings:
    lookback_days: int = 14
    max_tracks: int = 50
    favorites_count: int = 5
    include_groups: list[str] = field(
        default_factory=lambda: ["album", "single", "appears_on"]
    )
    rate_limit_delay: float = 0.5


@dataclass
class RadioConfig:
    playlist: PlaylistConfig
    settings: Settings
    artists: list[Artist]
    platform: str = "spotify"
    pinned: list[Track] = field(default_factory=list)
    favorites: list[Track] = field(default_factory=list)


def load_config(path: str | Path) -> RadioConfig:
    """Load a radio config from a YAML file."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Config not found: {path}")

    with open(path) as f:
        raw = yaml.safe_load(f)

    if not raw:
        raise ValueError(f"Empty config: {path}")

    platform = raw.get("platform", "spotify")
    if platform not in SUPPORTED_PLATFORMS:
        raise ValueError(f"Unsupported platform: {platform}. Choose from: {', '.join(SUPPORTED_PLATFORMS)}")

    uri_key = f"{platform}_uri"

    playlist_data = raw.get("playlist", {})
    if not playlist_data.get(uri_key):
        raise ValueError(f"Config must include playlist.{uri_key}")

    playlist = PlaylistConfig(
        spotify_uri=playlist_data.get("spotify_uri", ""),
        tidal_uri=playlist_data.get("tidal_uri", ""),
        name=playlist_data.get("name", "Village Radio"),
    )

    settings_data = raw.get("settings", {})
    settings = Settings(
        lookback_days=settings_data.get("lookback_days", 14),
        max_tracks=settings_data.get("max_tracks", 50),
        favorites_count=settings_data.get("favorites_count", 5),
        include_groups=settings_data.get(
            "include_groups", ["album", "single", "appears_on"]
        ),
        rate_limit_delay=settings_data.get("rate_limit_delay", 0.5),
    )

    artists = [
        Artist(
            name=a["name"],
            spotify_uri=a.get("spotify_uri", ""),
            tidal_uri=a.get("tidal_uri", ""),
            bandcamp_url=a.get("bandcamp_url", ""),
        )
        for a in raw.get("artists", [])
    ]

    pinned = [
        Track(
            name=t["name"],
            spotify_uri=t.get("spotify_uri", ""),
            tidal_uri=t.get("tidal_uri", ""),
            artist=t.get("artist", ""),
        )
        for t in raw.get("pinned", [])
    ]

    favorites = [
        Track(
            name=t["name"],
            spotify_uri=t.get("spotify_uri", ""),
            tidal_uri=t.get("tidal_uri", ""),
            artist=t.get("artist", ""),
        )
        for t in raw.get("favorites", [])
    ]

    return RadioConfig(
        playlist=playlist,
        settings=settings,
        artists=artists,
        platform=platform,
        pinned=pinned,
        favorites=favorites,
    )
