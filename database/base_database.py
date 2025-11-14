from abc import ABC, abstractmethod

class BaseDatabase(ABC):
    
    # Methods that have different implementations
    @abstractmethod
    def _get_game(self, game_id):
        pass
    
    @abstractmethod
    def _set_game(self, game_id, game_dict):
        pass
    
    @abstractmethod
    def exists(self, game_id):
        pass
    
    # Methods that have the same implementation
    def create_game(self, game_id, answer):
        game_dict = {
            "answer": answer,
            "guesses": []
        }
        self._set_game(game_id, game_dict)

    def get_answer(self, game_id):
        game_dict = self._get_game(game_id)
        if game_dict is not None:
            return game_dict.get("answer")
        return None

    def add_guess(self, game_id, guess):
        game_dict = self._get_game(game_id)
        if game_dict is not None:
            game_dict["guesses"].append(guess)
            self._set_game(game_id, game_dict)
            return True
        return False

    def get_guesses(self, game_id):
        game_dict = self._get_game(game_id)
        if game_dict is not None:
            return game_dict.get("guesses", [])
        return None