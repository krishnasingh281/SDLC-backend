# app/__init__.py
import os
from flask import Flask
from dotenv import load_dotenv

def create_app():
    load_dotenv()  # reads .env
    app = Flask(__name__)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app
