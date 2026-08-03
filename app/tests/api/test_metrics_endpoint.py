from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.metrics import router


def test_metrics_endpoint():

    app = FastAPI()

    app.include_router(router)

    client = TestClient(app)

    response = client.get("/metrics")

    assert response.status_code == 200

    assert response.headers["content-type"].startswith("text/plain")
