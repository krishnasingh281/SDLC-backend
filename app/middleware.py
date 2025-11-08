# app/middleware.py
import json
import time
import uuid
import traceback
from flask import request, g
from app.db import SessionLocal
from app.models import RequestLog, ResponseLog, ErrorLog

def register_request_response_logging(app):
    @app.before_request
    def _start_request_logging():
        g._t0 = time.perf_counter()
        g._db = SessionLocal()

        # honor incoming trace or generate one
        g.trace_id = request.headers.get("X-Trace-Id") or str(uuid.uuid4())

        try:
            headers = {k: v for k, v in request.headers.items()}
            body = request.get_data(as_text=True) or ""
            req_row = RequestLog(
                route=request.path,
                method=request.method,
                headers_json=json.dumps(headers),
                body_json=body,
                trace_id=g.trace_id,
            )
            g._db.add(req_row)
            g._db.flush()  # get req_row.id
            g._request_row_id = req_row.id
        except Exception:
            # do not break the request if logging fails
            g._request_row_id = None

    @app.after_request
    def _finish_request_logging(response):
        try:
            latency_ms = int((time.perf_counter() - g._t0) * 1000)
            body = response.get_data(as_text=True) or ""
            resp_row = ResponseLog(
                status_code=response.status_code,
                body_json=body,
                latency_ms=latency_ms,
                trace_id=g.trace_id,
                request_id=g.get("_request_row_id"),
            )
            g._db.add(resp_row)
            g._db.commit()
        except Exception:
            g._db.rollback()
        finally:
            try:
                g._db.close()
            finally:
                SessionLocal.remove()

        # propagate trace to client
        response.headers["X-Trace-Id"] = g.trace_id
        return response

    @app.teardown_request
    def _teardown_request(exc):
        if exc is not None:
            try:
                db = getattr(g, "_db", None) or SessionLocal()
                err = ErrorLog(
                    trace_id=getattr(g, "trace_id", None),
                    where=request.endpoint or request.path,
                    message=str(exc),
                    stack=traceback.format_exc(),
                )
                db.add(err)
                db.commit()
            except Exception:
                pass
            finally:
                try:
                    db.close()
                finally:
                    SessionLocal.remove()
