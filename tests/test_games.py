from typing import Any
import pytest
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from games import Games
from database.in_memory_storage import InMemoryDatabase

@pytest.fixture
def in_memory_db():
    """Provides an in-memory database for testing."""
    return InMemoryDatabase()


@pytest.fixture
def games_service(in_memory_db):
    """Provides a Games service instance with in-memory database."""
    return Games(in_memory_db)

# test game creation
def test_game_creation(games_service):
    """Test game creation: create a new game and check if it exists."""
    game_id = "test_game"
    answer_data = {
        "name": "Pitbull",
        "gender": "male",
        "area": {"name": "United States"},
        "tag": "dance-pop",
        "spotify popularity": 85
    }
    games_service.new_game(game_id, answer_data)
    assert games_service.exists(game_id) == True

# test game selects a random artist
def test_game_select_random_answer(games_service):
    from games import POSSIBLE_ANSWERS
    
    # Select a random artist
    artist = games_service.select_random_artist()
    
    # Verify it returns a string
    assert artist is not None
    assert isinstance(artist, str)
    
    # Verify the artist is in the possible answers list
    assert artist in POSSIBLE_ANSWERS
    
    # Test multiple calls to verify randomness (at least one should be different if called enough times)
    artists_selected = [games_service.select_random_artist() for _ in range(10)]
    # Verify all selections are valid
    assert all(a in POSSIBLE_ANSWERS for a in artists_selected)


# tests an invalid guess (guess doesn't exist in the game)
def test_game_takes_invalid_guess(games_service):
    game_id = "test_game"
    # Verify the game doesn't exist
    assert games_service.exists(game_id) == False
    
    guess_data = {
        "name": "Taylor Swift",
        "gender": "female",
        "area": {"name": "United States"},
        "tag": "pop",
        "spotify popularity": 92
    }
    # Make a guess on a non-existent game - should return None
    comparison = games_service.guess(game_id, guess_data)
    assert comparison is None

# tests a correct guess (guess is the same as the answer)
def test_game_correct_guess(games_service):
    game_id = "test_game"
    answer_data = {
        "name": "Pitbull",
        "gender": "male",
        "area": {"name": "United States"},
        "tag": "dance-pop",
        "spotify popularity": 85
    }
    games_service.new_game(game_id, answer_data)
    guess_data = {
        "name": "Pitbull",
        "gender": "male",
        "area": {"name": "United States"},
        "tag": "dance-pop",
        "spotify popularity": 85
    }
    comparison = games_service.guess(game_id, guess_data)
    assert comparison is not None
    assert "guess_artist" in comparison
    assert comparison["is_correct"] == True
    assert comparison["fields"]["gender"] == "match"
    assert comparison["fields"]["area"] == "match"
    assert comparison["fields"]["popularity"] == "match"

# test a guess that is incorrect (different artist name, different gender, same area, guess is higher than answer)
def test_game_incorrect_guess1(games_service):
    # Set up test data - create a game with answer data
    game_id = "test_game"
    answer_data = {
        "name": "Pitbull",
        "gender": "male",
        "area": {"name": "United States"},
        "tag": "dance-pop",
        "spotify popularity": 85
    }
    
    # Create a new game with the answer data
    games_service.new_game(game_id, answer_data)
    
    # Create guess data that differs from the answer
    guess_data = {
        "name": "Taylor Swift",
        "gender": "female",
        "area": {"name": "United States"},
        "tag": "pop",
        "spotify popularity": 92
    }
    
    # Make a guess and get the comparison results
    comparison = games_service.guess(game_id, guess_data)
    
    # the comparison was created, the guess was incorrect (different artist name, different gender, same area, guess is higher than answer)
    assert comparison is not None
    assert comparison["is_correct"] == False
    assert comparison["fields"]["gender"] == "no_match"
    assert comparison["fields"]["area"] == "match"
    assert comparison["fields"]["popularity"] == "higher"

# test a guess that is incorrect (different artist name, different gender, different area, guess is lower than answer)
def test_game_incorrect_guess2(games_service):
    # Set up test data - create a game with answer data
    game_id = "test_game"
    answer_data = {
        "name": "Pitbull",
        "gender": "male",
        "area": {"name": "United States"},
        "tag": "dance-pop",
        "spotify popularity": 85
    }

    # Create a new game with the answer data
    games_service.new_game(game_id, answer_data)
    
    # Create guess data that differs from the answer (popularity is lower than answer)
    guess_data = {
        "name": "Taylor Swift",
        "gender": "female",
        "area": {"name": "Canada"},
        "tag": "pop",
        "spotify popularity": 70
    }

    # Make a guess and get the comparison results
    comparison = games_service.guess(game_id, guess_data)
    
    # the comparison was created, the guess was incorrect (different artist name, different gender, different area, guess is lower than answer)
    assert comparison is not None
    assert comparison["is_correct"] == False
    assert comparison["fields"]["gender"] == "no_match"
    assert comparison["fields"]["area"] == "no_match"
    assert comparison["fields"]["popularity"] == "lower"

