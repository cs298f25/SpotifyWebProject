from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello, world!"

# Runs on 0.0.0.0 so that it can be accessed from the internet
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)