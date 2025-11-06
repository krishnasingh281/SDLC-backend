import os
from flask import Blueprint, request, jsonify
from app.core.schemas import ReviewRequest
from app.core.llm import run_review

bp = Blueprint("review", __name__)

USE_DOCS = os.getenv("ENABLE_DOCS", "0") == "1"
if USE_DOCS:
    from app.core.docs import api as docs

@bp.post("/")
def handle_review():
    body = ReviewRequest.model_validate_json(request.data)
    resp = run_review(body)
    return jsonify(resp.model_dump()), 200

if USE_DOCS:
    handle_review = docs.validate(
        json=ReviewRequest,
        tags=["Review"]
    )(handle_review)
