import secrets
from flask import Flask, jsonify, session, render_template, request
from pathlib import Path
import os
import dotenv
import sys
import random

#PATH SETUP
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))
template_dir = str(project_root / "templates")
static_dir = str(project_root / "static")

from database.database import Database
from games import Games
from musicbrain import musicbrain_bp, get_artist_data_for_game

#CONSTANTS
required_env = [
    "REDIS_HOST",
    "REDIS_PORT",
    "SECRET_KEY",
    "SPOTIFY_CLIENT_ID",
    "SPOTIFY_CLIENT_SECRET",
]

MAX_GUESSES = 7

INVALID_GAME_ERROR = {"error": "ERROR", "message": "Game session invalid"}
NO_RESULT_ERROR = {"error": "ERROR", "message": "No result returned"}


#SECRET KEY
def ensure_secret_key():
    key = os.getenv("SECRET_KEY")
    if key:
        return key

    key = secrets.token_hex(32)
    env_path = project_root / ".env"
    if not env_path.exists():
        env_path.write_text(f"\nSECRET_KEY={key}\n")
    else:
        with env_path.open("a") as f:
            f.write(f"\nSECRET_KEY={key}\n")

    return key


def _ensure_session_id():
    if "sid" not in session:
        session["sid"] = secrets.token_hex(16)
    return session["sid"]


def get_game_key():
    return f"game:{_ensure_session_id()}"


#APP FACTORY
def create_app(secret_key, games_service):
    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    app.secret_key = secret_key
    app.register_blueprint(musicbrain_bp, url_prefix="/musicbrain")

    @app.route("/")
    def home():
        return render_template("index.html")

    @app.get("/new-game")
    def new_game():
        """Start a new game with a random curated artist."""
        game_id = get_game_key()

        possible_answers = [
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

        artist_name = random.choice(possible_answers)

        try:
            answer_data = get_artist_data_for_game(artist_name)
        except Exception as e:
            print(f"Error fetching artist for new game: {e}", file=sys.stderr)
            return (
                jsonify(
                    {
                        "error": "ERROR",
                        "message": "Could not start a new game (artist lookup failed)",
                    }
                ),
                500,
            )

        games_service.new_game(game_id, answer_data)

        return jsonify({"ok": True})

    @app.post("/guess")
    def submit_guess():
        game_id = get_game_key()

        if not games_service.exists(game_id):
            return jsonify(INVALID_GAME_ERROR), 400

        data = request.json or {}
        guess_text = str(data.get("guess", "")).strip()

        if not guess_text:
            return (
                jsonify(
                    {
                        "error": "ERROR",
                        "message": "Guess must be a non-empty artist name",
                    }
                ),
                400,
            )

        try:
            guess_json = get_artist_data_for_game(guess_text)
        except Exception as e:
            print(f"Error looking up guess artist '{guess_text}': {e}", file=sys.stderr)
            return (
                jsonify(
                    {
                        "error": "ERROR",
                        "message": "Could not find that artist",
                    }
                ),
                500,
            )

        comparison = games_service.guess(game_id, guess_json)
        if comparison is None:
            return jsonify(NO_RESULT_ERROR), 400

        guess_number = comparison.get("guess_number", 0)
        is_correct = comparison.get("is_correct", False)

        status = "ONGOING"
        if is_correct:
            status = "WON"
        elif guess_number >= MAX_GUESSES:
            status = "LOST"

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
                "genre": answer_snapshot.get("genre"),
                "area": answer_snapshot.get("area"),
                "popularity": answer_snapshot.get("popularity"),
            }

        return jsonify(payload), 200

    return app


#ENV + LAUNCH
def check_required_env():
    for variable in required_env:
        value = os.environ.get(variable)
        if not value:
            print(f"ERROR: {variable} environment variable must be set", file=sys.stderr)
            sys.exit(1)


def launch():
    dotenv.load_dotenv(dotenv_path=project_root / ".env")
    os.environ["SECRET_KEY"] = ensure_secret_key()
    check_required_env()

    database = Database(os.getenv("REDIS_HOST"), int(os.getenv("REDIS_PORT")))
    games_service = Games(database)
    return create_app(os.getenv("SECRET_KEY"), games_service)


if __name__ == "__main__":
    app = launch()

    app.run(host="0.0.0.0", port=80, debug=True)
