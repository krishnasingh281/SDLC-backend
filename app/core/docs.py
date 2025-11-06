# app/core/docs.py
from spectree import SpecTree

# pass backend as positional arg, and use lowercase kw names
api = SpecTree(
    "flask",
    title="Intelligent SDLC Assistant",
    version="0.1.0",
    path="/apidocs",     # UI will be at /apidocs
    mode="strict",       # request/response validation
    ui="swagger"         # swagger | redoc | rapidoc
)
