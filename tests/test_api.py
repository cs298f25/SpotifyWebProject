import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock, Mock
import time

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from spotify import get_artist_popularity, _request_access_token
from musicbrain import (
    get_artist_data_for_game,
    get_artist_highest_tag,
    _filter_to_highest_tag,
    _initialize_musicbrainz,
)


# ========== SPOTIFY API TESTS ==========

#test when user does not have the spotfiy client id or secret
@patch.dict("os.environ", {})
def test_request_access_token_no_credentials():
    """Test that _request_access_token raises an exception when no credentials are set."""
    with pytest.raises(Exception):
        _request_access_token()

# test a successful token request
@patch.dict("os.environ", {"SPOTIFY_CLIENT_ID": "test_id", "SPOTIFY_CLIENT_SECRET": "test_secret"})
@patch("spotify.requests.post")
def test_request_access_token_success(mock_post):
    """Test that _request_access_token successfully gets a token."""
    # Reset cache before test
    import spotify
    spotify._cached_token = None
    spotify._cached_token_expiry = 0
    
    # Mock the token response
    mock_response = MagicMock()
    mock_response.json.return_value = {"access_token": "test_token_123", "expires_in": 3600}
    mock_response.raise_for_status = MagicMock()
    mock_post.return_value = mock_response
    
    token = _request_access_token()
    
    assert token == "test_token_123"
    mock_post.assert_called_once()
    assert "Basic" in mock_post.call_args[1]["headers"]["Authorization"]

# test that the token is cached and reused
@patch.dict("os.environ", {"SPOTIFY_CLIENT_ID": "test_id", "SPOTIFY_CLIENT_SECRET": "test_secret"})
@patch("spotify.requests.post")
def test_request_access_token_caching(mock_post):
    """Test that _request_access_token caches tokens and reuses them."""
    # Reset cache before test
    import spotify
    spotify._cached_token = None
    spotify._cached_token_expiry = 0
    
    # Mock the token response
    mock_response = MagicMock()
    mock_response.json.return_value = {"access_token": "cached_token", "expires_in": 3600}
    mock_response.raise_for_status = MagicMock()
    mock_post.return_value = mock_response
    
    # First call - should request token
    token1 = _request_access_token()
    assert token1 == "cached_token"
    assert mock_post.call_count == 1
    
    # Second call - should use cached token
    token2 = _request_access_token()
    assert token2 == "cached_token"
    assert mock_post.call_count == 1  # Should not make another request

# test that a new token is requested when the cached one expires
@patch.dict("os.environ", {"SPOTIFY_CLIENT_ID": "test_id", "SPOTIFY_CLIENT_SECRET": "test_secret"})
@patch("spotify.requests.post")
def test_request_access_token_expires(mock_post):
    """Test that _request_access_token requests new token when cached one expires."""
    # Reset cache before test
    import spotify
    spotify._cached_token = None
    spotify._cached_token_expiry = 0
    
    # Mock the token response
    mock_response = MagicMock()
    mock_response.json.return_value = {"access_token": "new_token", "expires_in": 3600}
    mock_response.raise_for_status = MagicMock()
    mock_post.return_value = mock_response
    
    # First call
    token1 = _request_access_token()
    assert mock_post.call_count == 1
    
    # Simulate token expiry by manipulating the cache
    spotify._cached_token_expiry = time.time() - 100  # Expired
    
    # Second call - should request new token
    token2 = _request_access_token()
    assert token2 == "new_token"
    assert mock_post.call_count == 2

# test that get_artist_popularity returns the popularity score
@patch("spotify._request_access_token")
@patch("spotify.requests.get")
def test_get_artist_popularity_success(mock_get, mock_token):
    """Test that get_artist_popularity returns popularity score."""
    # Mock token
    mock_token.return_value = "test_token"
    
    # Mock Spotify API response
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "artists": {
            "items": [{"popularity": 85}]
        }
    }
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response
    
    popularity = get_artist_popularity("Pitbull")
    
    assert popularity == 85
    mock_get.assert_called_once()
    assert "Bearer test_token" in mock_get.call_args[1]["headers"]["Authorization"]


