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
    risks: List[RiskItem] = []
    action_items: List[str] = []
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

# --- PS-04: Suggest Design ---

from pydantic import BaseModel, Field
from typing import List, Optional

class DesignSuggestRequest(BaseModel):
    problem: str = Field(..., description="Short description of the problem/domain")
    quality_goals: List[str] = Field(default_factory=list, description="e.g., Scalability, Reliability")
    constraints: List[str] = Field(default_factory=list, description="e.g., team of 3, no Kafka, budget cap")
    preferred_stack: Optional[List[str]] = Field(default=None, description="Optional tech preferences")

class DesignOption(BaseModel):
    name: str
    when_to_use: str
    key_components: List[str] = Field(default_factory=list)
    pros: List[str] = Field(default_factory=list)
    cons: List[str] = Field(default_factory=list)
    diagram_mermaid: Optional[str] = Field(
        default=None,
        description="Small mermaid snippet, e.g., graph LR; A-->B"
    )

class DesignSuggestResponse(BaseModel):
    version: str = "1.0"
    trace_id: str
    generated_at: str
    summary: str
    options: List[DesignOption] = Field(default_factory=list)
    recommendation: str = Field(..., description="One-paragraph final pick + why")


# --- PS-05: Design Performance & Tech Stack Recommendation ---

class TechSuggestion(BaseModel):
    category: str  # e.g., "Backend Framework", "Database", "Caching", "Observability"
    options: List[str]  # e.g., ["Django", "FastAPI"]
    reasoning: str      # why these choices

class PerfFinding(BaseModel):
    attribute: str      # e.g., Reliability, Latency, Scalability
    score: int          # 1–10 rating
    issues: List[str]
    suggestions: List[str]

class ReferenceComparison(BaseModel):
    matched: List[str]
    missing: List[str]
    improvements: List[str]

class TechStackRequest(BaseModel):
    architecture: str = Field(..., description="User-provided architecture description")
    quality_goals: List[str] = Field(default_factory=list, description="e.g., Reliability, Performance")
    domain: Optional[str] = Field(default=None, description="e.g., e-commerce, chat app, banking")

class TechStackResponse(BaseModel):
    version: str = "1.0"
    trace_id: str
    generated_at: str

    summary: str
    performance_review: List[PerfFinding]
    tech_recommendations: List[TechSuggestion]
    reference_comparison: ReferenceComparison
