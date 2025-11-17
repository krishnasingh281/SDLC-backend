import os
import json
import uuid
import datetime as dt
from tenacity import retry, stop_after_attempt, wait_exponential
import google.generativeai as genai


from app.core.schemas import (
    TradeoffRequest, TradeoffResponse, TradeoffRow,
    ReviewRequest, ReviewResponse, RiskItem,
    RiskRequest, RiskResponse, RiskRow,
    TestCaseRequest, TestCaseResponse, TestCase,
    DesignSuggestRequest, DesignSuggestResponse, DesignOption, # <-- Added missing Design imports here
    TechStackRequest, TechStackResponse, TechSuggestion, 
    PerfFinding, ReferenceComparison
)
from typing import List, Dict, Any, Optional, Union # Ensuring all types are imported

# --- Configure Gemini ---
# NOTE: Ensure GOOGLE_API_KEY environment variable is set
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
MODEL_NAME = "gemini-2.5-flash"


# ==========================
# Helper functions
# ==========================

def _extract_json(text: str) -> str:
    """Extract the largest JSON object from text (Gemini sometimes adds markdown)."""
    s, e = text.find("{"), text.rfind("}")
    return text[s:e + 1] if (s >= 0 and e > s) else text


def _now() -> str:
    """Return current UTC timestamp in ISO format."""
    return dt.datetime.now(dt.UTC).isoformat()


def _gemini(messages: list[str]) -> str:
    """Send system + user prompts to Gemini and return clean JSON string."""
    system, user_json = messages
    prompt = f"{system}\n\nUser input:\n{user_json}"

    model = genai.GenerativeModel(MODEL_NAME)
    response = model.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(
            response_mime_type="application/json"
        ),
    )

    text = (response.text or "").strip()
    try:
        json.loads(text)
        return text
    except json.JSONDecodeError:
        cleaned = _extract_json(text)
        json.loads(cleaned)
        return cleaned


# ==========================
# Core API Logic - PS-01: Trade-off Analysis
# ==========================

@retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=0.5, max=3))
def run_tradeoff(req: TradeoffRequest) -> TradeoffResponse:
    trace_id = str(uuid.uuid4())
    schema_hint = TradeoffResponse.model_json_schema()

    system = (
        "You are a senior software architect. "
        "Perform a clear, concise design trade-off analysis. "
        "Highlight only the most critical benefits, drawbacks, and recommendations "
        "without repeating information or giving lengthy explanations. "
        f"Return VALID JSON strictly matching this schema: {schema_hint}"
    )

    user = req.model_dump_json()
    raw = _gemini([system, user]) # Use the raw output from _gemini
    data = json.loads(_extract_json(raw))

    # Pydantic will validate structure, but we ensure essential fields are set
    data["trace_id"] = trace_id
    data["generated_at"] = _now()
    
    # Ensure nested objects are lists if the LLM was sparse
    data["matrix"] = data.get("matrix", []) or []

    return TradeoffResponse(**data)


# ==========================
# Core API Logic - PS-02: Design Review
# ==========================

@retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=0.5, max=3))
def run_review(req: ReviewRequest) -> ReviewResponse:
    trace_id = str(uuid.uuid4())
    schema_hint = ReviewResponse.model_json_schema()

    system = (
        "You are a senior design reviewer. "
        "Provide a concise and insightful design review summary. "
        "Highlight only the 2–3 most important risks and 3–4 key action items. "
        "Be factual, to-the-point, and avoid unnecessary elaboration. "
        f"Return VALID JSON strictly matching this schema: {schema_hint}"
    )

    user = req.model_dump_json()
    raw = _gemini([system, user])
    data = json.loads(_extract_json(raw))

    # Ensure structure validity
    data["risks"] = data.get("risks", []) or []
    data["action_items"] = data.get("action_items", []) or []

    data["trace_id"] = trace_id
    data["generated_at"] = _now()
    return ReviewResponse(**data)


# ==========================
# Core API Logic - PS-03: Design Risk Analysis
# ==========================

@retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=0.5, max=3))
def run_risk(req: RiskRequest) -> RiskResponse:
    trace_id = str(uuid.uuid4())
    schema_hint = RiskResponse.model_json_schema()

    system = (
        "You are a risk management expert. "
        "Identify only the most significant risks (up to 3–5). "
        "Keep descriptions short, precise, and avoid redundancy. "
        "Quantify likelihood (1-3) and impact (1-4). "
        "Compute score as likelihood * impact. "
        f"Return VALID JSON strictly following this schema: {schema_hint}"
    )

    user = req.model_dump_json()
    raw = _gemini([system, user])
    data = json.loads(_extract_json(raw))

    # Calculate score and assign IDs, then sort
    for r in data.get("risks", []):
        likelihood = int(r.get("likelihood", 1))
        impact = int(r.get("impact", 1))
        r["score"] = likelihood * impact
        r.setdefault("risk_id", f"R-{uuid.uuid4().hex[:6]}")
    data["risks"] = sorted(data.get("risks", []), key=lambda x: x["score"], reverse=True)

    data["trace_id"] = trace_id
    data["generated_at"] = _now()
    return RiskResponse(**data)


