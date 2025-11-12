
class Game():
    def __init__(self, answer):
        self.answer = answer

    def guess(self, guess):
        return self.higher_lower(int(guess), self.answer)

    def higher_lower(self, guess, target):
        if guess < target:
            return "low"
        elif guess > target:
            return "high"
        else:
            return "correct"