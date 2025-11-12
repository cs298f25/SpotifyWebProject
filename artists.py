import redis

class Artists():
    def __init__(self, host, port) -> None:
        self.storage = redis.Redis(
            host=host,
            port=port,
            decode_responses=True, # decode the byte responses from redis to python strings
        )

    def create_game(self, game_key, answer):
        self.storage.set(game_key, answer)

    def get_answer(self, game_key):
        return self.storage.get(game_key)
    
