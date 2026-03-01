# /village-radio:add-artist

Search Spotify for an artist and add them to your radio config.

## What this does

1. Take the artist name from `$ARGUMENTS`
2. Run `village-radio/scripts/radio.py --mode add-artist --config $CONFIG_PATH --artist "$ARGUMENTS"`
3. Show search results, confirm the right match with the user
4. Append the artist to the config YAML (preserving comments and formatting via ruamel.yaml)

## Arguments

- `$ARGUMENTS`: Artist name to search for (required)

## Running

```bash
cd village-radio/scripts && python radio.py --mode add-artist --config "$CONFIG_PATH" --artist "$ARGUMENTS"
```