# test that get_artist_popularity raises an exception on API error
@patch("spotify._request_access_token")
@patch("spotify.requests.get")
def test_get_artist_popularity_api_error(mock_get, mock_token):
    """Test that get_artist_popularity raises exception on API error."""
    mock_token.return_value = "test_token"
    
    # Mock API error
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = Exception("API Error")
    mock_get.return_value = mock_response
    
    with pytest.raises(Exception):
        get_artist_popularity("Pitbull")


# ========== MUSICBRAINZ API TESTS ==========

# test that _initialize_musicbrainz sets user agent correctly
@patch.dict("os.environ", {"USER_EMAIL": "test@example.com"})
@patch("musicbrain.musicbrainzngs.set_useragent")
def test_initialize_musicbrainz(mock_set_useragent):
    """Test that _initialize_musicbrainz sets user agent correctly."""
    _initialize_musicbrainz()
    
    mock_set_useragent.assert_called_once_with(
        "ArtistGuesser",
        "1.0",
        "test@example.com"
    )


# test that _initialize_musicbrainz uses default email when USER_EMAIL not set
@patch.dict("os.environ", {})
@patch("musicbrain.musicbrainzngs.set_useragent")
def test_initialize_musicbrainz_default_email(mock_set_useragent):
    """Test that _initialize_musicbrainz uses default email when USER_EMAIL not set."""
    _initialize_musicbrainz()
    
    mock_set_useragent.assert_called_once_with(
        "ArtistGuesser",
        "1.0",
        "example@example.com"
    )


# test that _filter_to_highest_tag filters to tag with highest count
def test_filter_to_highest_tag():
    """Test that _filter_to_highest_tag filters to tag with highest count."""
    artist_data = {
        "artist": {
            "tag-list": [
                {"name": "pop", "count": "5"},
                {"name": "dance-pop", "count": "10"},
                {"name": "hip-hop", "count": "3"}
            ]
        }
    }
    
    result = _filter_to_highest_tag(artist_data)
    
    assert len(result["artist"]["tag-list"]) == 1
    assert result["artist"]["tag-list"][0]["name"] == "dance-pop"
    assert result["artist"]["tag-list"][0]["count"] == "10"


# test that _filter_to_highest_tag handles artist with no tags
def test_filter_to_highest_tag_no_tags():
    """Test that _filter_to_highest_tag handles artist with no tags."""
    artist_data = {
        "artist": {}
    }
    
    result = _filter_to_highest_tag(artist_data)
    
    assert "tag-list" not in result["artist"] or not result["artist"].get("tag-list")


# test that _get_full_artist_by_query searches and retrieves full artist data
@patch("musicbrain.musicbrainzngs.get_artist_by_id")
@patch("musicbrain.musicbrainzngs.search_artists")
@patch("musicbrain._initialize_musicbrainz")
def test_get_full_artist_by_query(mock_init, mock_search, mock_get_by_id):
    """Test that _get_full_artist_by_query searches and retrieves full artist data."""
    # Mock search result
    mock_search.return_value = {
        "artist-list": [{"id": "test-artist-id", "name": "Pitbull"}]
    }
    
    # Mock full artist data
    mock_get_by_id.return_value = {
        "artist": {
            "id": "test-artist-id",
            "name": "Pitbull",
            "tag-list": []
        }
    }
    
    # Import the function to test it
    from musicbrain import _get_full_artist_by_query
    result = _get_full_artist_by_query("Pitbull")
    
    mock_init.assert_called_once()
    mock_search.assert_called_once_with(query="Pitbull", limit=1)
    mock_get_by_id.assert_called_once_with("test-artist-id", includes=["tags"])
    assert result["artist"]["name"] == "Pitbull"


