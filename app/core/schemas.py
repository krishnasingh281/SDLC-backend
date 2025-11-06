from pydantic import BaseModel
from typing import List, Literal, Optional, Dict

class TradeoffRow(BaseModel):
    criterion: str
    option_a: str
    option_b: str
    verdict: Literal["A","B","Tie","Insufficient Data"]
    notes: str = ""

class TradeoffRequest(BaseModel):
    option_a: str
    option_b: str
    criteria: List[str]
    constraints: List[str] = []
    context: Optional[str] = None

class TradeoffResponse(BaseModel):
    version: str = "1.0"
    generated_at: str
    trace_id: str
    context: Dict[str, str]
    criteria: List[str]
    matrix: List[TradeoffRow]
    summary: str
    recommendation: Dict[str, str]

class ReviewRequest(BaseModel):
    document: str
    quality_goals: List[str]
    checklists: List[str] = []

class RiskItem(BaseModel):
    area: str
    severity: Literal["Low","Medium","High","Critical"]
    likelihood: Literal["Low","Medium","High"]
    impact: str
    mitigation: str

class ReviewResponse(BaseModel):
    version: str = "1.0"
    summary: str
    risks: List[RiskItem]
    action_items: List[str]
    trace_id: str
    generated_at: str
