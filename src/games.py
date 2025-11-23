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
