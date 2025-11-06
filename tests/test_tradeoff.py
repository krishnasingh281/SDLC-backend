import json
from app import create_app
import warnings

def pytest_configure():
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    warnings.filterwarnings("ignore", message="PydanticDeprecatedSince20")


def test_tradeoff_200(monkeypatch):
    # ensure the app key matches what the test will send
    monkeypatch.setenv("API_KEY", "supersecret123")

    app = create_app()
    app.config["TESTING"] = True
    client = app.test_client()

    # stub _gemini so test is deterministic
    from app.core import llm
    def fake_gemini(_):
        return json.dumps({
            "version": "1.0",
            "context": {"option_a": "Monolith", "option_b": "Microservices"},
            "criteria": ["Scalability"],
            "matrix": [{
                "criterion": "Scalability",
                "option_a": "ok",
                "option_b": "better",
                "verdict": "B",
                "notes": ""
            }],
            "summary": "stub",
            "recommendation": {
                "winner": "B",
                "rationale": "x",
                "caveats": "y"
            }
        })
    monkeypatch.setattr(llm, "_gemini", fake_gemini)

    res = client.post(
        "/api/v1/tradeoff/",
        json={
            "option_a": "Monolith",
            "option_b": "Microservices",
            "criteria": ["Scalability"]
        },
        headers={"X-API-Key": "supersecret123"}
    )

    assert res.status_code == 200
    body = res.get_json()
    assert "recommendation" in body
    assert body["recommendation"]["winner"] in ("A", "B", "Tie", "Insufficient Data")
