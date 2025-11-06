# app/__init__.py
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from .apis.testcases import bp as tc_bp

def create_app():
    load_dotenv()
    app = Flask(__name__)
    CORS(app)

    app.config["API_KEY"] = os.getenv("API_KEY", "")

    @app.before_request
    def _auth():
        if app.config.get("TESTING"):
            return
        if request.path.startswith("/api/"):
            if request.headers.get("X-API-Key") != app.config.get("API_KEY", ""):
                return jsonify({"error":{"code":"UNAUTHORIZED","message":"Missing/invalid API key"}}), 401

    @app.get("/health")
    def health():
        return {"status": "ok"}

    # Blueprints
    from .apis.tradeoff import bp as tradeoff_bp
    from .apis.review import bp as review_bp
    from .apis.risk import bp as risk_bp
    app.register_blueprint(tradeoff_bp, url_prefix="/api/v1/tradeoff")
    app.register_blueprint(review_bp,   url_prefix="/api/v1/review")
    app.register_blueprint(risk_bp,     url_prefix="/api/v1/risk")
    app.register_blueprint(tc_bp,       url_prefix="/api/v1/testcases")

    # 👉 Register docs only when explicitly enabled and not in tests
    if os.getenv("ENABLE_DOCS", "0") == "1" and not app.config.get("TESTING"):
        try:
            from .core.docs import api as docs
            docs.register(app)
        except Exception as e:
            app.logger.warning(f"Docs disabled: {e}")

    return app
