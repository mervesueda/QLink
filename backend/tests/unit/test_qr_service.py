"""
unit/test_qr_service.py – QR üretim servisi unit testleri.

generate_qr_png fonksiyonunun davranışını test eder.
S3 veya veritabanı bağlantısı gerekmez.
"""

import io

import pytest
from PIL import Image

from app.services.qr_service import generate_qr_png


class TestGenerateQRPng:
    """generate_qr_png fonksiyonu için unit testler."""

    def test_returns_bytes(self):
        """Fonksiyon bytes döndürmeli."""
        result = generate_qr_png("https://example.com")
        assert isinstance(result, bytes)

    def test_output_is_valid_png(self):
        """Dönen bytes geçerli bir PNG resmi olmalı."""
        result = generate_qr_png("https://example.com")
        img = Image.open(io.BytesIO(result))
        assert img.format == "PNG"

    def test_non_empty_content(self):
        """Farklı içerikler farklı boyutlarda QR üretmeli (her biri geçerli)."""
        short_qr = generate_qr_png("hi")
        long_qr = generate_qr_png("https://very-long-url.example.com/" + "a" * 100)
        # Her iki çıktı da geçerli PNG olmalı
        assert Image.open(io.BytesIO(short_qr)).format == "PNG"
        assert Image.open(io.BytesIO(long_qr)).format == "PNG"

    def test_url_content(self):
        """URL içeriği QR'a encode edilebilmeli."""
        result = generate_qr_png("https://qlink.example.com")
        assert len(result) > 0

    def test_email_content(self):
        """E-posta adresi QR'a encode edilebilmeli."""
        result = generate_qr_png("mailto:test@example.com")
        assert len(result) > 0

    def test_text_content(self):
        """Düz metin QR'a encode edilebilmeli."""
        result = generate_qr_png("Merhaba Dünya")
        assert len(result) > 0

    def test_image_dimensions_are_square(self):
        """QR kodları kare olmalı."""
        result = generate_qr_png("test")
        img = Image.open(io.BytesIO(result))
        assert img.width == img.height
