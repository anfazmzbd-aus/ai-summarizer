from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.routes.ai import router


def test_endpoint():

    app = FastAPI()

    app.include_router(router)

    client = TestClient(app)

    response = client.post(
        "/api/v1/summarize",
        json={
            "text": "Hello World",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert "summary" in body
    assert body["model"] == "demo"
