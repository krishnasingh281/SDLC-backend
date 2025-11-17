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
    attribute: str       # e.g., Reliability, Latency, Scalability
    score: int           # 1–10 rating
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


# ==============================================================================
# PS-07: Code Compliance & Standards Check
# ==============================================================================

class Finding(BaseModel):
    line: Optional[int] = Field(None, description="The line number where the issue was found.")
    type: Literal["SECURITY_ERROR", "DESIGN_WARNING", "STYLE_VIOLATION"]
    message: str = Field(..., description="Concise description of the violation or suggestion.")
    severity: Literal["Critical", "High", "Medium", "Low"]

class ComplianceRequest(BaseModel):
    code_snippet: str = Field(..., description="The code snippet to analyze (e.g., Python function or block).")
    language: str = Field("Python", description="The programming language of the snippet (e.g., Python, JavaScript).")
    standard_context: Optional[str] = Field(None, description="Specific standards or rules to check against (e.g., 'Use PEP8', 'Avoid global state').")

class ComplianceResponse(BaseModel):
    version: str = "1.0"
    trace_id: str
    generated_at: str
    
    overall_score: int = Field(..., description="Overall compliance score out of 100.")
    summary: str = Field(..., description="A one-paragraph summary of the compliance status and biggest risks.")
    findings: List[Finding] = Field(default_factory=list, description="List of specific issues found in the code.")


class GenerationRequest(BaseModel):
    prompt: str = Field(..., description="The user story, function signature, or high-level description of the code required.")
    language: str = Field("Python", description="The desired programming language for the output code.")
    context_code: Optional[str] = Field(None, description="Existing code context in the file to help the AI complete the function.")
    framework: Optional[str] = Field(None, description="Specific framework or library to use (e.g., FastAPI, Pandas).")

class GenerationResponse(BaseModel):
    version: str = "1.0"
    trace_id: str
    generated_at: str
    
    generated_code: str = Field(..., description="The fully generated code snippet or boilerplate.")
    explanation: str = Field(..., description="A brief explanation of the code and the libraries used.")
    libraries_suggested: List[str] = Field(default_factory=list, description="List of specific libraries or packages that were used/suggested.")


# ==============================================================================
# PS-09: Streamlining Debugging / Debug Assistant
# ==============================================================================

class IssueFinding(BaseModel):
    category: Literal["Bug", "Bottleneck", "Logic Error", "Security Flaw"]
    location: str = Field(..., description="The filename:line_number or function name where the issue is centered.")
    description: str = Field(..., description="Detailed explanation of the problem detected.")
    
class DebugRequest(BaseModel):
    failing_code: str = Field(..., description="The code snippet or function causing the issue.")
    traceback: Optional[str] = Field(None, description="The full traceback, error message, or log snippet associated with the failure.")
    expected_behavior: str = Field(..., description="What the code was supposed to do.")
    language: str = Field("Python", description="The programming language of the code.")

class DebugResponse(BaseModel):
    version: str = "1.0"
    trace_id: str
    generated_at: str
    
    root_cause_summary: str = Field(..., description="A concise summary of the primary cause of the failure or bottleneck.")
    findings: List[IssueFinding] = Field(default_factory=list, description="List of 1-3 critical issues identified.")
    suggested_fix: str = Field(..., description="The corrected, ready-to-use code snippet or a clear description of the required fix.")
    optimization_notes: List[str] = Field(default_factory=list, description="Notes on potential performance optimizations found during analysis (max 3 points).")