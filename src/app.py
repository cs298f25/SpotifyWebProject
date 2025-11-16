import secrets
from flask import Flask, jsonify, session, render_template, request
from pathlib import Path
import os
import dotenv
import sys
import random

# Add project root and src to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
template_dir = str(project_root / "templates")
static_dir = str(project_root / "static")

from database.database import Database
from games import Games
from spotify import spotify_bp


required_env = [
    "REDIS_HOST",
    "REDIS_PORT",
    "SECRET_KEY",
    "SPOTIFY_CLIENT_ID",
    "SPOTIFY_CLIENT_SECRET",
]

INVALID_GAME_ERROR = { "error": "ERROR", "message": "Game session invalid" }
NO_RESULT_ERROR = {"error": "ERROR", "message": "No result returned"}

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

def create_app(secret_key, games_service):
    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    app.secret_key = secret_key
    app.register_blueprint(spotify_bp)

    @app.route('/')
    def home():
        return render_template('index.html')

    @app.get('/new-game')
    def new_game():
        game_id = get_game_key()
        answer = random.randint(1, 100)
        games_service.new_game(game_id, answer)
        return jsonify({"ok": True})
    
    @app.post('/guess')
    def submit_guess():
        game_id = get_game_key()
        if not games_service.exists(game_id):
            return jsonify(INVALID_GAME_ERROR), 400
        
        data = request.json
        guess = data["guess"]

        try:
            guess = int(guess)
        except ValueError:
            return jsonify({"error": "ERROR", "message": "Guess must be a valid integer"}), 400
        
        result = games_service.guess(game_id, guess)
        if result is None:
            return jsonify(NO_RESULT_ERROR), 400

        return jsonify({"result": result}), 200
    return app

def check_required_env():
    for variable in required_env:
        get = os.environ.get(variable)
        if not get:
            print(f"ERROR: {variable} environment variable must be set", file=sys.stderr)
            sys.exit(1)

def launch():
    dotenv.load_dotenv()
    os.environ["SECRET_KEY"] = ensure_secret_key()
    check_required_env()

    database = Database(os.getenv('REDIS_HOST'), int(os.getenv('REDIS_PORT')))

    games_service = Games(database)
    return create_app(os.getenv('SECRET_KEY'), games_service)

if __name__ == '__main__':
    app = launch()
    app.run(host='0.0.0.0', port=80, debug=True)
