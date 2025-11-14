import redis
import json
from .base_database import BaseDatabase

class Database(BaseDatabase):
    """Redis-based database implementation."""
    
    def __init__(self, host, port) -> None:
        self.storage = redis.Redis(
            host=host,
            port=port,
            decode_responses=True,
        )

    def _get_game(self, game_id):
        game_data = self.storage.get(game_id)
        if game_data is not None:
            return json.loads(game_data)  # json -> python object
        return None

    def _set_game(self, game_id, game_dict):
        self.storage.set(game_id, json.dumps(game_dict))

    def exists(self, game_id):
        return self.storage.exists(game_id)
    
