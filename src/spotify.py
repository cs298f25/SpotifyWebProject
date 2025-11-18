import base64
import os
import time
import requests
from flask import Blueprint, jsonify

spotify_bp = Blueprint("spotify", __name__)
artist_id = "0TnOYISbd1XYRBk9myaseg" # pitbull
_access_token = None
_token_expires_at = 0

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


def _get_access_token():
    global _access_token, _token_expires_at

    if _access_token and time.time() < _token_expires_at:
        return _access_token

    token_data = _request_access_token()
    _access_token = token_data["access_token"]
    _token_expires_at = time.time() + token_data["expires_in"] - 60
    print("Requesting new Spotify token...")
    return _access_token



@spotify_bp.get("/token")
def get_token():
    token = _get_access_token()
    return jsonify({"access_token": token})


@spotify_bp.get("/artist")
def get_default_artist():
    access_token = _get_access_token()
    response = requests.get(
    f"https://api.spotify.com/v1/artists/{artist_id}",
    headers={"Authorization": f"Bearer {access_token}"},
    timeout=10,
)
response.raise_for_status()
return jsonify(response.json())


