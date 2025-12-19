from flask import Flask
import os


def create_app():
    app = Flask(__name__)

    # Folders for uploads/downloads
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('downloads', exist_ok=True)

    # Import routes
    from app import routes
    app.register_blueprint(routes.bp)

    return app
