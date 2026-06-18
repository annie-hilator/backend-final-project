from fastapi.testclient import TestClient
import sys
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


def test_create_category():
    user = client.post(
        "/auth/register",
        json={
            "first_name": "Category",
            "last_name": "User",
            "email": "category_user@example.com",
            "password": "12345",
        },
    ).json()

    response = client.post(
        f"/categories/?user_id={user['id']}",
        json={"name": "Разработка"},
    )

    assert response.status_code in (200, 400)


def test_create_position():
    user = client.post(
        "/auth/register",
        json={
            "first_name": "Position",
            "last_name": "User",
            "email": "position_user@example.com",
            "password": "12345",
        },
    ).json()

    response = client.post(
        f"/positions/?user_id={user['id']}",
        json={"name": "Backend-разработчик"},
    )

    assert response.status_code in (200, 400)


def test_create_vacancy_flow():
    user = client.post(
        "/auth/register",
        json={
            "first_name": "Vacancy",
            "last_name": "User",
            "email": "vacancy_user@example.com",
            "password": "12345",
        },
    ).json()

    category = client.post(
        f"/categories/?user_id={user['id']}",
        json={"name": "Тестовая категория"},
    ).json()

    position = client.post(
        f"/positions/?user_id={user['id']}",
        json={"name": "Тестовая должность"},
    ).json()

    vacancy = client.post(
        f"/vacancies/?user_id={user['id']}",
        json={
            "title": "Python Developer",
            "description": "FastAPI backend",
            "is_open": True,
            "is_deleted": False,
            "category_id": category["id"],
            "position_id": position["id"],
        },
    )

    assert vacancy.status_code == 200
    assert vacancy.json()["title"] == "Python Developer"

    response = client.get("/vacancies/")
    assert response.status_code == 200


def test_create_candidate_resume_application_flow():
    user = client.post(
        "/auth/register",
        json={
            "first_name": "Resume",
            "last_name": "User",
            "email": "resume_user@example.com",
            "password": "12345",
        },
    ).json()

    category = client.post(
        f"/categories/?user_id={user['id']}",
        json={"name": "Категория резюме"},
    ).json()

    position = client.post(
        f"/positions/?user_id={user['id']}",
        json={"name": "Должность для отклика"},
    ).json()

    vacancy = client.post(
        f"/vacancies/?user_id={user['id']}",
        json={
            "title": "Backend Intern",
            "description": "Internship",
            "is_open": True,
            "is_deleted": False,
            "category_id": category["id"],
            "position_id": position["id"],
        },
    ).json()

    candidate = client.post(
        f"/resumes/candidates/?user_id={user['id']}",
        json={
            "full_name": "Анна Рашоян",
            "email": "ananan@test.com",
            "phone": "+79999999999",
        },
    ).json()

    resume = client.post(
        f"/resumes/?user_id={user['id']}",
        json={
            "experience": "Python, FastAPI",
            "status": "new",
            "is_deleted": False,
            "candidate_id": candidate["id"],
            "category_id": category["id"],
        },
    ).json()

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