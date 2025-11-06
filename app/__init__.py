# app/__init__.py
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from .core.docs import api as docs

def create_app():
    load_dotenv()
    app = Flask(__name__)
    CORS(app)

    API_KEY = os.getenv("API_KEY", "")

    @app.before_request
    def _auth():
        if request.path.startswith("/api/"):
            if request.headers.get("X-API-Key") != API_KEY:
                return jsonify({"error":{"code":"UNAUTHORIZED","message":"Missing/invalid API key"}}), 401

    @app.get("/health")
    def health():
        return {"status": "ok"}

    # 👇 vanilla registration
    from .apis.tradeoff import bp as tradeoff_bp
    from .apis.review import bp as review_bp
    app.register_blueprint(tradeoff_bp, url_prefix="/api/v1/tradeoff")
    app.register_blueprint(review_bp,   url_prefix="/api/v1/review")

    docs.register(app)  

    return app
