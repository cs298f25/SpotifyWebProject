from database import Database
from game import Game

class Games():

    def __init__(self, database):
        self.database = database
        self.games = {}
    
    def new_game(self, game_id, answer):
        self.games[game_id] = Game(answer)
    
    def get_game(self, game_id):
        return self.games[game_id]

