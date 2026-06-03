"""
integration/test_api_v1.py – /api/v1/qr alias endpoint integration testleri.

Şartname endpoint'lerinin (/api/v1/qr/generate, /api/v1/qr/history vb.)
Factory Boy ve Faker kullanılarak dinamik verilerle test edilmesi.
"""

from tests.factories import QRCodeFactory, UserFactory


def _register_and_login(client, email: str, password: str = "Secure123!") -> str:
    """Yardımcı: kullanıcı oluştur ve JWT token döndür."""
    client.post("/auth/register", json={"email": email, "password": password})
    resp = client.post("/auth/login", json={"email": email, "password": password})
    return resp.json()["access_token"]


def _auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


class TestV1GenerateEndpoint:
    """POST /api/v1/qr/generate endpoint testleri."""

    def test_generate_as_guest(self, client, mock_s3):
        """Misafir olarak /api/v1/qr/generate çalışmalı."""
        # Factory Boy ile dinamik veri üret
        factory_data = QRCodeFactory.build()
        response = client.post(
            "/api/v1/qr/generate",
            json={"content": factory_data.content, "qr_type": "url"},
        )
        assert response.status_code == 201
        body = response.json()
        assert "file_url" in body
        assert body["saved"] is False

    def test_generate_authenticated_saves_to_db(self, client, mock_s3):
        """Kayıtlı kullanıcı olarak /api/v1/qr/generate çalışmalı ve DB'ye kaydetmeli."""
        user = UserFactory.build()
        token = _register_and_login(client, user.email)

        factory_data = QRCodeFactory.build()
        response = client.post(
            "/api/v1/qr/generate",
            json={"content": factory_data.content, "qr_type": "url"},
            headers=_auth_header(token),
        )
        assert response.status_code == 201
        body = response.json()
        assert "id" in body
        assert "user_id" in body

    def test_generate_all_qr_types(self, client, mock_s3):
        """URL, metin ve e-posta tipleri /api/v1/qr/generate ile çalışmalı."""
        for qr_type, content in [
            ("url", "https://test.example.com"),
            ("text", "Merhaba Dünya"),
            ("email", "info@example.com"),
        ]:
            resp = client.post(
                "/api/v1/qr/generate",
                json={"content": content, "qr_type": qr_type},
            )
            assert resp.status_code == 201

    def test_generate_returns_image_data(self, client, mock_s3):
        """Yanıt içinde base64 image_data bulunmalı."""
        response = client.post(
            "/api/v1/qr/generate",
            json={"content": "https://example.com", "qr_type": "url"},
        )
        assert response.status_code == 201
        body = response.json()
        assert "image_data" in body
        assert body["image_data"].startswith("data:image/png;base64,")

    def test_generate_empty_content_rejected(self, client, mock_s3):
        """Boş içerik 422 ile reddedilmeli."""
        response = client.post(
            "/api/v1/qr/generate",
            json={"content": "   ", "qr_type": "url"},
        )
        assert response.status_code == 422

    def test_generate_invalid_type_rejected(self, client, mock_s3):
        """Geçersiz tip 422 ile reddedilmeli."""
        response = client.post(
            "/api/v1/qr/generate",
            json={"content": "test", "qr_type": "invalid"},
        )
        assert response.status_code == 422


