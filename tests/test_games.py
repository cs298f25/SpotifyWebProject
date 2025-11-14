import pytest
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.games import Games
from database.in_memory_storage import InMemoryDatabase


@pytest.fixture
def in_memory_db():
    return InMemoryDatabase()


@pytest.fixture
def games_service(in_memory_db):
    return Games(in_memory_db)


def test_new_game(games_service):
    game_id = "test_game_1"
    answer = 42
    
    games_service.new_game(game_id, answer)
    
    assert games_service.exists(game_id)
    assert games_service.database.get_answer(game_id) == answer


def test_game_exists(games_service):
    game_id = "test_game_2"
    
    assert not games_service.exists(game_id)
    
    games_service.new_game(game_id, 100)
    assert games_service.exists(game_id)


def test_guess_records_guesses(games_service):
    game_id = "test_game_3"
    answer = 50
    
    games_service.new_game(game_id, answer)
    games_service.guess(game_id, 30)
    games_service.guess(game_id, 70)
    games_service.guess(game_id, 50)
    
    guesses = games_service.database.get_guesses(game_id)
    assert guesses == [30, 70, 50]


def test_guess_nonexistent_game(games_service):
    game_id = "nonexistent_game"
    
    result = games_service.guess(game_id, 50)
    
    assert result is None

