import os
from flask import Blueprint, request, jsonify
from app.core.schemas import RiskRequest
from app.core.llm import run_risk

bp = Blueprint("risk", __name__)

USE_DOCS = os.getenv("ENABLE_DOCS", "0") == "1"
if USE_DOCS:
    from app.core.docs import api as docs

@bp.post("/")
def handle_risk():
    body = RiskRequest.model_validate_json(request.data)
    resp = run_risk(body)
    return jsonify(resp.model_dump()), 200

if USE_DOCS:
    handle_risk = docs.validate(
        json=RiskRequest,
        tags=["Risk"]
    )(handle_risk)
