import os, json
from app import create_app

def test_design_200(monkeypatch):
    monkeypatch.setenv("API_KEY", "supersecret123")

    # stub LLM so test is deterministic
    from app.core import llm
    def fake_gemini(_):
        return json.dumps({
            "version":"1.0",
            "summary":"Two viable options for the stated goals.",
            "options":[
                {
                    "name":"Simple 3-tier",
                    "when_to_use":"Small team, moderate traffic.",
                    "key_components":["API","Service","DB"],
                    "pros":["Easy to build","Low ops overhead"],
                    "cons":["Limited scalability"],
                    "diagram_mermaid":"graph LR; API-->Svc; Svc-->DB;"
                },
                {
                    "name":"Queue-based async",
                    "when_to_use":"Spiky workload; decoupling needed.",
                    "key_components":["API","Worker","Queue","DB"],
                    "pros":["Resilient to spikes","Improved user latency"],
                    "cons":["More moving parts"],
                    "diagram_mermaid":"graph LR; API-->Q; Q-->W; W-->DB;"
                }
            ],
            "recommendation":"Pick queue-based async if spikes/decoupling matter; otherwise 3-tier."
        })
    monkeypatch.setattr(llm, "_gemini", fake_gemini)

    app = create_app()
    client = app.test_client()

    payload = {
        "problem":"Users upload images; process and notify.",
        "quality_goals":["Scalability","Reliability"],
        "constraints":["Team of 3","Must use PostgreSQL"]
    }
    res = client.post("/api/v1/design/", json=payload, headers={"X-API-Key":"supersecret123"})
    assert res.status_code == 200
    data = res.get_json()
    assert "options" in data and len(data["options"]) >= 1
    assert "recommendation" in data
