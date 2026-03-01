"""Tests for the playlist builder algorithm."""

import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add scripts dir to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import RadioConfig, PlaylistConfig, Settings, Artist, Track
from platforms.base import Release
from playlist_builder import build_playlist, _sprinkle


def make_config(
    artists=None,
    pinned=None,
    favorites=None,
    max_tracks=50,
    favorites_count=5,
):
    return RadioConfig(
        playlist=PlaylistConfig(spotify_uri="spotify:playlist:test123"),
        settings=Settings(max_tracks=max_tracks, favorites_count=favorites_count),
        artists=artists or [],
        pinned=pinned or [],
        favorites=favorites or [],
    )


def make_release(name, artist, track_count=2, days_ago=3):
    release_date = datetime.now() - timedelta(days=days_ago)
    tracks = [
        {"name": f"{name} - Track {i+1}", "uri": f"spotify:track:{name.lower().replace(' ', '_')}_{i}"}
        for i in range(track_count)
    ]
    return Release(
        name=name,
        uri=f"spotify:album:{name.lower().replace(' ', '_')}",
        artist_name=artist,
        artist_uri=f"spotify:artist:{artist.lower().replace(' ', '_')}",
        release_date=release_date,
        release_type="single",
        tracks=tracks,
    )


def test_empty_releases():
    """Empty release week — should still include pinned and favorites."""
    config = make_config(
        pinned=[Track("Pinned One", "spotify:track:pin1", "Me")],
        favorites=[Track("Fav One", "spotify:track:fav1", "Them")],
        favorites_count=1,
    )
    result = build_playlist(config, [], seed=42)
    assert result.pinned_count == 1
    assert result.total_count == 2
    assert result.tracks[0].name == "Pinned One"
    assert result.tracks[1].name == "Fav One"
    print("  pass: empty releases")


def test_pinned_dedup():
    """If a pinned track also appears as a new release, pinned wins."""
    pinned_uri = "spotify:track:shared"
    config = make_config(
        pinned=[Track("Shared Track", pinned_uri, "Me")],
    )
    release = make_release("New Album", "Me", track_count=1)
    release.tracks = [{"name": "Shared Track", "uri": pinned_uri}]

    result = build_playlist(config, [release], seed=42)
    uris = [t.spotify_uri for t in result.tracks]
    assert uris.count(pinned_uri) == 1, "Pinned track should not appear twice"
    assert result.tracks[0].spotify_uri == pinned_uri
    print("  pass: pinned dedup")


def test_truncation():
    """More tracks than max_tracks — should truncate, pinned are sacred."""
    config = make_config(
        pinned=[Track("Pin", "spotify:track:pin", "Me")],
        max_tracks=5,
        favorites_count=0,
    )
    releases = [make_release(f"Release {i}", f"Artist {i}", track_count=3) for i in range(5)]

    result = build_playlist(config, releases, seed=42)
    assert result.total_count == 5, f"Expected 5 tracks, got {result.total_count}"
    assert result.tracks[0].name == "Pin"
    print("  pass: truncation")


def test_sprinkle_distribution():
    """Favorites should be distributed evenly, not clumped."""
    main = [Track(f"Track {i}", f"spotify:track:t{i}") for i in range(20)]
    extras = [Track(f"Fav {i}", f"spotify:track:f{i}") for i in range(4)]

    result = _sprinkle(main, extras)
    assert len(result) == 24

    # Find positions of favorites
    fav_uris = {f.spotify_uri for f in extras}
    positions = [i for i, t in enumerate(result) if t.spotify_uri in fav_uris]
    assert len(positions) == 4

    # Check they're roughly evenly spaced (not all clumped at start or end)
    gaps = [positions[i+1] - positions[i] for i in range(len(positions) - 1)]
    assert all(g >= 2 for g in gaps), f"Favorites too close together: positions={positions}"
    print("  pass: sprinkle distribution")


def test_small_favorites_pool():
    """Fewer favorites available than favorites_count — use what's there."""
    config = make_config(
        favorites=[Track("Only Fav", "spotify:track:fav1", "Someone")],
        favorites_count=5,
    )
    release = make_release("New One", "Artist", track_count=3)
    result = build_playlist(config, [release], seed=42)
    assert len(result.favorites_drawn) == 1
    print("  pass: small favorites pool")


def test_newest_first():
    """New releases should be sorted newest-first."""
    config = make_config(max_tracks=10, favorites_count=0)
    old = make_release("Old", "Artist A", track_count=1, days_ago=10)
    new = make_release("New", "Artist B", track_count=1, days_ago=1)

    result = build_playlist(config, [old, new], seed=42)
    # New release should come before old
    names = [t.name for t in result.tracks]
    new_idx = next(i for i, n in enumerate(names) if "New" in n)
    old_idx = next(i for i, n in enumerate(names) if "Old" in n)
    assert new_idx < old_idx, f"New ({new_idx}) should come before Old ({old_idx})"
    print("  pass: newest first")


def test_full_scenario():
    """Full scenario: pinned + releases + favorites, everything plays together."""
    config = make_config(
        pinned=[
            Track("My Single", "spotify:track:mine", "Me"),
            Track("Homie Feature", "spotify:track:homie", "Homie"),
        ],
        favorites=[
            Track("Classic 1", "spotify:track:c1", "Legend"),
            Track("Classic 2", "spotify:track:c2", "Icon"),
            Track("Classic 3", "spotify:track:c3", "Goat"),
        ],
        max_tracks=15,
        favorites_count=2,
    )
    releases = [
        make_release("Fresh Drop", "New Artist", track_count=3, days_ago=2),
        make_release("Also New", "Other Artist", track_count=2, days_ago=5),
    ]

    result = build_playlist(config, releases, seed=42)

    # Pinned at the top
    assert result.tracks[0].name == "My Single"
    assert result.tracks[1].name == "Homie Feature"
    assert result.pinned_count == 2

    # Favorites drawn
    assert len(result.favorites_drawn) == 2

    # Total within budget
    assert result.total_count <= 15

    print("  pass: full scenario")


if __name__ == "__main__":
    print("playlist builder tests:\n")
    test_empty_releases()
    test_pinned_dedup()
    test_truncation()
    test_sprinkle_distribution()
    test_small_favorites_pool()
    test_newest_first()
    test_full_scenario()
    print("\nall tests passed.")
