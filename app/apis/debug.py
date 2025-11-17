from flask import Blueprint, jsonify, request
from spectree import Response
from app.core.schemas import DebugRequest, DebugResponse
from app.core.llm import run_debug_assistant
from app.core.docs import api as docs, USE_DOCS

# Define the Blueprint with a URL prefix
bp = Blueprint("debug", __name__, url_prefix="/debug")

@bp.post("/")
def handle_debug_request():
    """
    Handles the request for PS-09: Debugging and Optimization Assistant.
    """
    # Use validated data placed in request.context by spectree, or fall back to manual validation
    if USE_DOCS and hasattr(request, 'context') and request.context.json:
        validated_body = request.context.json
    else:
        try:
            validated_body = DebugRequest.model_validate_json(request.data)
        except Exception as e:
            return jsonify({"msg": f"Invalid request body format: {e}"}), 400
            
    # Call the core LLM function
    resp = run_debug_assistant(validated_body)
    
    # Return the dumped JSON and HTTP 200 OK status
    return jsonify(resp.model_dump()), 200


if USE_DOCS:
    # Use the correct Spectree Response wrapping pattern
    handle_debug_request = docs.validate(
        json=DebugRequest,
        resp=Response(HTTP_200=DebugResponse),
        tags=["debugging", "coding"]
    )(handle_debug_request)