
from flask import Flask
from config import Config
from database import init_db
from routes import register_blueprints

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    CORS(app)
    init_db(app)

    @app.route("/health")
    def health():
        return {"status": "ok"}

    return app

# 👇 THIS LINE IS THE KEY
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)