# test build_guess_response with WON status
def test_build_guess_response_won(games_service):
    """Test build_guess_response returns WON status when guess is correct."""
    game_id = "test_game"
    answer_data = {
        "name": "Pitbull",
        "gender": "male",
        "area": {"name": "United States"},
        "tag": "dance-pop",
        "spotify popularity": 85
    }
    games_service.new_game(game_id, answer_data)
    guess_data = {
        "name": "Pitbull",
        "gender": "male",
        "area": {"name": "United States"},
        "tag": "dance-pop",
        "spotify popularity": 85
    }
    comparison = games_service.guess(game_id, guess_data)
    response = games_service.build_guess_response(comparison)
    
    assert response["status"] == "WON"
    assert response["is_correct"] == True
    assert response["guess_number"] == 1
    assert response["max_guesses"] == 7
    assert "answer" in response
    assert response["answer"]["name"] == "Pitbull"

# test build_guess_response with LOST status (7 incorrect guesses)
def test_build_guess_response_lost(games_service):
    """Test build_guess_response returns LOST status after 7 incorrect guesses."""
    game_id = "test_game"
    answer_data = {
        "name": "Pitbull",
        "gender": "male",
        "area": {"name": "United States"},
        "tag": "dance-pop",
        "spotify popularity": 85
    }
    games_service.new_game(game_id, answer_data)
    
    # Make 7 incorrect guesses
    guesses_data = [
        {"name": "Taylor Swift", "gender": "female", "area": {"name": "United States"}, "tag": "pop", "spotify popularity": 92},
        {"name": "Drake", "gender": "male", "area": {"name": "Canada"}, "tag": "hip-hop", "spotify popularity": 88},
        {"name": "Adele", "gender": "female", "area": {"name": "United Kingdom"}, "tag": "soul", "spotify popularity": 80},
        {"name": "Harry Styles", "gender": "male", "area": {"name": "United Kingdom"}, "tag": "pop", "spotify popularity": 87},
        {"name": "Kendrick Lamar", "gender": "male", "area": {"name": "United States"}, "tag": "hip-hop", "spotify popularity": 83},
        {"name": "Bad Bunny", "gender": "male", "area": {"name": "Puerto Rico"}, "tag": "reggaeton", "spotify popularity": 90},
        {"name": "Post Malone", "gender": "male", "area": {"name": "United States"}, "tag": "hip-hop", "spotify popularity": 89}
    ]
    
    for guess_data in guesses_data:
        comparison = games_service.guess(game_id, guess_data)
    
    # Build response for the last guess (7th guess)
    response = games_service.build_guess_response(comparison)
    
    assert response["status"] == "LOST"
    assert response["is_correct"] == False
    assert response["guess_number"] == 7
    assert response["max_guesses"] == 7
    assert "answer" in response
    assert response["answer"]["name"] == "Pitbull"

# test build_guess_response with ONGOING status
def test_build_guess_response_ongoing(games_service):
    """Test build_guess_response returns ONGOING status for mid-game guesses."""
    game_id = "test_game"
    answer_data = {
        "name": "Pitbull",
        "gender": "male",
        "area": {"name": "United States"},
        "tag": "dance-pop",
        "spotify popularity": 85
    }
    games_service.new_game(game_id, answer_data)
    
    # Make an incorrect guess (not the 7th)
    guess_data = {
        "name": "Taylor Swift",
        "gender": "female",
        "area": {"name": "United States"},
        "tag": "pop",
        "spotify popularity": 92
    }
    comparison = games_service.guess(game_id, guess_data)
    response = games_service.build_guess_response(comparison)
    
    assert response["status"] == "ONGOING"
    assert response["is_correct"] == False
    assert response["guess_number"] == 1
    assert response["max_guesses"] == 7
    assert "answer" not in response  # Answer not revealed during ongoing game

# test determine_game_status method
def test_determine_game_status(games_service):
    """Test determine_game_status returns correct status for different scenarios."""
    # Test WON status
    comparison_won = {"is_correct": True, "guess_number": 1}
    assert games_service.determine_game_status(comparison_won) == "WON"
    
    # Test LOST status (7th guess, incorrect)
    comparison_lost = {"is_correct": False, "guess_number": 7}
    assert games_service.determine_game_status(comparison_lost) == "LOST"
    
    # Test ONGOING status (mid-game, incorrect)
    comparison_ongoing = {"is_correct": False, "guess_number": 3}
    assert games_service.determine_game_status(comparison_ongoing) == "ONGOING"

