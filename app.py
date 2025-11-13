import secrets
from flask import Flask, jsonify, session, render_template, request
from pathlib import Path
import os, dotenv, sys, random

from database import Database
from games import Games
from spotify import spotify_bp

required_env = [
    "REDIS_HOST",
    "REDIS_PORT",
    "SECRET_KEY",
    "SPOTIFY_CLIENT_ID",
    "SPOTIFY_CLIENT_SECRET",
]

def ensure_secret_key():
    key = os.getenv("SECRET_KEY")
    if key:
        return key
    
    key = secrets.token_hex(32)
    env_path = Path(".env")
    if not env_path.exists():
        env_path.write_text(f"SECRET_KEY={key}\n")
    else:
        with env_path.open("a") as f:
            f.write(f"SECRET_KEY={key}\n")
    
    return key

def _ensure_session_id():
    if "sid" not in session:
        session["sid"] = secrets.token_hex(16)
    
    return session["sid"]

def get_game_key():
    return f"game:{_ensure_session_id()}"

def create_app(secret_key, games_service):
    app = Flask(__name__)
    app.secret_key = secret_key
    app.register_blueprint(spotify_bp)

    @app.route('/')
    def home():
        return render_template('index.html')

    @app.get('/new-game')
    def new_game():
        print("NEW GAMEEEE")
        game_id = get_game_key()
        answer = random.randint(1,100)
        games_service.new_game(game_id, answer)
        print(answer)
        return jsonify({"ok": True})
    
    @app.post('/guess')
    def submit_guess():
        game_id = get_game_key()
        game = games_service.get_game(game_id)
        if not game:
            return jsonify({"ok": False, "error": "Invalid session"})
        
        data = request.json
        guess = int(data["guess"])
        
        result = game.guess(guess)
        return jsonify({"ok": True, "result": result})
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

    database = Database(os.getenv('REDIS_HOST'),int(os.getenv('REDIS_PORT')))

    games_service = Games(database)
    return create_app(os.getenv('SECRET_KEY'), games_service)

if __name__ == '__main__':
    app = launch()
    app.run(host='0.0.0.0', port=80, debug=True)
