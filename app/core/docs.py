from spectree import SpecTree
from pydantic import BaseModel # CRITICAL: Import BaseModel here

# Check environment variable to decide whether to enable docs/validation
USE_DOCS = True # Set to False if you don't want validation/docs

# Initialize SpecTree, passing the BaseModel reference explicitly
# This prevents the conflict when spectree tries to load its own reference.
api = SpecTree(
    'flask',
    MODEL_TITLE='SDLC Assistant API',
    MODEL_DESCRIPTION='AI-powered tools for Design, Risk, and Development tasks.',
    version='v1.0.0',
    # CRITICAL FIX: Pass Pydantic's BaseModel reference directly
    PydanticModel=BaseModel 
)

# This initialization function is often used in the Flask setup
def init_docs(app):
    if USE_DOCS:
        api.register(app)