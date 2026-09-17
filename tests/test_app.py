from fastapi.testclient import TestClient

from src import app as app_module

client = TestClient(app_module.app)


def test_get_activities_returns_data():
    response = client.get("/activities")

    assert response.status_code == 200
    activities = response.json()
    assert "Chess Club" in activities
    assert "participants" in activities["Chess Club"]


def test_signup_rejects_duplicate_email(monkeypatch):
    activity_name = "Chess Club"
    email = "already@mergington.edu"
    monkeypatch.setitem(app_module.activities[activity_name], "participants", [email])

    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up"


def test_signup_rejects_full_activity(monkeypatch):
    activity_name = "Programming Class"
    monkeypatch.setitem(
        app_module.activities[activity_name],
        "participants",
        [f"student{i}@mergington.edu" for i in range(app_module.activities[activity_name]["max_participants"])],
    )

    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": "newstudent@mergington.edu"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Activity is full"


def test_unregister_participant(monkeypatch):
    activity_name = "Chess Club"
    email = "remove@mergington.edu"
    monkeypatch.setitem(app_module.activities[activity_name], "participants", ["existing@mergington.edu", email])

    response = client.delete(f"/activities/{activity_name}/participants/{email}")

    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from {activity_name}"
    assert email not in app_module.activities[activity_name]["participants"]
