from flask import Flask, render_template
import os
import redis
import dotenv


dotenv.load_dotenv()

r = redis.Redis(
    host=os.getenv('REDIS_HOST') or 'localhost',
    port=int(os.getenv('REDIS_PORT') or 6379),
    decode_responses=True, # decode the byte responses from redis to python strings
)

def create_app():
    app = Flask(__name__)

    r.set('latest_message', 'Hello, world! from the redis database')

    @app.route('/')
    def home():
        value = r.get('latest_message')
        return render_template('index.html', value=value)

    return app

def launch():
    return create_app()

if __name__ == '__main__':

    # Error handling if the .env file does not have the redis host and port
    # might have to change this for better error handling
    if os.getenv('REDIS_HOST') is None:
        print('REDIS_HOST is not set')
        exit(1)

    if os.getenv('REDIS_PORT') is None:
        print('REDIS_PORT is not set')
        exit(1)

    app = launch()
    app.run(host='0.0.0.0', port=80, debug=True)