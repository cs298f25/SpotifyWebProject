import redis

class Database():
    def __init__(self, host, port) -> None:
        self.storage = redis.Redis(
            host=host,
            port=port,
            decode_responses=True,
        )

    def create_game(self, game_key, answer):
        self.storage.set(game_key, answer)

    def get_answer(self, game_key):
        return self.storage.get(game_key)
    
