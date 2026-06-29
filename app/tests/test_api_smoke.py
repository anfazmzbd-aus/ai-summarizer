from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_docs_available():

    r = client.get("/docs")

    assert r.status_code == 200