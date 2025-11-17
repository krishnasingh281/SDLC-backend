from spectree import SpecTree
from pydantic import BaseModel # CRITICAL: BaseModel is still needed for the next step

# Check environment variable to decide whether to enable docs/validation
USE_DOCS = True # Keep this as is

# Initialize SpecTree
api = SpecTree(
    'flask',
    # --- CRITICAL FIX: Rename arguments to lowercase (snake_case) ---
    model_title='SDLC Assistant API', 
    model_description='AI-powered tools for Design, Risk, and Development tasks.',
    version='v1.0.0',
    # The BaseModel fix from before, renamed to pydantic_model
    pydantic_model=BaseModel 
    # -------------------------------------------------------------------
)

# This initialization function is often used in the Flask setup
def init_docs(app):
    if USE_DOCS:
        api.register(app)