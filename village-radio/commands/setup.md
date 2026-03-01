# /village-radio:setup

First-time setup — Spotify auth and config path.

## What this does

1. Check for `SPOTIPY_CLIENT_ID` and `SPOTIPY_CLIENT_SECRET` in the environment
2. If missing, walk the user through creating a Spotify Developer app:
   - Go to https://developer.spotify.com/dashboard
   - Create an app, set redirect URI to `http://localhost:8888/callback`
   - Copy Client ID and Client Secret into shell profile
3. Run OAuth flow: `python radio.py --mode setup`
4. Ask for the path to their radio config YAML (or help them create one from the example)
5. Remember the config path for future runs

## Spotify App Registration

Tell the user:

> You need a Spotify Developer app. Here's how:
> 1. Go to https://developer.spotify.com/dashboard
> 2. Click "Create App"
> 3. Name it whatever you want (e.g., "Village Radio")
> 4. Set the redirect URI to `http://localhost:8888/callback`
> 5. Copy the Client ID and Client Secret
> 6. Add to your shell profile:
>    ```
>    export SPOTIPY_CLIENT_ID="your_client_id"
>    export SPOTIPY_CLIENT_SECRET="your_client_secret"
>    export SPOTIPY_REDIRECT_URI="http://localhost:8888/callback"
>    ```
> 7. Restart your terminal or `source` the profile

## Running

```bash
cd village-radio/scripts && python radio.py --mode setup
```
