# app/apis/design.py
import os
from flask import Blueprint, request, jsonify
from app.core.schemas import DesignSuggestRequest
from app.core.llm import run_design_suggest

bp = Blueprint("design", __name__)

@bp.post("/")
def handle_design_suggest():
    body = DesignSuggestRequest.model_validate_json(request.data)
    resp = run_design_suggest(body)
    return jsonify(resp.model_dump()), 200

# Hook docs only if enabled AND only import here
if os.getenv("ENABLE_DOCS", "0") == "1":
    from app.core.docs import api as docs
    handle_design_suggest = docs.validate(
        json=DesignSuggestRequest,
        resp=200,
        tags=["PS-04 Suggest Design"],
        deprecated=False,
        after=handle_design_suggest,
    )
