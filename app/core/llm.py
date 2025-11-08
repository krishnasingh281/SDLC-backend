import os
import json
import uuid
import datetime as dt
from tenacity import retry, stop_after_attempt, wait_exponential
import google.generativeai as genai

from app.core.schemas import (
    TradeoffRequest, TradeoffResponse,
    ReviewRequest, ReviewResponse,
    RiskRequest, RiskResponse,
    TestCaseRequest, TestCaseResponse
)

# --- Configure Gemini ---
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
# Core API Logic
# ==========================

@retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=0.5, max=3))
def run_tradeoff(req: TradeoffRequest) -> TradeoffResponse:
    trace_id = str(uuid.uuid4())
    schema_hint = TradeoffResponse.model_json_schema()

    system = (
        "You are a senior software architect. "
        "Perform a design trade-off analysis and return VALID JSON "
        f"that exactly matches this schema: {schema_hint}"
    )

    user = req.model_dump_json()
    data = json.loads(_extract_json(_gemini([system, user])))

    data["trace_id"] = trace_id
    data["generated_at"] = _now()
    return TradeoffResponse(**data)


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

    # Fallbacks to keep Pydantic happy
    if not isinstance(data.get("risks"), list):
        data["risks"] = []
    if not isinstance(data.get("action_items"), list):
        data["action_items"] = []

    data["trace_id"] = trace_id
    data["generated_at"] = _now()
    return ReviewResponse(**data)



@retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=0.5, max=3))
def run_risk(req: RiskRequest) -> RiskResponse:
    trace_id = str(uuid.uuid4())
    schema_hint = RiskResponse.model_json_schema()

    system = (
        "You are a risk management expert. Identify and quantify system risks. "
        "Return VALID JSON strictly following this schema: "
        f"{schema_hint}. Include numerical likelihood and impact values (1–5)."
    )

    user = req.model_dump_json()
    data = json.loads(_extract_json(_gemini([system, user])))

    for r in data.get("risks", []):
        r["score"] = int(r.get("likelihood", 1)) * int(r.get("impact", 1))
        r.setdefault("risk_id", f"R-{uuid.uuid4().hex[:6]}")
    data["risks"] = sorted(data.get("risks", []), key=lambda x: x["score"], reverse=True)

    data["trace_id"] = trace_id
    data["generated_at"] = _now()
    return RiskResponse(**data)


@retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=0.5, max=3))
def run_testcases(req: TestCaseRequest) -> TestCaseResponse:
    trace_id = str(uuid.uuid4())
    schema_hint = TestCaseResponse.model_json_schema()

    system = (
        "You are a senior QA engineer. Generate BDD-style test cases (Given/When/Then). "
        f"Return VALID JSON that exactly matches this schema: {schema_hint}"
    )

    user = req.model_dump_json()
    data = json.loads(_extract_json(_gemini([system, user])))

    for i, c in enumerate(data.get("cases", []), start=1):
        c.setdefault("id", f"TC-{i:03}")
        c.setdefault("priority", "Medium")
        c.setdefault("type", "Positive")

    data["trace_id"] = trace_id
    data["generated_at"] = _now()
    return TestCaseResponse(**data)
