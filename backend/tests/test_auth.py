"""Integration tests for authentication endpoints and RBAC."""

from __future__ import annotations

from fastapi.testclient import TestClient

from src.app.services.auth import auth_service


def test_login_returns_token_pair(client: TestClient, create_user) -> None:
    email = "admin@example.com"
    password = "super-secret"
    create_user(email, password, roles=["admin"])

    response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    assert "access_token" in data and "refresh_token" in data


def test_login_rejects_invalid_password(client: TestClient, create_user) -> None:
    email = "admin2@example.com"
    create_user(email, "correct-password", roles=["admin"])

    response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "wrong"},
    )

    assert response.status_code == 401


def test_refresh_issues_new_tokens(client: TestClient, create_user) -> None:
    email = "viewer@example.com"
    password = "viewer-pass"
    create_user(email, password, roles=["viewer"])

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    refresh_token = login_response.json()["refresh_token"]

    refresh_response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )

    assert refresh_response.status_code == 200
    data = refresh_response.json()
    assert data["access_token"] != login_response.json()["access_token"]
    assert data["refresh_token"]


def test_admin_route_requires_admin_role(client: TestClient, create_user) -> None:
    email = "manager@example.com"
    password = "manager-pass"
    create_user(email, password, roles=["manager"])

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    token = login_response.json()["access_token"]

    response = client.get(
        "/api/v1/users/admin/pulse",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403

    # Create an admin and ensure access works.
    admin_email = "admin-role@example.com"
    admin_password = "admin-pass"
    create_user(admin_email, admin_password, roles=["admin"])
    admin_login = client.post(
        "/api/v1/auth/login",
        json={"email": admin_email, "password": admin_password},
    )
    admin_token = admin_login.json()["access_token"]
    admin_response = client.get(
        "/api/v1/users/admin/pulse",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert admin_response.status_code == 200
    assert admin_response.json()["status"] == "admin-ok"


def test_hashing_helpers_roundtrip() -> None:
    password = "roundtrip"
    hashed = auth_service.hash_password(password)
    assert auth_service.verify_password(password, hashed)
