import base64
import os
import time
import requests

_cached_token = None
_cached_token_expiry = 0


def _request_access_token():
    """
    Request a Spotify access token, with simple in-process caching
    so we don't hit the token endpoint for every search.
    """
    global _cached_token, _cached_token_expiry

    if _cached_token and time.time() < _cached_token_expiry:
        return _cached_token

    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

    auth_header = base64.b64encode(
        f"{client_id}:{client_secret}".encode("utf-8")
    ).decode("utf-8")

    response = requests.post(
        "https://accounts.spotify.com/api/token",
        headers={
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data={"grant_type": "client_credentials"},
        timeout=10,
    )
    response.raise_for_status()
    token_data = response.json()

    _cached_token = token_data["access_token"]
    # Spotify tokens are usually ~3600 seconds; we renew a bit earlier
    _cached_token_expiry = time.time() + 3500

    return _cached_token


def get_artist_popularity(query):
    token = _request_access_token()

    response = requests.get(
        f"https://api.spotify.com/v1/search?q={query}&type=artist&limit=1",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10,
    )
    response.raise_for_status()
    data = response.json()
    artist = data["artists"]["items"][0]
    return artist["popularity"]
