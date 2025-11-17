# app/core/docs.py

from spectree import SpecTree
from spectree.plugins.flask_plugin import FlaskPlugin

# Toggle to enable/disable docs decorators
USE_DOCS = True

api = SpecTree(
    backend=FlaskPlugin,          # ⬅️ pass the backend class, NOT "flask"
    mode="strict",                # validate both request & response
    path="/apidocs",              # base path for API docs
    title="Intelligent SDLC Assistant",
    version="1.0.0",
    # NOTE: don't pass ui / UI here; newer Spectree config throws on it
)
