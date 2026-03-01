"""Playlist building algorithm for Village Radio.

The ordering logic:
1. Pinned tracks at the top, in configured order
2. Fetch recent releases for all artists
3. Deduplicate: if a pinned track is also a new release, pinned wins
4. Sort new releases newest-first
5. Sample favorites_count from the favorites pool
6. Sprinkle favorites evenly through the non-pinned portion
7. Truncate to max_tracks — pinned are sacred, favorites get reserved slots
"""

import random
from dataclasses import dataclass

from config import RadioConfig, Track
from platforms.base import Release


@dataclass
class PlaylistResult:
    """The result of building a playlist."""

    tracks: list[Track]
    new_releases: list[Release]
    favorites_drawn: list[Track]
    pinned_count: int
    total_count: int


def _track_uri(track: Track, platform: str) -> str:
    """Get the URI for a track on the active platform."""
    return track.uri_for(platform)


def build_playlist(
    config: RadioConfig,
    releases: list[Release],
    seed: int | None = None,
) -> PlaylistResult:
    """Build a playlist from config and fetched releases.

    Args:
        config: The radio config with artists, pinned, favorites, settings.
        releases: Recent releases fetched from the platform.
        seed: Optional random seed for reproducible favorite selection.
    """
    if seed is not None:
        random.seed(seed)

    platform = config.platform
    max_tracks = config.settings.max_tracks
    favorites_count = min(config.settings.favorites_count, len(config.favorites))

    # 1. Pinned tracks — sacred, always at the top
    pinned_uris = {_track_uri(t, platform) for t in config.pinned}
    pinned_tracks = list(config.pinned)

    # 2. Collect all tracks from new releases
    release_tracks = []
    for release in releases:
        for track_data in release.tracks:
            # 3. Deduplicate: skip if already pinned
            if track_data["uri"] in pinned_uris:
                continue
            track_kwargs = {
                "name": track_data["name"],
                f"{platform}_uri": track_data["uri"],
                "artist": release.artist_name,
            }
            release_tracks.append(Track(**track_kwargs))

    # 4. Sort by release date (releases are already per-artist, but we want
    # global newest-first). We use the release's date for all its tracks.
    release_date_map = {}
    for release in releases:
        for track_data in release.tracks:
            release_date_map[track_data["uri"]] = release.release_date

    release_tracks.sort(
        key=lambda t: release_date_map.get(_track_uri(t, platform), 0),
        reverse=True,
    )

    # Deduplicate release tracks (same track can appear in album + single)
    seen_uris = set(pinned_uris)
    deduped_releases = []
    for track in release_tracks:
        uri = _track_uri(track, platform)
        if uri not in seen_uris:
            seen_uris.add(uri)
            deduped_releases.append(track)

    # 5. Sample favorites (excluding anything already in the list)
    available_favorites = [
        f for f in config.favorites if _track_uri(f, platform) not in seen_uris
    ]
    favorites_drawn = random.sample(
        available_favorites,
        min(favorites_count, len(available_favorites)),
    )

    # 7. Budget: pinned are sacred, favorites get reserved slots, releases fill the rest
    pinned_count = len(pinned_tracks)
    fav_count = len(favorites_drawn)
    release_budget = max_tracks - pinned_count - fav_count
    trimmed_releases = deduped_releases[:max(0, release_budget)]

    # 6. Sprinkle favorites evenly through the non-pinned portion
    body = _sprinkle(trimmed_releases, favorites_drawn)

    final_tracks = pinned_tracks + body

    return PlaylistResult(
        tracks=final_tracks,
        new_releases=releases,
        favorites_drawn=favorites_drawn,
        pinned_count=pinned_count,
        total_count=len(final_tracks),
    )


def _sprinkle(main: list[Track], extras: list[Track]) -> list[Track]:
    """Distribute extras evenly through main.

    If main has 20 items and extras has 4, place an extra roughly every 5 items.
    """
    if not extras:
        return list(main)
    if not main:
        return list(extras)

    result = []
    # Calculate even spacing
    total = len(main) + len(extras)
    interval = total / (len(extras) + 1)

    extra_idx = 0
    main_idx = 0
    for i in range(total):
        # Should we place a favorite at this position?
        if extra_idx < len(extras) and i + 1 >= interval * (extra_idx + 1):
            result.append(extras[extra_idx])
            extra_idx += 1
        else:
            if main_idx < len(main):
                result.append(main[main_idx])
                main_idx += 1

    # Append any remaining
    result.extend(main[main_idx:])
    result.extend(extras[extra_idx:])

    return result
