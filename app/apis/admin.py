# app/apis/admin.py
from flask import Blueprint, jsonify
from app.db import SessionLocal
from app.models import RequestLog, ResponseLog, ErrorLog

bp = Blueprint("admin", __name__)

@bp.get("/trace/<trace_id>")
def get_trace(trace_id: str):
    db = SessionLocal()
    try:
        reqs = db.query(RequestLog).filter(RequestLog.trace_id == trace_id).all()
        resps = db.query(ResponseLog).filter(ResponseLog.trace_id == trace_id).all()
        errs = db.query(ErrorLog).filter(ErrorLog.trace_id == trace_id).all()
        return jsonify({
            "requests": [ _row(r) for r in reqs ],
            "responses": [ _row(r) for r in resps ],
            "errors": [ _row(e) for e in errs ],
        })
    finally:
        db.close()

def _row(obj):
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}
