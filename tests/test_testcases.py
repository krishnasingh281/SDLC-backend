import json
from app import create_app

def test_testcases_200(monkeypatch):
    monkeypatch.setenv("API_KEY", "supersecret123")
    app = create_app()
    app.config["TESTING"] = True
    client = app.test_client()

    # stub _gemini to deterministic JSON
    from app.core import llm
    def fake_gemini(_):
        return json.dumps({
            "version":"1.0",
            "summary":"stub",
            "cases":[
                {
                    "id":"TC-001",
                    "title":"Reset password happy path",
                    "given":"A registered user exists",
                    "when":"They request a password reset via email",
                    "then":"A reset link is sent to their email",
                    "priority":"High",
                    "type":"Positive",
                    "data":{}
                }
            ]
        })
    monkeypatch.setattr(llm, "_gemini", fake_gemini)

    res = client.post("/api/v1/testcases/", json={
        "user_story": "As a user, I want to reset my password via email so that I can recover my account.",
        "count": 1
    }, headers={"X-API-Key":"supersecret123"})

    assert res.status_code == 200
    body = res.get_json()
    assert "cases" in body and len(body["cases"]) == 1
    case = body["cases"][0]
    assert all(k in case for k in ("given","when","then"))
