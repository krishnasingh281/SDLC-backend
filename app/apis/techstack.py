from flask import Blueprint, jsonify, request
# CRITICAL FIX 1: Must import Response from spectree
from spectree import Response 
from app.core.schemas import TechStackRequest, TechStackResponse
from app.core.llm import run_techstack
from app.core.docs import api as docs, USE_DOCS

# Define the Blueprint with a URL prefix for organization
bp = Blueprint("techstack", __name__, url_prefix="/techstack")

@bp.post("/")
def handle_techstack():
    """
    Handles the request for PS-05: Design Performance & Tech Stack Recommendation.
    """
    # Use validated data placed in request.context by spectree, or fall back to manual validation
    if USE_DOCS and hasattr(request, 'context') and request.context.json:
        # Data has been validated by spectree's decorator
        validated_body = request.context.json
    else:
        # Manual validation if spectree decorator is skipped (e.g., if USE_DOCS is False)
        try:
            validated_body = TechStackRequest.model_validate_json(request.data)
        except Exception as e:
            return jsonify({"msg": f"Invalid request body format: {e}"}), 400
            
    # Call the core LLM function
    resp = run_techstack(validated_body)
    
    # Use model_dump() to convert the Pydantic model back to a Python dict for JSON response
    return jsonify(resp.model_dump()), 200


if USE_DOCS:
    # CRITICAL FIX 2: Correctly wrap the response model using Response(HTTP_200=...)
    # This syntax is required by spectree to define the response schema for documentation.
    handle_techstack = docs.validate(
        json=TechStackRequest,
        resp=Response(HTTP_200=TechStackResponse), # THIS IS THE CRITICAL LINE
        tags=["techstack", "architecture"]
    )(handle_techstack)