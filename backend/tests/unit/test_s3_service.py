"""
unit/test_s3_service.py – S3 servis katmanı unit testleri.

boto3 çağrıları moto[s3] ile AWS'ye bağlanmadan mock'lanır.
Gerçek S3 veya LocalStack bağlantısı gerekmez.
"""

import os

import boto3
import pytest
from moto import mock_aws

from app.core.config import settings


# ── moto mock: gerçek AWS yerine bellek içi sahte S3 ─────────────────────────

@pytest.fixture(autouse=True)
def aws_env(monkeypatch):
    """moto'nun çalışması için sahte AWS kimlik bilgileri set eder."""
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "test")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "test")
    monkeypatch.setenv("AWS_ENDPOINT_URL", "")  # moto kendi intercept eder


@pytest.fixture
def s3_bucket():
    """Sahte bir S3 bucket'ı oluşturur ve test sonunda temizler."""
    with mock_aws():
        client = boto3.client("s3", region_name="us-east-1")
        client.create_bucket(Bucket=settings.AWS_BUCKET_NAME)
        yield client


class TestUploadToS3:
    """upload_to_s3 fonksiyonu unit testleri."""

    def test_upload_returns_url(self, s3_bucket, monkeypatch):
        """Yükleme başarılı olduğunda URL döndürmeli."""
        monkeypatch.setenv("AWS_ENDPOINT_URL", "http://localhost:4566")
        from app.services.s3_service import upload_to_s3
        url = upload_to_s3(b"fake-png-data", "test_key.png")
        assert "test_key.png" in url

    def test_upload_stores_object(self, s3_bucket, monkeypatch):
        """Yüklenen nesne S3'te bulunabilmeli."""
        monkeypatch.setenv("AWS_ENDPOINT_URL", "")
        with mock_aws():
            client = boto3.client("s3", region_name="us-east-1")
            client.create_bucket(Bucket=settings.AWS_BUCKET_NAME)

            from importlib import reload
            import app.services.s3_service as s3_mod
            original = s3_mod._get_client
            s3_mod._get_client = lambda: client

            try:
                s3_mod.upload_to_s3(b"png-bytes", "stored_key.png")
                response = client.get_object(Bucket=settings.AWS_BUCKET_NAME, Key="stored_key.png")
                assert response["Body"].read() == b"png-bytes"
            finally:
                s3_mod._get_client = original


class TestDeleteFromS3:
    """delete_from_s3 fonksiyonu unit testleri."""

    def test_delete_nonexistent_key_does_not_raise(self, monkeypatch):
        """Olmayan key silinmeye çalışıldığında exception fırlatmamalı."""
        with mock_aws():
            client = boto3.client("s3", region_name="us-east-1")
            client.create_bucket(Bucket=settings.AWS_BUCKET_NAME)

            from app.services.s3_service import delete_from_s3
            import app.services.s3_service as s3_mod
            s3_mod._get_client = lambda: client

            # Exception fırlatmadan çalışmalı
            delete_from_s3("nonexistent_key.png")

    def test_delete_existing_key(self, monkeypatch):
        """Mevcut key silinmeli."""
        with mock_aws():
            client = boto3.client("s3", region_name="us-east-1")
            client.create_bucket(Bucket=settings.AWS_BUCKET_NAME)
            client.put_object(Bucket=settings.AWS_BUCKET_NAME, Key="to_delete.png", Body=b"data")

            from app.services.s3_service import delete_from_s3
            import app.services.s3_service as s3_mod
            s3_mod._get_client = lambda: client

            delete_from_s3("to_delete.png")

            # Nesne silinmiş olmalı
            import botocore.exceptions
            with pytest.raises(botocore.exceptions.ClientError) as exc_info:
                client.get_object(Bucket=settings.AWS_BUCKET_NAME, Key="to_delete.png")
            assert exc_info.value.response["Error"]["Code"] == "NoSuchKey"


class TestCreateBucketIfNotExists:
    """create_bucket_if_not_exists fonksiyonu unit testleri."""

    def test_creates_bucket_when_missing(self, monkeypatch):
        """Bucket yokken oluşturulmalı."""
        with mock_aws():
            client = boto3.client("s3", region_name="us-east-1")

            from app.services.s3_service import create_bucket_if_not_exists
            import app.services.s3_service as s3_mod
            s3_mod._get_client = lambda: client

            create_bucket_if_not_exists()
            buckets = [b["Name"] for b in client.list_buckets()["Buckets"]]
            assert settings.AWS_BUCKET_NAME in buckets

    def test_does_not_raise_when_bucket_exists(self, monkeypatch):
        """Bucket zaten varken exception fırlatmamalı."""
        with mock_aws():
            client = boto3.client("s3", region_name="us-east-1")
            client.create_bucket(Bucket=settings.AWS_BUCKET_NAME)

            from app.services.s3_service import create_bucket_if_not_exists
            import app.services.s3_service as s3_mod
            s3_mod._get_client = lambda: client

            # İkinci kez çağrıldığında hata fırlatmamalı
            create_bucket_if_not_exists()
