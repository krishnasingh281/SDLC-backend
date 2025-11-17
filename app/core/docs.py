from spectree import SpecTree
from pydantic import BaseModel # Keep the import, but don't pass it to SpecTree

# Check environment variable to decide whether to enable docs/validation
USE_DOCS = True 

# Initialize SpecTree with ONLY the version and the framework type.
# We are removing 'pydantic_model' to avoid the validation error.
api = SpecTree(
    'flask',
    version='v1.0.0', 
    # Removed the following lines to bypass the validation error:
    # model_title='SDLC Assistant API', 
    # model_description='AI-powered tools for Design, Risk, and Development tasks.',
    # pydantic_model=BaseModel 
)

# This initialization function is often used in the Flask setup
def init_docs(app):
    if USE_DOCS:
        api.register(app)