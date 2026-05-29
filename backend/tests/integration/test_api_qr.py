"""
integration/test_api_qr.py – QR endpoint integration testleri.

Hem misafir hem kayıtlı kullanıcı senaryolarını kapsar.
S3 monkeypatch ile mock'lanır; sadece DB gerçek (Testcontainers).
"""

import pytest


def _register_and_login(client, email: str, password: str = "Secure123!") -> str:
    """Yardımcı: kullanıcı oluştur ve JWT token döndür."""
    client.post("/auth/register", json={"email": email, "password": password})
    resp = client.post("/auth/login", json={"email": email, "password": password})
    return resp.json()["access_token"]


def _auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


class TestGuestQRCreate:
    """Misafir kullanıcı QR oluşturma testleri."""

    def test_guest_can_create_qr(self, client, mock_s3):
        """Token olmadan QR oluşturulabilmeli (misafir akışı)."""
        response = client.post(
            "/qr/create",
            json={"content": "https://example.com", "qr_type": "url"},
        )
        assert response.status_code == 201
        data = response.json()
        assert "file_url" in data
        assert data["saved"] is False  # Misafir: DB'ye kaydedilmedi

    def test_guest_qr_url_type(self, client, mock_s3):
        """URL tipinde QR oluşturulabilmeli."""
        response = client.post(
            "/qr/create",
            json={"content": "https://github.com", "qr_type": "url"},
        )
        assert response.status_code == 201

    def test_guest_qr_text_type(self, client, mock_s3):
        """Metin tipinde QR oluşturulabilmeli."""
        response = client.post(
            "/qr/create",
            json={"content": "Merhaba Dünya", "qr_type": "text"},
        )
        assert response.status_code == 201

    def test_guest_qr_email_type(self, client, mock_s3):
        """E-posta tipinde QR oluşturulabilmeli."""
        response = client.post(
            "/qr/create",
            json={"content": "test@example.com", "qr_type": "email"},
        )
        assert response.status_code == 201

    def test_empty_content_rejected(self, client, mock_s3):
        """Boş içerik reddedilmeli."""
        response = client.post(
            "/qr/create",
            json={"content": "   ", "qr_type": "text"},
        )
        assert response.status_code == 422


class TestAuthenticatedQR:
    """Giriş yapmış kullanıcı QR testleri."""

    def test_logged_in_qr_saved_to_db(self, client, mock_s3):
        """Kayıtlı kullanıcı QR'ı DB'ye kaydedilmeli."""
        token = _register_and_login(client, "saved@example.com")
        response = client.post(
            "/qr/create",
            json={"content": "https://saved.com", "qr_type": "url"},
            headers=_auth_header(token),
        )
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert "user_id" in data

    def test_list_qr_empty_initially(self, client, mock_s3):
        """Yeni kullanıcının QR listesi boş olmalı."""
        token = _register_and_login(client, "empty_list@example.com")
        response = client.get("/qr/list", headers=_auth_header(token))
        assert response.status_code == 200
        assert response.json() == []

    def test_list_qr_after_create(self, client, mock_s3):
        """QR oluşturulduktan sonra listede görünmeli."""
        token = _register_and_login(client, "list_after@example.com")
        client.post(
            "/qr/create",
            json={"content": "https://list-test.com", "qr_type": "url"},
            headers=_auth_header(token),
        )
        response = client.get("/qr/list", headers=_auth_header(token))
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_get_qr_by_id(self, client, mock_s3):
        """ID ile belirli QR getirilebilmeli."""
        token = _register_and_login(client, "getbyid@example.com")
        create_resp = client.post(
            "/qr/create",
            json={"content": "https://getme.com", "qr_type": "url"},
            headers=_auth_header(token),
        )
        qr_id = create_resp.json()["id"]
        response = client.get(f"/qr/{qr_id}", headers=_auth_header(token))
        assert response.status_code == 200
        assert response.json()["id"] == qr_id

    def test_delete_qr(self, client, mock_s3):
        """QR silinebilmeli ve ardından 404 dönmeli."""
        token = _register_and_login(client, "delete_qr@example.com")
        create_resp = client.post(
            "/qr/create",
            json={"content": "https://deleteme.com", "qr_type": "url"},
            headers=_auth_header(token),
        )
        qr_id = create_resp.json()["id"]

        del_resp = client.delete(f"/qr/{qr_id}", headers=_auth_header(token))
        assert del_resp.status_code == 204

        get_resp = client.get(f"/qr/{qr_id}", headers=_auth_header(token))
        assert get_resp.status_code == 404

    def test_cannot_access_other_users_qr(self, client, mock_s3):
        """Başka kullanıcının QR'ına erişim 404 ile engellenmiş olmalı."""
        token1 = _register_and_login(client, "owner@example.com")
        token2 = _register_and_login(client, "hacker@example.com")

        create_resp = client.post(
            "/qr/create",
            json={"content": "https://private.com", "qr_type": "url"},
            headers=_auth_header(token1),
        )
        qr_id = create_resp.json()["id"]

        response = client.get(f"/qr/{qr_id}", headers=_auth_header(token2))
        assert response.status_code == 404

    def test_list_requires_auth(self, client, mock_s3):
        """/qr/list token olmadan 401 döndürmeli."""
        response = client.get("/qr/list")
        assert response.status_code == 401

    def test_delete_requires_auth(self, client, mock_s3):
        """/qr/{id} DELETE token olmadan 401 döndürmeli."""
        response = client.delete("/qr/some-fake-id")
        assert response.status_code == 401
