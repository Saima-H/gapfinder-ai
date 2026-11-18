from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch

client = TestClient(app)

# 1. Test that unauthenticated users are blocked (No mock needed)
def test_get_all_scripts_requires_auth():
    response = client.get("/all-scripts")
    assert response.status_code == 401

# 2. Test that a student cannot hit the teacher endpoint
@patch("main.get_user_email")
def test_student_cannot_access_teacher_endpoint(mock_get_email):
    mock_get_email.return_value = "student1@test.com" # Simulate a student
    response = client.get("/all-scripts", headers={"Authorization": "Bearer dummy"})
    assert response.status_code == 403
    assert response.json()["detail"] == "Access Denied: You are not a registered teacher."

# 3. Test that a teacher CAN hit the teacher endpoint
@patch("main.get_user_email")
def test_teacher_can_access_all_scripts(mock_get_email):
    mock_get_email.return_value = "teacher@test.com" # Simulate a teacher
    response = client.get("/all-scripts", headers={"Authorization": "Bearer dummy"})
    assert response.status_code == 200

# 4. Test that a student cannot view another student's result
@patch("main.get_user_email")
def test_student_cannot_view_other_result(mock_get_email):
    mock_get_email.return_value = "student1@test.com" # Simulate Student 1
    response = client.get("/results/2", headers={"Authorization": "Bearer dummy"})
    assert response.status_code == 403
    assert response.json()["detail"] == "You are not allowed to view this result"

# 5. Test invalid token (Will fail JWT verification naturally)
def test_invalid_token():
    response = client.get("/all-scripts", headers={"Authorization": "Bearer invalid_token"})
    assert response.status_code == 401