# ==========================
# Core API Logic - PS-06: Generate Test Cases
# ==========================

@retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=0.5, max=3))
def run_testcases(req: TestCaseRequest) -> TestCaseResponse:
    trace_id = str(uuid.uuid4())
    schema_hint = TestCaseResponse.model_json_schema()

    system = (
        "You are a senior QA engineer. "
        "Generate concise, BDD-style test cases (Given/When/Then). "
        "Focus on key functional scenarios only (limit to the requested count, up to 10). "
        "Avoid verbose descriptions or trivial cases. "
        f"Return VALID JSON strictly matching this schema: {schema_hint}"
    )

    user = req.model_dump_json()
    raw = _gemini([system, user])
    data = json.loads(_extract_json(raw))

    for i, c in enumerate(data.get("cases", []), start=1):
        c.setdefault("id", f"TC-{i:03}")
        c.setdefault("priority", "Medium")
        c.setdefault("type", "Positive")

    data["trace_id"] = trace_id
    data["generated_at"] = _now()
    return TestCaseResponse(**data)


# ==========================
# Core API Logic - PS-04: Suggest Design
# ==========================

@retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=0.5, max=3))
def run_design_suggest(req: DesignSuggestRequest) -> DesignSuggestResponse:
    trace_id = str(uuid.uuid4())
    schema_hint = DesignSuggestResponse.model_json_schema()

    system = (
    "You are a pragmatic software architect. Propose 2–3 concise design options.\n"
    "Rules:\n"
    "• VALID JSON ONLY matching the schema exactly.\n"
    "• Keep each option tight: when_to_use (1 line), 3–5 key_components, pros/cons max 3 each.\n"
    "• Use a tiny mermaid snippet or null for diagram_mermaid.\n"
    "• Keep the summary to 1–2 lines.\n"
    "• End with a single-paragraph recommendation.\n"
    "• If all options are cloud-specific, include at least one cloud-agnostic alternative (Docker+Postgres+Redis, etc.).\n"
    f"\nSchema: {schema_hint}"
)

    user = req.model_dump_json()
    raw = _gemini([system, user])
    data = json.loads(_extract_json(raw))

    # Harden output so Pydantic never explodes
    # Cap list lengths so outputs stay crisp
    for opt in data.get("options", []) or []:
        if isinstance(opt.get("key_components"), list):
            opt["key_components"] = opt["key_components"][:5]
        if isinstance(opt.get("pros"), list):
            opt["pros"] = opt["pros"][:3]
        if isinstance(opt.get("cons"), list):
            opt["cons"] = opt["cons"][:3]


    data["trace_id"] = trace_id
    data["generated_at"] = _now()
    data.setdefault("version", "1.0")
    data.setdefault("summary", "")
    data.setdefault("recommendation", "")

    return DesignSuggestResponse(**data)


# ==========================
# Core API Logic - PS-05: Tech Stack Recommendation
# ==========================

@retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=0.5, max=3))
def run_techstack(req: TechStackRequest) -> TechStackResponse:
    trace_id = str(uuid.uuid4())
    schema_hint = TechStackResponse.model_json_schema()

    system = (
        "You are a senior software architect. "
        "Evaluate the given architecture against quality attributes. "
        "For performance_review, **limit issues and suggestions to 3 items each** and keep them concise (1 sentence maximum). "
        "Recommend specific tech stacks (frameworks, databases, messaging, DevOps). "
        "For reference_comparison, **limit matched, missing, and improvements to 3 items each**. "
        f"Return VALID JSON strictly matching this schema: {schema_hint}"
    )

    user = req.model_dump_json()
    raw = _gemini([system, user])
    data = json.loads(_extract_json(raw))

    # Ensure fallback correctness
    data["trace_id"] = trace_id
    data["generated_at"] = _now()

    # Fix nested defaults if LLM messes up
    data.setdefault("performance_review", [])
    data.setdefault("tech_recommendations", [])
    data.setdefault("reference_comparison", {"matched": [], "missing": [], "improvements": []})

    return TechStackResponse(**data)