from flask import Blueprint, jsonify
from spectree import Response
from app.core.docs import api as docs
from app.core.schemas import ReviewRequest, ReviewResponse
from app.core.llm import run_review

bp = Blueprint("review", __name__)

@bp.post("/")
@docs.validate(
    json=ReviewRequest,
    resp=Response(HTTP_200=ReviewResponse),
    tags=["Review"]
)
def handle_review(json: ReviewRequest):
    resp = run_review(json)
    return jsonify(resp.model_dump()), 200
