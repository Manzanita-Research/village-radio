# /village-radio:dry-run

Preview this week's playlist without pushing changes to Spotify.

## What this does

1. Load the user's radio config
2. Run `village-radio/scripts/radio.py --mode dry-run --config $CONFIG_PATH`
3. Display the playlist: pinned tracks, new releases found, favorites drawn, final track order

## Arguments

- `$ARGUMENTS`: Optional config path override.

## Running

```bash
cd village-radio/scripts && python radio.py --mode dry-run --config "$CONFIG_PATH"
```
