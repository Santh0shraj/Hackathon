# Flask app entry point: creates app, loads config, registers blueprints, runs server.

from dotenv import load_dotenv
load_dotenv()

from flask import Flask

from database import engine
from models import Base
from routes import register_blueprints

app = Flask(__name__)
register_blueprints(app)


def init_db():
    """Create tables if they don't exist."""
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)
