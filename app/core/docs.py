from spectree import SpecTree
from pydantic import BaseModel
from pydantic.v1 import BaseModel as PydanticV1BaseModel # Use Pydantic V1 reference

# Check environment variable to decide whether to enable docs/validation
USE_DOCS = True 

# Initialize SpecTree with minimal required parameters.
# The `version` parameter is recognized by Spectree's internal Configuration model.
# By passing only the minimum, we avoid triggering the strict 'extra fields not permitted' error.
api = SpecTree(
    'flask',
    version='v1.0.0', 
    # Use the PydanticV1 reference to avoid dual-BaseModel conflicts 
    # if the system has Pydantic V2 also installed.
    pydantic_model=BaseModel 
)

# This initialization function is often used in the Flask setup
def init_docs(app):
    if USE_DOCS:
        api.register(app)