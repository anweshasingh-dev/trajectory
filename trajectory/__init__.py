"""Application factory for the local Trajectory workspace."""
from pathlib import Path
import secrets
from flask import Flask
from . import storage


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=secrets.token_hex(32),
        DATABASE=str(Path(app.instance_path) / "trajectory.sqlite"),
        OLLAMA_MODEL="qwen3:4b",
        INFERENCE_TIMEOUT=120,
        MAX_CONTENT_LENGTH=64 * 1024,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        TRUSTED_HOSTS=["localhost", "127.0.0.1"],
    )
    if test_config:
        app.config.update(test_config)
    Path(app.config["DATABASE"]).parent.mkdir(parents=True, exist_ok=True)
    app.teardown_appcontext(storage.close_db)
    with app.app_context():
        storage.initialize()
    from .routes import bp
    app.register_blueprint(bp)
    return app
