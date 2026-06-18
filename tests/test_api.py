from fastapi.testclient import TestClient
import sys
import uuid
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from app.main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "HR Service is running"


def test_register_user():
    response = client.post(
        "/auth/register",
        json={
            "first_name": "Test",
            "last_name": "User",
            "email": "test_user@example.com",
            "password": "12345",
        },
    )

    assert response.status_code in (200, 400)


def test_login_user():
    client.post(
        "/auth/register",
        json={
            "first_name": "Login",
            "last_name": "User",
            "email": "login_user@example.com",
            "password": "12345",
        },
    )

    response = client.post(
        "/auth/login",
        json={
            "email": "login_user@example.com",
            "password": "12345",
        },
    )

    assert response.status_code == 200
    assert "user_id" in response.json()

def create_test_user():
    email = f"user_{uuid.uuid4().hex}@example.com"

    response = client.post(
        "/auth/register",
        json={
            "first_name": "Test",
            "last_name": "User",
            "email": email,
            "password": "12345",
        },
    )

    assert response.status_code == 200
    return response.json()


def test_create_category():
    user = create_test_user()

    response = client.post(
        f"/categories/?user_id={user['id']}",
        json={"name": f"Разработка {uuid.uuid4().hex}"},
    )

    assert response.status_code == 200


def test_create_position():
    user = create_test_user()

    response = client.post(
        f"/positions/?user_id={user['id']}",
        json={"name": f"Backend-разработчик {uuid.uuid4().hex}"},
    )

    assert response.status_code == 200


