
from flask import Flask
from config import Config
from database import init_db
from routes import register_blueprints

def create_app():
    """Application Factory Pattern"""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions and database
    init_db(app)

    # Register blueprints
    register_blueprints(app)
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
