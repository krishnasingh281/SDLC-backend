# app/models.py
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db import Base

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True)
    name = Column(String(200), unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class RequestLog(Base):
    __tablename__ = "request_logs"
    id = Column(Integer, primary_key=True)
    route = Column(String(512), nullable=False)
    method = Column(String(16), nullable=False)
    headers_json = Column(Text, nullable=False, default="{}")
    body_json = Column(Text, nullable=False, default="")
    trace_id = Column(String(64), index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    project = relationship("Project", backref="requests")

class ResponseLog(Base):
    __tablename__ = "response_logs"
    id = Column(Integer, primary_key=True)
    status_code = Column(Integer, nullable=False)
    body_json = Column(Text, nullable=False, default="")
    latency_ms = Column(Integer, nullable=False, default=0)
    trace_id = Column(String(64), index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    request_id = Column(Integer, ForeignKey("request_logs.id"), nullable=True)
    request = relationship("RequestLog", backref="responses")

class ErrorLog(Base):
    __tablename__ = "error_logs"
    id = Column(Integer, primary_key=True)
    trace_id = Column(String(64), index=True, nullable=True)
    where = Column(String(256), nullable=True)
    message = Column(Text, nullable=False)
    stack = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
