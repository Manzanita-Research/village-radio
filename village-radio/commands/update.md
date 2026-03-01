# /village-radio:update

Full playlist update — fetch new releases, build the playlist, push to Spotify.

## What this does

1. Load the user's radio config from the path stored in memory (ask if not set)
2. Run `village-radio/scripts/radio.py --mode update --config $CONFIG_PATH`
3. Report what changed: new releases found, tracks added, final playlist shape

## Arguments

- `$ARGUMENTS`: Optional config path override. If not provided, use the remembered path.

## Prerequisites

- Spotify credentials in env (`SPOTIPY_CLIENT_ID`, `SPOTIPY_CLIENT_SECRET`)
- OAuth tokens cached (run `/village-radio:setup` first if not)
- A valid radio config YAML

## Running

```bash
cd village-radio/scripts && python radio.py --mode update --config "$CONFIG_PATH"
```

If the script exits non-zero, show the error and suggest `/village-radio:setup` if it looks like an auth issue.
