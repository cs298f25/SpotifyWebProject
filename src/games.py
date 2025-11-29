import random

MAX_GUESSES = 7

POSSIBLE_ANSWERS = [
    "Drake",
    "Taylor Swift",
    "Harry Styles",
    "Pitbull",
    "Adele",
    "Kendrick Lamar",
    "Bad Bunny",
    "Post Malone",
    "Lana Del Rey",
    "The Weeknd",
]


class Games:
    def __init__(self, database):
        self.database = database

    def exists(self, game_id):
        return self.database.exists(game_id)

    def new_game(self, game_id, answer_json):
        self.database.create_game(game_id, answer_json)

    #COMPARISON HELPERS

    def _compare_exact(self, answer_value, guess_value):
        if answer_value is None or guess_value is None:
            return "unknown"

        return (
            "match"
            if str(answer_value).lower() == str(guess_value).lower()
            else "no_match"
        )

    def _compare_numeric(self, answer_value, guess_value):
        if answer_value is None or guess_value is None:
            return "unknown"

        try:
            a = int(answer_value)
            g = int(guess_value)
        except (ValueError, TypeError):
            return "unknown"

        if g == a:
            return "match"
        return "higher" if g > a else "lower"

    # ---------- MAIN GUESS LOGIC ----------

    def guess(self, game_id, guess_json):
        answer_json = self.database.get_answer(game_id)
        if answer_json is None:
            return None

        comparison = {
            "is_correct": (
                str(guess_json.get("name", "")).lower()
                == str(answer_json.get("name", "")).lower()
            ),
            "fields": {
                "gender": self._compare_exact(
                    answer_json.get("gender"), guess_json.get("gender")
                ),
                "genre": self._compare_exact(
                    answer_json.get("tag"), guess_json.get("tag")
                ),
                "area": self._compare_exact(
                    (answer_json.get("area") or {}).get("name"),
                    (guess_json.get("area") or {}).get("name"),
                ),
                "popularity": self._compare_numeric(
                    answer_json.get("spotify popularity"),
                    guess_json.get("spotify popularity"),
                ),
            },
            "answer_snapshot": {
                "name": answer_json.get("name"),
                "gender": answer_json.get("gender"),
                "area": (answer_json.get("area") or {}).get("name"),
                "genre": answer_json.get("tag"),
                "popularity": answer_json.get("spotify popularity"),
            },
            "guess_artist": guess_json,
        }

        # Save this guess
        self.database.add_guess(game_id, comparison)

        # Attach guess_number for UI (1..7)
        guesses = self.database.get_guesses(game_id) or []
        comparison["guess_number"] = len(guesses)

        return comparison

    def higher_lower(self, guess, target):
        if guess < target:
            return "low"
        elif guess > target:
            return "high"
        else:
            return "correct"

    # ---------- GAME LOGIC METHODS ----------

    def select_random_artist(self):
        """Select a random artist from the possible answers list."""
        return random.choice(POSSIBLE_ANSWERS)

    def determine_game_status(self, comparison):
        """
        Determine the game status based on the comparison result.
        Returns: "WON", "LOST", or "ONGOING"
        """
        guess_number = comparison.get("guess_number", 0)
        is_correct = comparison.get("is_correct", False)

        if is_correct:
            return "WON"
        elif guess_number >= MAX_GUESSES:
            return "LOST"
        else:
            return "ONGOING"

    def build_guess_response(self, comparison):
        """
        Build the response payload for a guess.
        Returns a dictionary with status, comparison data, and answer (if game ended).
        """
        status = self.determine_game_status(comparison)
        guess_number = comparison.get("guess_number", 0)
        is_correct = comparison.get("is_correct", False)
        answer_snapshot = comparison.get("answer_snapshot") or {}

        payload = {
            "status": status,  # ONGOING / WON / LOST
            "is_correct": is_correct,
            "comparison": comparison,
            "guess_number": guess_number,
            "max_guesses": MAX_GUESSES,
        }

        if status in ("WON", "LOST"):
            payload["answer"] = {
                "name": answer_snapshot.get("name"),
                "gender": answer_snapshot.get("gender"),
                "genre": answer_snapshot.get("genre"),
                "area": answer_snapshot.get("area"),
                "popularity": answer_snapshot.get("popularity"),
            }

        return payload