# test that get_artist_data_for_game returns combined data from both APIs
@patch("musicbrain.get_artist_popularity")
@patch("musicbrain._get_full_artist_by_query")
@patch("musicbrain._filter_to_highest_tag")
def test_get_artist_data_for_game_success(mock_filter, mock_get_artist, mock_popularity):
    """Test that get_artist_data_for_game returns combined data from both APIs."""
    # Mock MusicBrainz data
    mock_get_artist.return_value = {
        "artist": {
            "name": "Pitbull",
            "type": "Person",
            "gender": "male",
            "life-span": {"begin": "1981-01-15", "ended": "false"},
            "area": {"name": "United States"},
            "tag-list": [{"name": "dance-pop", "count": "10"}]
        }
    }
    
    # Mock filtered data
    mock_filter.return_value = {
        "artist": {
            "name": "Pitbull",
            "type": "Person",
            "gender": "male",
            "life-span": {"begin": "1981-01-15", "ended": "false"},
            "area": {"name": "United States"},
            "tag-list": [{"name": "dance-pop", "count": "10"}]
        }
    }
    
    # Mock Spotify popularity
    mock_popularity.return_value = 85
    
    result = get_artist_data_for_game("Pitbull")
    
    assert result["name"] == "Pitbull"
    assert result["gender"] == "male"
    assert result["type"] == "Person"
    assert result["area"]["name"] == "United States"
    assert result["tag"] == "dance-pop"
    assert result["spotify popularity"] == 85


# test that get_artist_data_for_game handles artist with no tags
@patch("musicbrain.get_artist_popularity")
@patch("musicbrain._get_full_artist_by_query")
@patch("musicbrain._filter_to_highest_tag")
def test_get_artist_data_for_game_no_tags(mock_filter, mock_get_artist, mock_popularity):
    """Test that get_artist_data_for_game handles artist with no tags."""
    mock_get_artist.return_value = {
        "artist": {
            "name": "Pitbull",
            "gender": "male",
            "area": {"name": "United States"}
        }
    }
    
    mock_filter.return_value = {
        "artist": {
            "name": "Pitbull",
            "gender": "male",
            "area": {"name": "United States"}
        }
    }
    
    mock_popularity.return_value = 85
    
    result = get_artist_data_for_game("Pitbull")
    
    assert result["tag"] is None
    assert result["spotify popularity"] == 85


# test that get_artist_data_for_game handles artist with no area
@patch("musicbrain.get_artist_popularity")
@patch("musicbrain._get_full_artist_by_query")
@patch("musicbrain._filter_to_highest_tag")
def test_get_artist_data_for_game_no_area(mock_filter, mock_get_artist, mock_popularity):
    """Test that get_artist_data_for_game handles artist with no area."""
    mock_get_artist.return_value = {
        "artist": {
            "name": "Pitbull",
            "gender": "male",
            "tag-list": [{"name": "pop", "count": "5"}]
        }
    }
    
    mock_filter.return_value = {
        "artist": {
            "name": "Pitbull",
            "gender": "male",
            "tag-list": [{"name": "pop", "count": "5"}]
        }
    }
    
    mock_popularity.return_value = 85
    
    result = get_artist_data_for_game("Pitbull")
    
    assert result["area"] is None
    assert result["tag"] == "pop"


@patch("musicbrain._get_full_artist_by_query")
@patch("musicbrain._filter_to_highest_tag")
def test_get_artist_highest_tag_success(mock_filter, mock_get_artist):
    """Test that get_artist_highest_tag returns the highest tag."""
    mock_get_artist.return_value = {
        "artist": {
            "tag-list": [
                {"name": "pop", "count": "5"},
                {"name": "dance-pop", "count": "10"}
            ]
        }
    }
    
    mock_filter.return_value = {
        "artist": {
            "tag-list": [{"name": "dance-pop", "count": "10"}]
        }
    }
    
    result = get_artist_highest_tag("Pitbull")
    
    assert result["name"] == "dance-pop"
    assert result["count"] == "10"


# test that get_artist_highest_tag returns None when no tags exist
@patch("musicbrain._get_full_artist_by_query")
@patch("musicbrain._filter_to_highest_tag")
def test_get_artist_highest_tag_no_tags(mock_filter, mock_get_artist):
    """Test that get_artist_highest_tag returns None when no tags exist."""
    mock_get_artist.return_value = {"artist": {}}
    mock_filter.return_value = {"artist": {}}
    
    result = get_artist_highest_tag("Pitbull")
    
    assert result is None

