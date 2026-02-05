
from contextlib import contextmanager
from flask_sqlalchemy import SQLAlchemy

# Initialize Flask-SQLAlchemy
db = SQLAlchemy()

def init_db(app):
    """Initialize the database with the Flask app."""
    db.init_app(app)
    
    # Create tables within app context
    with app.app_context():
        # Import models here to ensure they are registered with SQLAlchemy
        import models
        db.create_all()

@contextmanager
def get_session():
    """
    Compatibility shim for existing code that expects a session context manager.
    Wraps db.session with commit/rollback logic.
    """
    try:
        yield db.session
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
    # Note: Flask-SQLAlchemy handles session removal automatically at end of request
