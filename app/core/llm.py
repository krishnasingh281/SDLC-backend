# app/core/llm.py
import json, uuid, datetime as dt
from tenacity import retry, stop_after_attempt, wait_exponential
from app.core.schemas import (
    TradeoffRequest, TradeoffResponse,
    ReviewRequest, ReviewResponse,
    RiskRequest, RiskResponse, RiskRow,
    TestCaseRequest, TestCaseResponse, TestCase,
)

def _extract_json(text: str) -> str:
    s, e = text.find("{"), text.rfind("}")
    return text[s:e+1] if (s >= 0 and e > s) else text

def _now() -> str:
    return dt.datetime.utcnow().isoformat() + "Z"

# Stub so tests can monkeypatch this
def _gemini(messages: list[str]) -> str:
    # minimal deterministic stub
    system, user_json = messages
    u = json.loads(user_json)
    if "option_a" in u:
        body = {
            "version":"1.0",
            "context":{"option_a":u["option_a"],"option_b":u["option_b"]},
            "criteria":u.get("criteria",[]),
            "matrix":[
                {"criterion":c,"option_a":"ok","option_b":"better","verdict":"B","notes":""}
                for c in u.get("criteria",[])
            ],
            "summary":"Stub summary",
            "recommendation":{"winner":"B","rationale":"Stub rationale","caveats":"Stub caveats"}
        }
        return json.dumps(body)
    elif "design" in u:
        body = {
            "version":"1.0",
            "summary":"Stub risk summary",
            "risks":[
                {"risk_id":"R-000001","category":"Reliability","description":"Possible queue backlog",
                 "likelihood":2,"impact":3,"score":6,"mitigation":"Add DLQ"}
            ]
        }
        return json.dumps(body)
    else:
        count = int(u.get("count", 6))
        cases = []
        for i in range(count):
            cases.append({
                "id": f"TC-{i+1:03}",
                "title": f"Sample case {i+1}",
                "given": "A valid user in the system",
                "when": "They perform the primary action",
                "then": "The expected outcome occurs",
                "priority": "Medium",
                "type": "Positive",
                "data": {}
            })
        body = {
            "version": "1.0",
            "summary": "Stub test cases generated",
            "cases": cases
        }
        return json.dumps(body)

@retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=0.5, max=3))
def run_tradeoff(req: TradeoffRequest) -> TradeoffResponse:
    trace_id = str(uuid.uuid4())
    schema_hint = TradeoffResponse.model_json_schema()
    system = f"You are a senior architect. Output VALID JSON ONLY matching this schema: {schema_hint}"
    user = req.model_dump_json()
    data = json.loads(_extract_json(_gemini([system, user])))
    data["trace_id"] = trace_id
    data["generated_at"] = _now()
    return TradeoffResponse(**data)

@retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=0.5, max=3))
def run_review(req: ReviewRequest) -> ReviewResponse:
    trace_id = str(uuid.uuid4())
    schema_hint = ReviewResponse.model_json_schema()
    system = f"You are a meticulous design reviewer. Output VALID JSON ONLY matching this schema: {schema_hint}"
    user = req.model_dump_json()
    data = json.loads(_extract_json(_gemini([system, user])))
    data["trace_id"] = trace_id
    data["generated_at"] = _now()
    return ReviewResponse(**data)

@retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=0.5, max=3))
def run_risk(req: RiskRequest) -> RiskResponse:
    trace_id = str(uuid.uuid4())
    schema_hint = RiskResponse.model_json_schema()
    system = f"You are a risk management expert. Output VALID JSON ONLY matching this schema: {schema_hint}"
    user = req.model_dump_json()
    data = json.loads(_extract_json(_gemini([system, user])))

    # ensure score and id present; sort
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
        "You are a senior QA engineer. "
        "Generate high-quality BDD-style test cases (Given/When/Then). "
        f"Output VALID JSON ONLY matching this schema: {schema_hint}"
    )
    user = req.model_dump_json()

    data = json.loads(_extract_json(_gemini([system, user])))

    # ensure IDs and types look sane
    for i, c in enumerate(data.get("cases", []), start=1):
        c.setdefault("id", f"TC-{i:03}")
        c.setdefault("priority", "Medium")
        c.setdefault("type", "Positive")

    data["trace_id"] = trace_id
    data["generated_at"] = _now()
    return TestCaseResponse(**data)
