from fastapi import status
from fastapi.testclient import TestClient

from run_api import app
from src import messages

client = TestClient(app)


def test_get_root():
    response = client.get("/")
    assert response.status_code == status.HTTP_418_IM_A_TEAPOT
    data = response.json()
    assert data == messages.RootMessage().model_dump()
