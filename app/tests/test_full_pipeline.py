from fastapi.testclient import (
    TestClient,
)

from app.main import (
    app,
)

client = TestClient(app)


def test_pipeline():

    r = client.post(
        "/playground/execute",
        json={"text": "Revenue increased."},
    )

    assert r.status_code == 200