# test genre/tag field comparison
def test_genre_tag_comparison(games_service):
    """Test that genre/tag field comparison works correctly."""
    game_id = "test_game"
    answer_data = {
        "name": "Pitbull",
        "gender": "male",
        "area": {"name": "United States"},
        "tag": "dance-pop",
        "spotify popularity": 85
    }
    games_service.new_game(game_id, answer_data)
    
    # Test matching genre
    guess_data_match = {
        "name": "Taylor Swift",
        "gender": "female",
        "area": {"name": "United States"},
        "tag": "dance-pop",
        "spotify popularity": 92
    }
    comparison = games_service.guess(game_id, guess_data_match)
    assert comparison["fields"]["genre"] == "match"
    
    # Test non-matching genre
    guess_data_no_match = {
        "name": "Drake",
        "gender": "male",
        "area": {"name": "Canada"},
        "tag": "hip-hop",
        "spotify popularity": 88
    }
    comparison2 = games_service.guess(game_id, guess_data_no_match)
    assert comparison2["fields"]["genre"] == "no_match"

# test a guess that is unknown (guess data is unknown)
def test_game_unknown_guess_data(games_service):
    # Set up test data - create a game with answer data
    game_id = "test_game"
    answer_data = {
        "name": "Pitbull",
        "gender": "male",
        "area": {"name": "United States"},
        "tag": "dance-pop",
        "spotify popularity": 85
    }
    games_service.new_game(game_id, answer_data)

    # Create guess data that is unknown
    guess_data = {
        "name": "Unknown",
        "gender": "Unknown",
        "area": {"name": "Unknown"},
        "tag": "Unknown",
        "spotify popularity": 0
    }
    
    # Make a guess and get the comparison results
    comparison = games_service.guess(game_id, guess_data)
    assert comparison is not None
    assert comparison["is_correct"] == False
    assert comparison["fields"]["gender"] == "no_match"
    assert comparison["fields"]["area"] == "no_match"
    assert comparison["fields"]["popularity"] == "lower"

# test a guess with none values (guess data is none)
def test_game_guess_with_none_values(games_service):
    """Test that None values in guess data return 'unknown' for comparisons."""
    game_id = "test_game"
    answer_data = {
        "name": "Pitbull",
        "gender": "male",
        "area": {"name": "United States"},
        "tag": "dance-pop",
        "spotify popularity": 85
    }
    games_service.new_game(game_id, answer_data)
    guess_data = {
        "name": None,
        "gender": None,
        "area": None,
        "tag": None,
        "spotify popularity": None
    }
    comparison = games_service.guess(game_id, guess_data)
    assert comparison is not None
    assert "guess_artist" in comparison
    assert comparison["is_correct"] == False
    # When guess value is None, comparison should return "unknown"
    assert comparison["fields"]["gender"] == "unknown"
    assert comparison["fields"]["area"] == "unknown"
    assert comparison["fields"]["popularity"] == "unknown"

# test game guesses increment with 7 guesses
def test_game_guesses_increment(games_service):
    """Test that guess_number increments correctly through 7 guesses."""
    game_id = "test_game"
    answer_data = {
        "name": "Pitbull",
        "gender": "male",
        "area": {"name": "United States"},
        "tag": "dance-pop",
        "spotify popularity": 85
    }
    games_service.new_game(game_id, answer_data)
    
    # List of different artists to guess
    guesses_data = [
        {"name": "Taylor Swift", "gender": "female", "area": {"name": "United States"}, "tag": "pop", "spotify popularity": 92},
        {"name": "Drake", "gender": "male", "area": {"name": "Canada"}, "tag": "hip-hop", "spotify popularity": 88},
        {"name": "Adele", "gender": "female", "area": {"name": "United Kingdom"}, "tag": "soul", "spotify popularity": 80},
        {"name": "Harry Styles", "gender": "male", "area": {"name": "United Kingdom"}, "tag": "pop", "spotify popularity": 87},
        {"name": "Kendrick Lamar", "gender": "male", "area": {"name": "United States"}, "tag": "hip-hop", "spotify popularity": 83},
        {"name": "Bad Bunny", "gender": "male", "area": {"name": "Puerto Rico"}, "tag": "reggaeton", "spotify popularity": 90},
        {"name": "Post Malone", "gender": "male", "area": {"name": "United States"}, "tag": "hip-hop", "spotify popularity": 89}
    ]
    
    # Make 7 guesses and verify each guess_number increments correctly
    for i, guess_data in enumerate[dict[str, Any]](guesses_data, start=1):
        comparison = games_service.guess(game_id, guess_data)
        assert comparison is not None
        assert comparison["guess_number"] == i