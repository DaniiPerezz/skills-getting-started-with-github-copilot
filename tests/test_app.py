import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture(autouse=True)
def reset_activities_state():
    original = copy.deepcopy(activities)
    activities.clear()
    activities.update(copy.deepcopy(original))
    yield
    activities.clear()
    activities.update(copy.deepcopy(original))


client = TestClient(app)


def test_get_activities_returns_activity_data():
    response = client.get("/activities")

    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert "Programming Class" in payload
    assert "participants" in payload["Chess Club"]


def test_signup_adds_participant_and_rejects_duplicates():
    activity = "Soccer Team"
    email = "student@example.edu"

    response = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity}"
    assert email in activities[activity]["participants"]

    duplicate_response = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert duplicate_response.status_code == 400
    assert "already signed up" in duplicate_response.json()["detail"]


def test_unregister_removes_participant():
    activity = "Soccer Team"
    email = "remove@example.edu"

    client.post(f"/activities/{activity}/signup", params={"email": email})
    response = client.delete(f"/activities/{activity}/unregister", params={"email": email})

    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from {activity}"
    assert email not in activities[activity]["participants"]


def test_unregister_missing_participant_returns_404():
    activity = "Soccer Team"
    email = "missing@example.edu"

    response = client.delete(f"/activities/{activity}/unregister", params={"email": email})

    assert response.status_code == 404
    assert "not registered" in response.json()["detail"]
