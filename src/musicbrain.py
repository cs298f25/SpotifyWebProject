import musicbrainzngs
import os
from spotify import get_artist_popularity


def _initialize_musicbrainz():
    musicbrainzngs.set_useragent(
        "ArtistGuesser",
        "1.0",
        os.getenv("USER_EMAIL") or "example@example.com",
    )


def get_artist_data_for_game(query):
    """
    Returns a filtered artist dict with:
    - name
    - gender
    - area
    - tag (genre)
    - spotify popularity
    """
    full_artist = _get_full_artist_by_query(query)
    full_artist = _filter_to_highest_tag(full_artist)
    artist = full_artist["artist"]

    popularity = get_artist_popularity(query)

    filtered_result = {
        "name": artist.get("name"),
        "type": artist.get("type"),
        "gender": artist.get("gender"),
        "life-span": artist.get("life-span"),
        "area": (
            {"name": artist.get("area", {}).get("name")}
            if artist.get("area")
            else None
        ),
        "spotify popularity": popularity,
        "tag": artist["tag-list"][0]["name"]
        if artist.get("tag-list")
        else None,
    }

    return filtered_result


def _get_full_artist_by_query(query):
    _initialize_musicbrainz()
    result = musicbrainzngs.search_artists(query=query, limit=1)
    artist = result["artist-list"][0]
    full_artist = musicbrainzngs.get_artist_by_id(artist["id"], includes=["tags"])
    return full_artist


def _filter_to_highest_tag(artist_data):
    if "tag-list" in artist_data["artist"] and artist_data["artist"]["tag-list"]:
        tag_list = artist_data["artist"]["tag-list"]
        highest_tag = max(tag_list, key=lambda x: int(x.get("count", 0)))
        artist_data["artist"]["tag-list"] = [highest_tag]
    return artist_data


def get_artist_highest_tag(query):
    full_artist = _get_full_artist_by_query(query)
    full_artist = _filter_to_highest_tag(full_artist)

    if "tag-list" in full_artist["artist"] and full_artist["artist"]["tag-list"]:
        return full_artist["artist"]["tag-list"][0]
    return None
