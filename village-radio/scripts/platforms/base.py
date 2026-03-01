"""Abstract platform interface for Village Radio."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Release:
    """A release (album/single) from an artist."""

    name: str
    uri: str
    artist_name: str
    artist_uri: str
    release_date: datetime
    release_type: str  # album, single, appears_on
    tracks: list[dict]  # [{"name": ..., "uri": ...}, ...]


@dataclass
class SearchResult:
    """An artist search result."""

    name: str
    uri: str
    genres: list[str]
    popularity: int


class Platform(ABC):
    """Base interface for music platforms.

    Subclass this for Spotify, Tidal, etc.
    """

    @abstractmethod
    def authenticate(self) -> None:
        """Authenticate with the platform. Raises on failure."""

    @abstractmethod
    def get_artist_releases(
        self,
        artist_uri: str,
        lookback_days: int,
        include_groups: list[str],
    ) -> list[Release]:
        """Fetch recent releases for an artist."""

    @abstractmethod
    def replace_playlist(
        self,
        playlist_uri: str,
        track_uris: list[str],
    ) -> None:
        """Replace all tracks in a playlist."""

    @abstractmethod
    def search_artist(self, query: str, limit: int = 5) -> list[SearchResult]:
        """Search for artists by name."""
