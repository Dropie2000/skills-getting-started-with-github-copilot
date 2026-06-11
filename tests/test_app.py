from fastapi.testclient import TestClient

from src.app import app

client = TestClient(app)


def test_get_activities_returns_all_activities():
    response = client.get("/activities")

    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    assert "Chess Club" in activities
    assert "Programming Class" in activities


def test_signup_for_activity_adds_participant():
    email = "test.student@mergington.edu"
    activity_name = "Chess Club"
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"

    # Verify participant was added
    activities = client.get("/activities").json()
    assert email in activities[activity_name]["participants"]


def test_signup_duplicate_participant_returns_400():
    email = "duplicate.student@mergington.edu"
    activity_name = "Programming Class"

    first_response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    assert first_response.status_code == 200

    second_response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    assert second_response.status_code == 400
    assert second_response.json()["detail"] == "Student already signed up for this activity"


def test_unregister_participant_removes_participant():
    email = "delete.student@mergington.edu"
    activity_name = "Gym Class"

    signup_response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    assert signup_response.status_code == 200

    delete_response = client.delete(f"/activities/{activity_name}/participants", params={"email": email})
    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == f"Unregistered {email} from {activity_name}"

    activities = client.get("/activities").json()
    assert email not in activities[activity_name]["participants"]


def test_unregister_missing_participant_returns_404():
    activity_name = "Robotics Club"
    email = "missing.student@mergington.edu"

    response = client.delete(f"/activities/{activity_name}/participants", params={"email": email})
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