class TestV1HistoryEndpoint:
    """GET /api/v1/qr/history endpoint testleri."""

    def test_history_requires_auth(self, client, mock_s3):
        """/api/v1/qr/history token olmadan 401 döndürmeli."""
        response = client.get("/api/v1/qr/history")
        assert response.status_code == 401

    def test_history_empty_for_new_user(self, client, mock_s3):
        """Yeni kullanıcının geçmişi boş olmalı."""
        user = UserFactory.build()
        token = _register_and_login(client, user.email)
        response = client.get("/api/v1/qr/history", headers=_auth_header(token))
        assert response.status_code == 200
        assert response.json() == []

    def test_history_returns_created_qrs(self, client, mock_s3):
        """Oluşturulan QR'lar geçmişte görünmeli."""
        user = UserFactory.build()
        token = _register_and_login(client, user.email)
        headers = _auth_header(token)

        # Faker ile 3 farklı URL üret ve QR oluştur
        for i in range(3):
            factory_data = QRCodeFactory.build()
            client.post(
                "/api/v1/qr/generate",
                json={"content": f"https://test-{i}.example.com", "qr_type": "url"},
                headers=headers,
            )

        response = client.get("/api/v1/qr/history", headers=headers)
        assert response.status_code == 200
        assert len(response.json()) == 3

    def test_history_returns_newest_first(self, client, mock_s3):
        """Geçmiş en yeniden eskiye sıralı olmalı."""
        user = UserFactory.build()
        token = _register_and_login(client, user.email)
        headers = _auth_header(token)

        for url in ["https://first.com", "https://second.com", "https://third.com"]:
            client.post(
                "/api/v1/qr/generate",
                json={"content": url, "qr_type": "url"},
                headers=headers,
            )

        response = client.get("/api/v1/qr/history", headers=headers)
        items = response.json()
        # En son oluşturulan ilk sırada olmalı
        assert items[0]["content"] == "https://third.com"

    def test_history_isolated_between_users(self, client, mock_s3):
        """Farklı kullanıcıların geçmişleri birbirinden izole olmalı."""
        user1 = UserFactory.build()
        user2 = UserFactory.build()
        token1 = _register_and_login(client, user1.email)
        token2 = _register_and_login(client, user2.email)

        # User1 QR oluşturur
        client.post(
            "/api/v1/qr/generate",
            json={"content": "https://user1only.com", "qr_type": "url"},
            headers=_auth_header(token1),
        )

        # User2'nin geçmişi boş kalmalı
        resp = client.get("/api/v1/qr/history", headers=_auth_header(token2))
        assert resp.json() == []


class TestV1GetAndDeleteEndpoints:
    """GET /api/v1/qr/{id} ve DELETE /api/v1/qr/{id} testleri."""

    def test_get_qr_by_id_via_v1(self, client, mock_s3):
        """ID ile QR detayı /api/v1/qr/{id} üzerinden alınabilmeli."""
        user = UserFactory.build()
        token = _register_and_login(client, user.email)
        headers = _auth_header(token)

        create_resp = client.post(
            "/api/v1/qr/generate",
            json={"content": "https://getme.example.com", "qr_type": "url"},
            headers=headers,
        )
        qr_id = create_resp.json()["id"]

        response = client.get(f"/api/v1/qr/{qr_id}", headers=headers)
        assert response.status_code == 200
        assert response.json()["id"] == qr_id
        assert response.json()["content"] == "https://getme.example.com"

    def test_delete_qr_via_v1(self, client, mock_s3):
        """QR /api/v1/qr/{id} DELETE ile silinmeli."""
        user = UserFactory.build()
        token = _register_and_login(client, user.email)
        headers = _auth_header(token)

        create_resp = client.post(
            "/api/v1/qr/generate",
            json={"content": "https://deleteme.com", "qr_type": "url"},
            headers=headers,
        )
        qr_id = create_resp.json()["id"]

        del_resp = client.delete(f"/api/v1/qr/{qr_id}", headers=headers)
        assert del_resp.status_code == 204

        # Silindikten sonra 404 dönmeli
        get_resp = client.get(f"/api/v1/qr/{qr_id}", headers=headers)
        assert get_resp.status_code == 404

    def test_cross_user_access_forbidden_via_v1(self, client, mock_s3):
        """Başka kullanıcının QR'ına /api/v1 üzerinden erişim 404 ile engellenmeli."""
        user1 = UserFactory.build()
        user2 = UserFactory.build()
        token1 = _register_and_login(client, user1.email)
        token2 = _register_and_login(client, user2.email)

        create_resp = client.post(
            "/api/v1/qr/generate",
            json={"content": "https://private.com", "qr_type": "url"},
            headers=_auth_header(token1),
        )
        qr_id = create_resp.json()["id"]

        # user2 user1'in QR'ına erişemez
        resp = client.get(f"/api/v1/qr/{qr_id}", headers=_auth_header(token2))
        assert resp.status_code == 404
