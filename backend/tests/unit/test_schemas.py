"""
unit/test_schemas.py – Pydantic şema doğrulama unit testleri.

QRCreate, QRResponse ve GuestQRResponse şemalarının
doğrulama kurallarını test eder.
DB veya HTTP bağlantısı gerektirmez.
"""

import pytest
from pydantic import ValidationError

from app.schemas.qr import GuestQRResponse, QRCreate, QRResponse


class TestQRCreate:
    """QRCreate Pydantic şeması testleri."""

    def test_valid_url_type(self):
        """Geçerli URL içeriği kabul edilmeli."""
        qr = QRCreate(content="https://example.com", qr_type="url")
        assert qr.content == "https://example.com"
        assert qr.qr_type == "url"

    def test_valid_text_type(self):
        """Geçerli metin içeriği kabul edilmeli."""
        qr = QRCreate(content="Merhaba Dünya", qr_type="text")
        assert qr.qr_type == "text"

    def test_valid_email_type(self):
        """Geçerli e-posta içeriği kabul edilmeli."""
        qr = QRCreate(content="test@example.com", qr_type="email")
        assert qr.qr_type == "email"

    def test_invalid_qr_type_rejected(self):
        """Geçersiz tip reddedilmeli."""
        with pytest.raises(ValidationError):
            QRCreate(content="test", qr_type="invalid_type")

    def test_empty_content_rejected(self):
        """Boş içerik reddedilmeli."""
        with pytest.raises(ValidationError):
            QRCreate(content="   ", qr_type="text")

    def test_content_is_stripped(self):
        """İçerik başındaki/sonundaki boşluklar temizlenmeli."""
        qr = QRCreate(content="  https://example.com  ", qr_type="url")
        assert qr.content == "https://example.com"

    def test_missing_content_raises(self):
        """İçerik alanı zorunlu olmalı."""
        with pytest.raises(ValidationError):
            QRCreate(qr_type="url")  # type: ignore

    def test_missing_qr_type_raises(self):
        """Tip alanı zorunlu olmalı."""
        with pytest.raises(ValidationError):
            QRCreate(content="hello")  # type: ignore


class TestGuestQRResponse:
    """GuestQRResponse şeması testleri."""

    def test_default_saved_is_false(self):
        """saved alanı varsayılan olarak False olmalı."""
        resp = GuestQRResponse(
            file_url="http://localhost:4566/bucket/test.png",
            content="https://example.com",
            qr_type="url",
        )
        assert resp.saved is False

    def test_default_format_is_png(self):
        """file_format alanı varsayılan olarak 'png' olmalı."""
        resp = GuestQRResponse(
            file_url="http://localhost:4566/bucket/test.png",
            content="test",
            qr_type="text",
        )
        assert resp.file_format == "png"

    def test_image_data_optional(self):
        """image_data alanı opsiyonel olmalı."""
        resp = GuestQRResponse(
            file_url="http://localhost/test.png",
            content="hello",
            qr_type="text",
        )
        assert resp.image_data is None


class TestQRCreateAllTypes:
    """QRCreate tüm geçerli tipler için parameterized testler."""

    @pytest.mark.parametrize("qr_type", ["url", "text", "email"])
    def test_all_valid_types_accepted(self, qr_type):
        """Tüm geçerli tipler kabul edilmeli."""
        qr = QRCreate(content="some content", qr_type=qr_type)
        assert qr.qr_type == qr_type

    @pytest.mark.parametrize("invalid_type", ["qrcode", "sms", "phone", "image", ""])
    def test_invalid_types_rejected(self, invalid_type):
        """Geçersiz tipler reddedilmeli."""
        with pytest.raises(ValidationError):
            QRCreate(content="test", qr_type=invalid_type)
