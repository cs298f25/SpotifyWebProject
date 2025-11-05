from flask import Flask

def create_app():
    app = Flask(__name__)

    @app.route('/')
    def home():
        return "Hello, world!"

    return app

def launch():
    return create_app()

if __name__ == '__main__':
    app = launch()
    app.run(host='0.0.0.0', port=80, debug=True)