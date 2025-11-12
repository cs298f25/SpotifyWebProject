import secrets
from flask import Flask, jsonify, session, render_template, request
from pathlib import Path
import os, dotenv, sys, random

from artists import Artists

required_env = ["REDIS_HOST", "REDIS_PORT", "SECRET_KEY"]

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

def create_app(secret_key, artists):
    app = Flask(__name__)
    app.secret_key = secret_key

    @app.route('/')
    def home():
        return render_template('index.html')

    @app.get('/new-game')
    def new_game():
        number = random.randint(1,10000)
        artists.create_game(get_game_key(), number)
        return jsonify({"ok": True})
    
    @app.post('/guess')
    def submit_guess():
        data = request.json
        guess = int(data["guess"])

        target = artists.get_answer(get_game_key())
        if target is None:
            return jsonify({"ok": False, "error": "Invalid session"}), 400
        
        target = int(target)

        if guess < target:
            return jsonify({"result": "too low"})
        elif guess > target:
            return jsonify({"result": "too high"})
        else:
            return jsonify({"result": "correct!"})

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

    artist_service = Artists(os.getenv('REDIS_HOST'),int(os.getenv('REDIS_PORT')))
    return create_app(os.getenv('SECRET_KEY'),artist_service)

if __name__ == '__main__':
    app = launch()
    app.run(host='0.0.0.0', port=80, debug=True)
