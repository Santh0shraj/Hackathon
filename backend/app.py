# Flask app entry point: creates app, loads config, registers blueprints, runs server.

from flask import Flask

from routes import register_blueprints

app = Flask(__name__)
register_blueprints(app)


if __name__ == "__main__":
    app.run(debug=True)
