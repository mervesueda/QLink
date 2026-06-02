"""
integration/test_qr_image_flow.py – QR görsel indirme ve önizleme akış testleri.

Önceki testlerin yakalayamadığı senaryolar:
1. listQR endpoint'inin image_data döndürüp döndürmediğinden bağımsız olarak,
   resimlerin /qr/{id}/image üzerinden doğru alınıp alınmadığı.
2. Download URL'inin Content-Disposition header'ını doğru ayarlayıp ayarlamadığı.
"""

from io import BytesIO

from PIL import Image


def _register_and_login(client, email: str, password: str = "Secure123!") -> str:
    """Yardımcı: kullanıcı oluştur ve JWT token döndür."""
    client.post("/auth/register", json={"email": email, "password": password})
    resp = client.post("/auth/login", json={"email": email, "password": password})
    return resp.json()["access_token"]

def _auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}

class TestQRImageFlow:
    """QR Görsel ve İndirme Akış Testleri."""

    def test_qr_image_endpoint_returns_valid_png(self, client, mock_s3):
        """Oluşturulan bir QR'ın image endpoint'inden geçerli bir PNG döndüğünü doğrula."""
        token = _register_and_login(client, "imageflow@example.com")

        # 1. QR oluştur
        create_resp = client.post(
            "/qr/create",
            json={"content": "https://qlink.com/test", "qr_type": "url"},
            headers=_auth_header(token),
        )
        assert create_resp.status_code == 201
        qr_id = create_resp.json()["id"]

        # 2. Image endpoint'ini çağır
        img_resp = client.get(f"/qr/{qr_id}/image", headers=_auth_header(token))
        assert img_resp.status_code == 200
        assert img_resp.headers["content-type"] == "image/png"

        # 3. Geçerli bir PNG mi kontrol et
        img = Image.open(BytesIO(img_resp.content))
        assert img.format == "PNG"

    def test_qr_image_download_mode(self, client, mock_s3):
        """?download=true parametresinin attachment header'ı eklediğini doğrula."""
        token = _register_and_login(client, "downloadflow@example.com")

        create_resp = client.post(
            "/qr/create",
            json={"content": "https://qlink.com/download", "qr_type": "url"},
            headers=_auth_header(token),
        )
        qr_id = create_resp.json()["id"]

        # Download flag ile çağır
        img_resp = client.get(f"/qr/{qr_id}/image?download=true", headers=_auth_header(token))
        assert img_resp.status_code == 200
        assert "attachment" in img_resp.headers["content-disposition"]
        assert f"filename=\"qlink-{qr_id}.png\"" in img_resp.headers["content-disposition"]

    def test_qr_image_requires_auth(self, client, mock_s3):
        """Image endpoint'inin token gerektirdiğini doğrula."""
        token = _register_and_login(client, "authflow@example.com")

        create_resp = client.post(
            "/qr/create",
            json={"content": "https://qlink.com/auth", "qr_type": "url"},
            headers=_auth_header(token),
        )
        qr_id = create_resp.json()["id"]

        # Token olmadan erişmeye çalış
        img_resp = client.get(f"/qr/{qr_id}/image")
        assert img_resp.status_code == 401

    def test_qr_image_other_user_denied(self, client, mock_s3):
        """Başka bir kullanıcının QR görseline erişim engellenmeli."""
        token1 = _register_and_login(client, "owner_image@example.com")
        token2 = _register_and_login(client, "hacker_image@example.com")

        create_resp = client.post(
            "/qr/create",
            json={"content": "https://qlink.com/private", "qr_type": "url"},
            headers=_auth_header(token1),
        )
        qr_id = create_resp.json()["id"]

        # Hacker token'ıyla erişmeye çalış
        img_resp = client.get(f"/qr/{qr_id}/image", headers=_auth_header(token2))
        assert img_resp.status_code == 404

    def test_list_then_image_flow(self, client, mock_s3):
        """Frontend'in MyQRs sayfasındaki akışı simüle et: listele ve her resme istek at."""
        token = _register_and_login(client, "list_image_flow@example.com")

        # İki farklı QR oluştur
        client.post("/qr/create", json={"content": "URL1", "qr_type": "text"}, headers=_auth_header(token))
        client.post("/qr/create", json={"content": "URL2", "qr_type": "text"}, headers=_auth_header(token))

        # Listeyi al
        list_resp = client.get("/qr/list", headers=_auth_header(token))
        assert list_resp.status_code == 200
        items = list_resp.json()
        assert len(items) == 2

        # Listede gelen ID'lerle image endpoint'e eriş
        for item in items:
            img_resp = client.get(f"/qr/{item['id']}/image", headers=_auth_header(token))
            assert img_resp.status_code == 200
            assert img_resp.headers["content-type"] == "image/png"

    def test_invalid_token_rejected_on_optional_auth(self, client, mock_s3):
        """Geçersiz bir token gönderildiğinde opsiyonel auth kullanan endpoint'in 401 döndürdüğünü doğrula."""
        response = client.post(
            "/qr/create",
            json={"content": "https://qlink.com/invalid-token", "qr_type": "url"},
            headers={"Authorization": "Bearer invalid_or_expired_token_here"},
        )
        assert response.status_code == 401

