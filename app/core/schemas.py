# app/core/schemas.py
from pydantic import BaseModel
from typing import List, Literal, Optional, Dict

# ===== Tradeoff =====
class TradeoffRow(BaseModel):
    criterion: str
    option_a: str
    option_b: str
    verdict: Literal["A", "B", "Tie", "Insufficient Data"]
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

# ===== Review =====
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

# ===== Risk =====
class RiskRow(BaseModel):
    risk_id: str
    category: str
    description: str
    likelihood: int  # 1..3
    impact: int      # 1..4
    score: int       # likelihood * impact
    mitigation: str
    owner: str = "Unassigned"
    due_by: Optional[str] = None

class RiskRequest(BaseModel):
    design: str
    non_functionals: List[str] = []
    constraints: List[str] = []

class RiskResponse(BaseModel):
    version: str = "1.0"
    trace_id: str
    generated_at: str
    summary: str
    risks: List[RiskRow]


# ===== Test Cases =====
from typing import Any

class TestCase(BaseModel):
    id: str
    title: str
    given: str
    when: str
    then: str
    priority: Literal["Low", "Medium", "High"] = "Medium"
    type: Literal["Positive", "Negative", "Edge"] = "Positive"
    data: Dict[str, Any] = {}

class TestCaseRequest(BaseModel):
    # accept either a user story or a function signature
    user_story: Optional[str] = None
    function_signature: Optional[str] = None
    non_functionals: List[str] = []           # e.g., ["Performance","Security"]
    constraints: List[str] = []               # e.g., ["2-week deadline"]
    count: int = 6                             # desired number of cases

class TestCaseResponse(BaseModel):
    version: str = "1.0"
    trace_id: str
    generated_at: str
    summary: str
    cases: List[TestCase]
