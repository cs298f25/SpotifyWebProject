import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from app import create_app
from database.in_memory_storage import InMemoryDatabase
from games import Games


@pytest.fixture
def in_memory_db():
    """Provides an in-memory database for testing."""
    return InMemoryDatabase()


@pytest.fixture
def games_service(in_memory_db):
    """Provides a Games service instance with in-memory database."""
    return Games(in_memory_db)


@pytest.fixture
def app(games_service):
    """Provides a Flask app instance for testing."""
    return create_app("test_secret_key", games_service)


@pytest.fixture
def client(app):
    """Provides a Flask test client."""
    return app.test_client()


# test the home route
def test_home_route(client):
    """Test that the home route returns the index page."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.content_type == "text/html; charset=utf-8"


@patch("app.get_artist_data_for_game")
def test_new_game_success(mock_get_artist_data, client, games_service):
    """Test that /new-game successfully creates a new game."""
    # Mock the artist data response
    mock_get_artist_data.return_value = {
        "name": "Pitbull",
        "gender": "male",
        "area": {"name": "United States"},
        "tag": "dance-pop",
        "spotify popularity": 85
    }
    
    response = client.get("/new-game")
    assert response.status_code == 200
    data = response.get_json()
    assert data == {"ok": True}


@patch("app.get_artist_data_for_game")
def test_new_game_artist_lookup_fails(mock_get_artist_data, client):
    """Test that /new-game returns error when artist lookup fails."""
    # Mock the artist data to raise an exception
    mock_get_artist_data.side_effect = Exception("API Error")
    
    response = client.get("/new-game")
    assert response.status_code == 500
    data = response.get_json()
    assert data["error"] == "ERROR"
    assert "Could not start a new game" in data["message"]


def test_guess_no_game_exists(client):
    """Test that /guess returns error when no game exists."""
    response = client.post("/guess", json={"guess": "Taylor Swift"})
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "ERROR"
    assert data["message"] == "Game session invalid"


# test a guess when the guess is empty
@patch("app.get_artist_data_for_game")
def test_guess_empty_guess(mock_get_artist_data, client, games_service):
    """Test that /guess returns 400 error when guess is empty."""
    # Create a game via /new-game endpoint
    mock_get_artist_data.return_value = {
        "name": "Pitbull",
        "gender": "male",
        "area": {"name": "United States"},
        "tag": "dance-pop",
        "spotify popularity": 85
    }
    client.get("/new-game")
    
    # Test empty guess
    response = client.post("/guess", json={"guess": ""})
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "ERROR"
    assert "Guess must be a non-empty artist name" in data["message"]

# test a guess when the artist is not found
@patch("app.get_artist_data_for_game")
def test_guess_artist_not_found(mock_get_artist_data, client):
    """Test that /guess returns 500 error when artist lookup fails."""
    # Create a game via /new-game endpoint
    mock_get_artist_data.return_value = {
        "name": "Pitbull",
        "gender": "male",
        "area": {"name": "United States"},
        "tag": "dance-pop",
        "spotify popularity": 85
    }
    client.get("/new-game")
    
    # Mock artist lookup to fail for the guess
    mock_get_artist_data.side_effect = Exception("Artist not found")
    
    response = client.post("/guess", json={"guess": "Unknown Artist"})
    assert response.status_code == 500
    data = response.get_json()
    assert data["error"] == "ERROR"
    assert data["message"] == "Could not find that artist"


# test a successful guess
@patch("app.get_artist_data_for_game")
def test_guess_success(mock_get_artist_data, client):
    """Test that /guess returns 200 with valid JSON response structure."""
    # Create a game via /new-game endpoint
    mock_get_artist_data.return_value = {
        "name": "Pitbull",
        "gender": "male",
        "area": {"name": "United States"},
        "tag": "dance-pop",
        "spotify popularity": 85
    }
    client.get("/new-game")
    
    # Mock the guess artist data
    mock_get_artist_data.return_value = {
        "name": "Taylor Swift",
        "gender": "female",
        "area": {"name": "United States"},
        "tag": "pop",
        "spotify popularity": 92
    }
    
    response = client.post("/guess", json={"guess": "Taylor Swift"})
    assert response.status_code == 200
    assert response.content_type == "application/json"
    data = response.get_json()
    # Only verify HTTP response structure, not game logic
    assert "status" in data
    assert "comparison" in data
    assert isinstance(data["status"], str)
    assert isinstance(data["comparison"], dict)


# test a guess when comparison returns None
@patch("app.get_artist_data_for_game")
def test_guess_comparison_none(mock_get_artist_data, client, games_service):
    """Test that /guess returns 400 error when games_service.guess() returns None."""
    # Create a game via /new-game endpoint
    mock_get_artist_data.return_value = {
        "name": "Pitbull",
        "gender": "male",
        "area": {"name": "United States"},
        "tag": "dance-pop",
        "spotify popularity": 85
    }
    client.get("/new-game")
    
    # Mock the guess artist data
    mock_get_artist_data.return_value = {
        "name": "Taylor Swift",
        "gender": "female",
        "area": {"name": "United States"},
        "tag": "pop",
        "spotify popularity": 92
    }
    
    # Mock games_service.guess() to return None
    with patch.object(games_service, 'guess', return_value=None):
        response = client.post("/guess", json={"guess": "Taylor Swift"})
        assert response.status_code == 400
        data = response.get_json()
        assert data["error"] == "ERROR"
        assert data["message"] == "No result returned"