def test_create_vacancy_flow():
    user = create_test_user()
    vacancy, _, _ = create_vacancy(user["id"])

    assert vacancy["title"] == "Test Vacancy"

    response = client.get("/vacancies/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_candidate_resume_application_flow():
    user = create_test_user()

    vacancy, _, _ = create_vacancy(user["id"])
    _, resume, _ = create_candidate_resume(user["id"])

    application = client.post(
        f"/applications/?user_id={user['id']}",
        json={
            "status": "new",
            "is_deleted": False,
            "vacancy_id": vacancy["id"],
            "resume_id": resume["id"],
        },
    )

    assert application.status_code == 200

    stats = client.get(f"/applications/statistics/vacancy/{vacancy['id']}")
    assert stats.status_code == 200
    assert stats.json()["total_applications"] >= 1

def create_category_position(user_id: int):
    unique = uuid.uuid4().hex

    category = client.post(
        f"/categories/?user_id={user_id}",
        json={"name": f"Category {unique}"},
    )

    position = client.post(
        f"/positions/?user_id={user_id}",
        json={"name": f"Position {unique}"},
    )

    assert category.status_code == 200
    assert position.status_code == 200

    return category.json(), position.json()


def create_vacancy(user_id: int):
    category, position = create_category_position(user_id)

    response = client.post(
        f"/vacancies/?user_id={user_id}",
        json={
            "title": "Test Vacancy",
            "description": "Test vacancy description",
            "is_open": True,
            "is_deleted": False,
            "category_id": category["id"],
            "position_id": position["id"],
        },
    )

    assert response.status_code == 200
    return response.json(), category, position


def create_candidate_resume(user_id: int):
    category, _ = create_category_position(user_id)
    unique = uuid.uuid4().hex

    candidate = client.post(
        f"/resumes/candidates/?user_id={user_id}",
        json={
            "full_name": "Test Candidate",
            "email": f"candidate_{unique}@test.com",
            "phone": "+79990000000",
        },
    )

    assert candidate.status_code == 200

    resume = client.post(
        f"/resumes/?user_id={user_id}",
        json={
            "experience": "Python, FastAPI",
            "status": "new",
            "is_deleted": False,
            "candidate_id": candidate.json()["id"],
            "category_id": category["id"],
        },
    )

    assert resume.status_code == 200
    return candidate.json(), resume.json(), category


def test_change_password():
    user = create_test_user()

    response = client.post(
        "/auth/change-password",
        json={
            "user_id": user["id"],
            "old_password": "12345",
            "new_password": "54321",
        },
    )

    assert response.status_code == 200
    assert "new_token" in response.json()


def test_refresh_token():
    user = create_test_user()

    response = client.post(
        "/auth/refresh-token",
        json={"user_id": user["id"]},
    )

    assert response.status_code == 200
    assert "token" in response.json()


def test_close_vacancy():
    user = create_test_user()
    vacancy, _, _ = create_vacancy(user["id"])

    response = client.patch(
        f"/vacancies/{vacancy['id']}/close?user_id={user['id']}"
    )

    assert response.status_code == 200
    assert response.json()["is_open"] is False


def test_soft_delete_vacancy():
    user = create_test_user()
    vacancy, _, _ = create_vacancy(user["id"])

    response = client.delete(
        f"/vacancies/{vacancy['id']}?user_id={user['id']}"
    )

    assert response.status_code == 200
    assert "marked as deleted" in response.json()["message"]


def test_filter_vacancies_by_is_open():
    user = create_test_user()
    create_vacancy(user["id"])

    response = client.get("/vacancies/?is_open=true")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_update_resume_status():
    user = create_test_user()
    _, resume, _ = create_candidate_resume(user["id"])

    response = client.patch(
        f"/resumes/{resume['id']}?user_id={user['id']}",
        json={"status": "interview"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "interview"


def test_soft_delete_resume():
    user = create_test_user()
    _, resume, _ = create_candidate_resume(user["id"])

    response = client.delete(
        f"/resumes/{resume['id']}?user_id={user['id']}"
    )

    assert response.status_code == 200
    assert "marked as deleted" in response.json()["message"]


def test_filter_resumes_by_status():
    user = create_test_user()
    create_candidate_resume(user["id"])

    response = client.get("/resumes/?status=new")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_invalid_user_access():
    response = client.post(
        "/categories/?user_id=999999",
        json={"name": f"Invalid {uuid.uuid4().hex}"},
    )

    assert response.status_code == 401


def test_create_application_for_closed_vacancy():
    user = create_test_user()
    vacancy, _, _ = create_vacancy(user["id"])
    _, resume, _ = create_candidate_resume(user["id"])

    client.patch(f"/vacancies/{vacancy['id']}/close?user_id={user['id']}")

    response = client.post(
        f"/applications/?user_id={user['id']}",
        json={
            "status": "new",
            "is_deleted": False,
            "vacancy_id": vacancy["id"],
            "resume_id": resume["id"],
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Vacancy is closed"

def test_get_vacancy_by_id():
    user = create_test_user()
    vacancy, _, _ = create_vacancy(user["id"])

    response = client.get(f"/vacancies/{vacancy['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == vacancy["id"]


def test_update_vacancy():
    user = create_test_user()
    vacancy, _, _ = create_vacancy(user["id"])

    response = client.patch(
        f"/vacancies/{vacancy['id']}?user_id={user['id']}",
        json={"title": "Updated Vacancy"},
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Updated Vacancy"


def test_get_not_existing_vacancy():
    response = client.get("/vacancies/999999")

    assert response.status_code == 404


def test_create_vacancy_with_wrong_category():
    user = create_test_user()
    _, position = create_category_position(user["id"])

    response = client.post(
        f"/vacancies/?user_id={user['id']}",
        json={
            "title": "Wrong Category Vacancy",
            "description": "Test",
            "is_open": True,
            "is_deleted": False,
            "category_id": 999999,
            "position_id": position["id"],
        },
    )

    assert response.status_code == 404


def test_get_resume_by_id():
    user = create_test_user()
    _, resume, _ = create_candidate_resume(user["id"])

    response = client.get(f"/resumes/{resume['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == resume["id"]


def test_get_not_existing_resume():
    response = client.get("/resumes/999999")

    assert response.status_code == 404


def test_create_application_and_get_by_id():
    user = create_test_user()
    vacancy, _, _ = create_vacancy(user["id"])
    _, resume, _ = create_candidate_resume(user["id"])

    created = client.post(
        f"/applications/?user_id={user['id']}",
        json={
            "status": "new",
            "is_deleted": False,
            "vacancy_id": vacancy["id"],
            "resume_id": resume["id"],
        },
    ).json()

    response = client.get(f"/applications/{created['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_filter_applications_by_status():
    user = create_test_user()
    vacancy, _, _ = create_vacancy(user["id"])
    _, resume, _ = create_candidate_resume(user["id"])

    client.post(
        f"/applications/?user_id={user['id']}",
        json={
            "status": "new",
            "is_deleted": False,
            "vacancy_id": vacancy["id"],
            "resume_id": resume["id"],
        },
    )

    response = client.get("/applications/?status=new")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_update_application_status():
    user = create_test_user()
    vacancy, _, _ = create_vacancy(user["id"])
    _, resume, _ = create_candidate_resume(user["id"])

    created = client.post(
        f"/applications/?user_id={user['id']}",
        json={
            "status": "new",
            "is_deleted": False,
            "vacancy_id": vacancy["id"],
            "resume_id": resume["id"],
        },
    ).json()

    response = client.patch(
        f"/applications/{created['id']}?user_id={user['id']}",
        json={"status": "accepted"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "accepted"


def test_soft_delete_application():
    user = create_test_user()
    vacancy, _, _ = create_vacancy(user["id"])
    _, resume, _ = create_candidate_resume(user["id"])

    created = client.post(
        f"/applications/?user_id={user['id']}",
        json={
            "status": "new",
            "is_deleted": False,
            "vacancy_id": vacancy["id"],
            "resume_id": resume["id"],
        },
    ).json()

    response = client.delete(
        f"/applications/{created['id']}?user_id={user['id']}"
    )

    assert response.status_code == 200
    assert "marked as deleted" in response.json()["message"]


def test_create_application_with_wrong_vacancy():
    user = create_test_user()
    _, resume, _ = create_candidate_resume(user["id"])

    response = client.post(
        f"/applications/?user_id={user['id']}",
        json={
            "status": "new",
            "is_deleted": False,
            "vacancy_id": 999999,
            "resume_id": resume["id"],
        },
    )

    assert response.status_code == 404


def test_create_application_with_wrong_resume():
    user = create_test_user()
    vacancy, _, _ = create_vacancy(user["id"])

    response = client.post(
        f"/applications/?user_id={user['id']}",
        json={
            "status": "new",
            "is_deleted": False,
            "vacancy_id": vacancy["id"],
            "resume_id": 999999,
        },
    )

    assert response.status_code == 404