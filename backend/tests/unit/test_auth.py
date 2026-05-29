"""
unit/test_auth.py – Güvenlik katmanı unit testleri.

Veritabanı veya HTTP bağlantısı gerektirmez.
Sadece security.py modülündeki fonksiyonları test eder.
"""

import pytest
from jose import jwt

from app.core.config import settings
from app.core.security import (
    create_access_token,
    decode_token,
    hash_password,
    verify_password,
)


class TestPasswordHashing:
    """Şifre hash ve doğrulama testleri."""

    def test_hash_returns_string(self):
        """Hash fonksiyonu string döndürmeli."""
        result = hash_password("mypassword")
        assert isinstance(result, str)

    def test_hash_is_not_plaintext(self):
        """Hash, düz metinden farklı olmalı."""
        plain = "mypassword"
        assert hash_password(plain) != plain

    def test_same_password_different_hashes(self):
        """bcrypt her seferinde farklı salt kullandığından hash'ler farklı olur."""
        h1 = hash_password("same")
        h2 = hash_password("same")
        assert h1 != h2

    def test_verify_correct_password(self):
        """Doğru şifre doğrulanabilmeli."""
        hashed = hash_password("correct")
        assert verify_password("correct", hashed) is True

    def test_verify_wrong_password(self):
        """Yanlış şifre reddedilmeli."""
        hashed = hash_password("correct")
        assert verify_password("wrong", hashed) is False


class TestJWT:
    """JWT üretme ve çözme testleri."""

    def test_create_token_returns_string(self):
        """Token string olmalı."""
        token = create_access_token({"sub": "user-123"})
        assert isinstance(token, str)

    def test_token_contains_subject(self):
        """Token içindeki sub alanı doğru olmalı."""
        token = create_access_token({"sub": "user-abc"})
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert payload["sub"] == "user-abc"

    def test_token_has_expiry(self):
        """Token'ın geçerlilik süresi olmalı."""
        token = create_access_token({"sub": "user-123"})
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert "exp" in payload

    def test_decode_valid_token(self):
        """Geçerli token doğru user_id döndürmeli."""
        token = create_access_token({"sub": "user-xyz"})
        result = decode_token(token)
        assert result == "user-xyz"

    def test_decode_invalid_token(self):
        """Bozuk token None döndürmeli."""
        result = decode_token("not.a.valid.token")
        assert result is None

    def test_decode_tampered_token(self):
        """İmzası değiştirilmiş token reddedilmeli."""
        token = create_access_token({"sub": "user-123"})
        tampered = token[:-5] + "XXXXX"
        result = decode_token(tampered)
        assert result is None
