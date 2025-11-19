import musicbrainzngs
import os
from flask import Blueprint, jsonify, request
from spotify import get_artist_popularity

musicbrain_bp = Blueprint("musicbrain", __name__)

# initialize musicbrainz and set user agent
def _initialize_musicbrainz():
    musicbrainzngs.set_useragent(
        "ArtistGuesser",
        "1.0",
        os.getenv("USER_EMAIL")   
    )

# search for artists
@musicbrain_bp.get("/search")
def search_artists():
    query = request.args.get("q")
    full_artist = _get_full_artist_by_query(query)
    full_artist = _filter_to_highest_tag(full_artist)
    
    popularity = get_artist_popularity(query)
    artist = full_artist["artist"] # artist is the full artist data

    # filtered_result is the filtered artist data
    filtered_result = {
        "name": artist.get("name"),
        "type": artist.get("type"),
        "gender": artist.get("gender"),
        "life-span": artist.get("life-span"),
        "area": {"name": artist.get("area", {}).get("name")} if artist.get("area") else None,
        "spotify popularity": popularity,
        "tag": artist["tag-list"][0]["name"] if artist.get("tag-list") and len(artist["tag-list"]) > 0 else None
        }
    
    return jsonify(filtered_result)

# Get the full artist's data by query
def _get_full_artist_by_query(query):
    _initialize_musicbrainz()
    result = musicbrainzngs.search_artists(query=query, limit=1)
    artist = result["artist-list"][0]
    full_artist = musicbrainzngs.get_artist_by_id(artist["id"], includes=["tags"])
    return full_artist

# Filters the search artist results data to the highest tag 
def _filter_to_highest_tag(artist_data):
    if "tag-list" in artist_data["artist"] and artist_data["artist"]["tag-list"]:
        tag_list = artist_data["artist"]["tag-list"]
        highest_tag = max(tag_list, key=lambda x: int(x.get("count", 0)))
        artist_data["artist"]["tag-list"] = [highest_tag]
    return artist_data

#Gets 
def get_artist_highest_tag(query):
    full_artist = _get_full_artist_by_query(query)
    full_artist = _filter_to_highest_tag(full_artist)
    
    if "tag-list" in full_artist["artist"] and full_artist["artist"]["tag-list"]:
        return full_artist["artist"]["tag-list"][0]
    return None


