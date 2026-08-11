from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_pipeline():
    response = client.post(
        "/playground/execute",
        json={"text": "Revenue increased."},
    )

    assert response.status_code == 200

    body = response.json()

    # ExecutionResponse contract
    assert body["execution_id"]
    assert body["status"] == "success"

    assert isinstance(body["result"], dict)
    assert isinstance(body["node_outputs"], dict)
    assert isinstance(body["trace"], list)
    assert isinstance(body["metrics"], dict)
    assert isinstance(body["errors"], list)
    assert isinstance(body["metadata"], dict)

    # V9 deterministic MockProvider result
    assert body["result"]["summary"] == ("Mock response generated successfully.")

    # Summary agent output must also be present
    assert body["node_outputs"]["summary"]["summary"] == (
        "Mock response generated successfully."
    )

    # Successful execution must not contain errors
    assert body["errors"] == []
