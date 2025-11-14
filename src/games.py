class Games():

    def __init__(self, database):
        self.database = database
    
    def exists(self, game_id):
        return self.database.exists(game_id)
    
    def new_game(self, game_id, answer):
        self.database.create_game(game_id, answer)

    def guess(self, game_id, guess):
        answer = self.database.get_answer(game_id)
        if answer is None:
            return None
        result = self.higher_lower(guess, answer)
        
        self.database.add_guess(game_id, guess)
        return result

    def higher_lower(self, guess, target):
        if guess < target:
            return "low"
        elif guess > target:
            return "high"
        else:
            return "correct"

