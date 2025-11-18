import base64
import os
import requests

# Requests an access token from Spotify with the client id and client secret
def _request_access_token():
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

    auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode("utf-8")).decode("utf-8")

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
    return response.json()

# Gets the popularity of an artist by query
def get_artist_popularity(query):
    token_data = _request_access_token()
    response = requests.get(
        f"https://api.spotify.com/v1/search?q={query}&type=artist&limit=1",
        headers={"Authorization": f"Bearer {token_data['access_token']}"},
        timeout=10,
    )
    response.raise_for_status()
    data = response.json()
    artist = data["artists"]["items"][0]
    return artist["popularity"]

