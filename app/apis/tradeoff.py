# app/apis/tradeoff.py
import os
from flask import Blueprint, request, jsonify
from app.core.schemas import TradeoffRequest
from app.core.llm import run_tradeoff

bp = Blueprint("tradeoff", __name__)

# Only import Spectree if explicitly enabled
USE_DOCS = os.getenv("ENABLE_DOCS", "0") == "1"
if USE_DOCS:
    from app.core.docs import api as docs  # <- imported only when enabled

@bp.post("/")
def handle_tradeoff():
    body = TradeoffRequest.model_validate_json(request.data)
    resp = run_tradeoff(body)
    return jsonify(resp.model_dump()), 200

# If docs are enabled, apply the Spectree decorator dynamically
if USE_DOCS:
    handle_tradeoff = docs.validate(
        json=TradeoffRequest,
        # avoid Response(...) to keep it simple/compatible
        tags=["Tradeoff"]
    )(handle_tradeoff)
