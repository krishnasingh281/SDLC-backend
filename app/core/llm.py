import json, uuid, datetime as dt
from tenacity import retry, stop_after_attempt, wait_exponential
from app.core.schemas import (
    TradeoffRequest, TradeoffResponse,
    ReviewRequest, ReviewResponse
)

def _extract_json(text: str) -> str:
    s, e = text.find("{"), text.rfind("}")
    return text[s:e+1] if (s >= 0 and e > s) else text

def _now() -> str:
    return dt.datetime.utcnow().isoformat() + "Z"

# TEMP: stubbed model output. Replace with real Gemini later.
def _gemini(messages: list[str]) -> str:
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
    else:
        body = {
            "version":"1.0",
            "summary":"Stub review summary",
            "risks":[
                {"area":"Architecture","severity":"High","likelihood":"Medium","impact":"Latency risk","mitigation":"Add cache"}
            ],
            "action_items":["Add metrics","Define SLAs"]
        }
        return json.dumps(body)

@retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=0.5, max=3))
def run_tradeoff(req: TradeoffRequest) -> TradeoffResponse:
    trace_id = str(uuid.uuid4())
    raw = _gemini(["system", req.model_dump_json()])
    data = json.loads(_extract_json(raw))
    data["trace_id"] = trace_id
    data["generated_at"] = _now()
    return TradeoffResponse(**data)

@retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=0.5, max=3))
def run_review(req: ReviewRequest) -> ReviewResponse:
    trace_id = str(uuid.uuid4())
    raw = _gemini(["system", req.model_dump_json()])
    data = json.loads(_extract_json(raw))
    data["trace_id"] = trace_id
    data["generated_at"] = _now()
    return ReviewResponse(**data)
