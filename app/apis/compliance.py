from flask import Blueprint, jsonify, request
from spectree import Response
from app.core.schemas import ComplianceRequest, ComplianceResponse
from app.core.llm import run_compliance_check
from app.core.docs import api as docs, USE_DOCS

# Define the Blueprint with a URL prefix
bp = Blueprint("compliance", __name__, url_prefix="/compliance")

@bp.post("/")
def handle_compliance_check():
    """
    Handles the request for PS-07: Code Compliance & Standards Check.
    """
    # Use validated data placed in request.context by spectree, or fall back to manual validation
    if USE_DOCS and hasattr(request, 'context') and request.context.json:
        validated_body = request.context.json
    else:
        try:
            validated_body = ComplianceRequest.model_validate_json(request.data)
        except Exception as e:
            return jsonify({"msg": f"Invalid request body format: {e}"}), 400
            
    # Call the core LLM function
    resp = run_compliance_check(validated_body)
    
    # Return the dumped JSON and HTTP 200 OK status
    return jsonify(resp.model_dump()), 200


if USE_DOCS:
    # Use the correct Spectree Response wrapping pattern
    handle_compliance_check = docs.validate(
        json=ComplianceRequest,
        resp=Response(HTTP_200=ComplianceResponse),
        tags=["compliance", "coding"]
    )(handle_compliance_check)

    