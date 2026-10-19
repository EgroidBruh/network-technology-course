from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def client():
    app.state.incidents.clear()
    app.state.incident_events.clear()
    with TestClient(app) as client:
        yield client
    app.state.incidents.clear()
    app.state.incident_events.clear()


@pytest.fixture
def payload():
    return {
        "source": "Zabbix", "error_code": "HTTP_503", "title": "Сервис недоступен",
        "description": "Сервер api-01 отвечает HTTP 503", "severity": "CRITICAL",
    }


def test_register_incident_and_event(client, payload):
    response = client.post("/incidents", json=payload)
    assert response.status_code == 201
    incident = response.json()
    assert incident.items() >= payload.items()
    assert incident["status"] == "OPEN"
    assert client.get(f"/incidents/{incident['id']}").json() == incident
    assert client.get("/incidents").json() == [incident]
    events = client.get(f"/incidents/{incident['id']}/events").json()
    assert len(events) == 1
    assert events[0]["event_type"] == "IncidentCreatedEvent"
    assert events[0]["incident_id"] == incident["id"]
    assert events[0]["severity"] == "CRITICAL"
    assert events[0]["occurred_at"] == incident["created_at"]


@pytest.mark.parametrize("field", ["source", "error_code", "title", "description", "severity"])
def test_missing_field_does_not_register_anything(client, payload, field):
    del payload[field]
    assert client.post("/incidents", json=payload).status_code == 422
    assert client.get("/incidents").json() == []
    assert app.state.incident_events == {}


@pytest.mark.parametrize("changes", [
    {"severity": "FATAL"}, {"source": "  "}, {"error_code": ""},
    {"description": " "}, {"title": ""}, {"unexpected": "field"},
])
def test_invalid_payload_does_not_register_anything(client, payload, changes):
    payload.update(changes)
    assert client.post("/incidents", json=payload).status_code == 422
    assert client.get("/incidents").json() == []
    assert app.state.incident_events == {}


@pytest.mark.parametrize("severity", ["INFO", "WARNING", "CRITICAL"])
def test_supported_severity(client, payload, severity):
    payload["severity"] = severity
    assert client.post("/incidents", json=payload).json()["severity"] == severity


def test_unknown_incident(client):
    incident_id = uuid4()
    assert client.get(f"/incidents/{incident_id}").status_code == 404
    assert client.get(f"/incidents/{incident_id}/events").status_code == 404
    assert client.get("/incidents/not-a-uuid").status_code == 422


def test_existing_routers_are_still_available(client):
    assert client.get("/employees").status_code == 200
    assert client.get("/duty/shifts").status_code == 200
