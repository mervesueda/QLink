"""
integration/test_api_auth.py – Auth endpoint integration testleri.

Testcontainers PostgreSQL'i üzerinde gerçek HTTP istekleri gönderilir.
S3 mock'lanır (conftest.py'deki mock_s3 fixture).
"""

import pytest


class TestRegister:
    """POST /auth/register endpoint testleri."""

    def test_register_success(self, client, mock_s3):
        """Geçerli veriyle kayıt başarılı olmalı."""
        response = client.post(
            "/auth/register",
            json={"email": "test@example.com", "password": "Secure123!"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "test@example.com"
        assert "id" in data
        # Şifre hash'i yanıtta olmamalı
        assert "password" not in data
        assert "password_hash" not in data

    def test_register_duplicate_email(self, client, mock_s3):
        """Aynı e-posta iki kez kayıt edilemez."""
        payload = {"email": "duplicate@example.com", "password": "Secure123!"}
        client.post("/auth/register", json=payload)
        response = client.post("/auth/register", json=payload)
        assert response.status_code == 400
        assert "zaten kayıtlı" in response.json()["detail"]

    def test_register_invalid_email(self, client, mock_s3):
        """Geçersiz e-posta formatı reddedilmeli."""
        response = client.post(
            "/auth/register",
            json={"email": "not-an-email", "password": "Secure123!"},
        )
        assert response.status_code == 422

    def test_register_short_password(self, client, mock_s3):
        """8 karakterden kısa şifre reddedilmeli."""
        response = client.post(
            "/auth/register",
            json={"email": "short@example.com", "password": "abc"},
        )
        assert response.status_code == 422


class TestLogin:
    """POST /auth/login endpoint testleri."""

    def _register(self, client, email="login_test@example.com", password="Secure123!"):
        """Yardımcı: test kullanıcısı oluşturur."""
        client.post("/auth/register", json={"email": email, "password": password})

    def test_login_success(self, client, mock_s3):
        """Doğru kimlik bilgileriyle token alınabilmeli."""
        self._register(client, "success@example.com")
        response = client.post(
            "/auth/login",
            json={"email": "success@example.com", "password": "Secure123!"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client, mock_s3):
        """Yanlış şifre 401 döndürmeli."""
        self._register(client, "wrongpw@example.com")
        response = client.post(
            "/auth/login",
            json={"email": "wrongpw@example.com", "password": "WrongPass!"},
        )
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client, mock_s3):
        """Kayıtsız kullanıcı 401 döndürmeli."""
        response = client.post(
            "/auth/login",
            json={"email": "nobody@example.com", "password": "Secure123!"},
        )
        assert response.status_code == 401
