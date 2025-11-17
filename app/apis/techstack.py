from flask import Blueprint, request, jsonify
from app.core.schemas import TechStackRequest, TechStackResponse
from app.core.llm import run_techstack
from app.core.docs import api as docs, USE_DOCS

bp = Blueprint("techstack", __name__)

@bp.post("/")
def handle_techstack():
    body = TechStackRequest.model_validate_json(request.data)
    resp = run_techstack(body)
    return jsonify(resp.model_dump()), 200


if USE_DOCS:
    handle_techstack = docs.validate(
        json=TechStackRequest,
        resp=TechStackResponse,
        tags=["techstack", "architecture"]
    )(handle_techstack)
