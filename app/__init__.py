# app/__init__.py
import os
from flask import Flask, request, jsonify, g
from flask_cors import CORS
from dotenv import load_dotenv


def create_app():
    # Load .env early
    load_dotenv()

    app = Flask(__name__)
    # CORS: allow everything by default; tighten via CORS_ORIGINS if you have a frontend origin
    CORS(app, resources={r"/api/*": {"origins": os.getenv("CORS_ORIGINS", "*")}})

    # --- Config ---
    app.config["API_KEY"] = os.getenv("API_KEY", "").strip()
    app.config["TESTING"] = app.config.get("TESTING", False)

    # --- Auth for /api/* (skips when TESTING or no API_KEY set) ---
    @app.before_request
    def _auth():
        if app.config.get("TESTING"):
            return
        if not app.config.get("API_KEY"):
            # Auth disabled if no key configured
            return
        if request.path.startswith("/api/"):
            if request.headers.get("X-API-Key") != app.config["API_KEY"]:
                return jsonify({
                    "error": {"code": "UNAUTHORIZED", "message": "Missing/invalid API key"}
                }), 401

    # --- Health probe ---
    @app.get("/health")
    def health():
        return {"status": "ok"}

    # --- Optional: DB init & request/response logging middleware ---
    if os.getenv("ENABLE_DB", "false").lower() == "true":
        from app.db import init_db
        from app.middleware import register_request_response_logging
        init_db()
        register_request_response_logging(app)

    # Even if DB logging is off, propagate any trace id set by handlers/middleware
    @app.after_request
    def _propagate_trace(resp):
        tid = getattr(g, "trace_id", None)
        if tid:
            resp.headers["X-Trace-Id"] = tid
        return resp

    # --- Blueprints (import inside factory to avoid circulars) ---
    from .apis.tradeoff import bp as tradeoff_bp
    from .apis.review import bp as review_bp
    from .apis.risk import bp as risk_bp
    from .apis.testcases import bp as tc_bp
    from .apis.admin import bp as admin_bp

    app.register_blueprint(tradeoff_bp, url_prefix="/api/v1/tradeoff")
    app.register_blueprint(review_bp,   url_prefix="/api/v1/review")
    app.register_blueprint(risk_bp,     url_prefix="/api/v1/risk")
    app.register_blueprint(tc_bp,       url_prefix="/api/v1/testcases")
    app.register_blueprint(admin_bp,    url_prefix="/api/v1/admin")

    # --- Optional API docs (Spectree) ---
    if os.getenv("ENABLE_DOCS", "0") == "1" and not app.config.get("TESTING"):
        try:
            from .core.docs import api as docs
            docs.register(app)
        except Exception as e:
            app.logger.warning(f"Docs disabled: {e}")

    return app
