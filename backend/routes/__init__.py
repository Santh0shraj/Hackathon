# Routes package: register blueprints from workflows, runs.

from flask import Flask

from .runs import runs_bp
from .workflows import workflows_bp


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(workflows_bp, url_prefix="/workflows")
    app.register_blueprint(runs_bp, url_prefix="/workflow-runs")
