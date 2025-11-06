from flask import Blueprint, jsonify
from spectree import Response
from app.core.docs import api as docs
from app.core.schemas import TradeoffRequest, TradeoffResponse
from app.core.llm import run_tradeoff

bp = Blueprint("tradeoff", __name__)

@bp.post("/")
@docs.validate(
    json=TradeoffRequest,
    resp=Response(HTTP_200=TradeoffResponse),
    tags=["Tradeoff"]
)
def handle_tradeoff(json: TradeoffRequest):
    resp = run_tradeoff(json)
    return jsonify(resp.model_dump()), 200
