import base64 #for decoding the client id and secret
import os #for getting the client id and secret from the environment variables

import requests #for making the request to the Spotify API
from flask import Blueprint, jsonify #for creating the blueprint and returning the json response
# Blueprint is the 


spotify_bp = Blueprint("spotify", __name__)
artist_id="0TnOYISbd1XYRBk9myaseg" # artist id for pitbull 


def _request_access_token():
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

    auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode("utf-8")).decode(
        "utf-8"
    ) #must be encoded in base64 or spotify will not accept the request

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


@spotify_bp.get("/token")
def get_token():
    token_data = _request_access_token()
    return jsonify(token_data)


@spotify_bp.get("/artist")
def get_default_artist():
    token_data = _request_access_token()
    response = requests.get(
        f"https://api.spotify.com/v1/artists/{artist_id}",
        headers={"Authorization": f"Bearer {token_data['access_token']}"},
        timeout=10,
    )
    response.raise_for_status()
    return jsonify(response.json())


