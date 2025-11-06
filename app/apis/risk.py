# app/apis/risk.py
from flask import Blueprint, request, jsonify
from app.core.schemas import RiskRequest
from app.core.llm import run_risk

bp = Blueprint("risk", __name__)

@bp.post("/")
def handle_risk():
    body = RiskRequest.model_validate_json(request.data)
    resp = run_risk(body)
    return jsonify(resp.model_dump()), 200
