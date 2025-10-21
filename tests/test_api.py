import json


def test_metrics_endpoint(client):
    resp = client.get("/api/metrics")
    data = json.loads(resp.data)
    assert resp.status_code == 200
    assert data["status"] == "success"
    assert "cpu" in data["data"]


def test_history_endpoint(client):
    resp = client.get("/api/history")
    data = json.loads(resp.data)
    assert resp.status_code == 200
    assert data["status"] == "success"
