from .base_database import BaseDatabase

class InMemoryDatabase(BaseDatabase):
    """In-memory database for tests and development"""
    
    def __init__(self, host=None, port=None):
        self.storage = {}
    
    def _get_game(self, game_id):
        return self.storage.get(game_id)
    
    def _set_game(self, game_id, game_dict):
        self.storage[game_id] = game_dict
    
    def exists(self, game_id):
        return game_id in self.storage