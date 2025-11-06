import os
from flask import Blueprint, request, jsonify
from app.core.schemas import TestCaseRequest
from app.core.llm import run_testcases

bp = Blueprint("testcases", __name__)

USE_DOCS = os.getenv("ENABLE_DOCS", "0") == "1"
if USE_DOCS:
    from app.core.docs import api as docs

@bp.post("/")
def handle_testcases():
    body = TestCaseRequest.model_validate_json(request.data)
    resp = run_testcases(body)
    return jsonify(resp.model_dump()), 200

if USE_DOCS:
    handle_testcases = docs.validate(
        json=TestCaseRequest,
        tags=["TestCases"]
    )(handle_testcases)
