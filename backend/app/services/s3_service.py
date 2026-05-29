"""
services/s3_service.py – LocalStack S3 entegrasyonu.

boto3 kullanarak LocalStack üzerindeki S3'e dosya yükler.
URL formatı: http://<endpoint>/<bucket>/<key>
Bu URL misafir ve kayıtlı kullanıcılara döndürülür.
"""

import boto3
from botocore.exceptions import ClientError

from app.core.config import settings


def _get_client():
    """
    boto3 S3 client oluşturur.
    LocalStack için endpoint_url zorunludur.
    """
    return boto3.client(
        "s3",
        endpoint_url=settings.AWS_ENDPOINT_URL,
        region_name=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )


def create_bucket_if_not_exists() -> None:
    """
    Uygulama başlarken çağrılır.
    Bucket yoksa oluşturur, varsa sessizce geçer.
    """
    client = _get_client()
    try:
        client.head_bucket(Bucket=settings.AWS_BUCKET_NAME)
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code in ("404", "NoSuchBucket"):
            client.create_bucket(Bucket=settings.AWS_BUCKET_NAME)
            # Bucket'ı herkese açık yap (LocalStack'te gerekli)
            client.put_bucket_acl(Bucket=settings.AWS_BUCKET_NAME, ACL="public-read")


def upload_to_s3(file_bytes: bytes, object_key: str, content_type: str = "image/png") -> str:
    """
    Dosyayı S3'e yükler ve public URL döner.

    Args:
        file_bytes: Yüklenecek dosya içeriği
        object_key: S3'teki dosya adı (örn: "qr_abc123.png")
        content_type: MIME tipi

    Returns:
        Dosyanın public URL'i
    """
    client = _get_client()
    client.put_object(
        Bucket=settings.AWS_BUCKET_NAME,
        Key=object_key,
        Body=file_bytes,
        ContentType=content_type,
        ACL="public-read",  # Herkesin okuyabilmesi için
    )
    # LocalStack public URL formatı
    return f"{settings.AWS_ENDPOINT_URL}/{settings.AWS_BUCKET_NAME}/{object_key}"


def delete_from_s3(object_key: str) -> None:
    """
    QR silindiğinde S3'teki dosyayı da temizler.
    """
    client = _get_client()
    try:
        client.delete_object(Bucket=settings.AWS_BUCKET_NAME, Key=object_key)
    except ClientError:
        # Dosya zaten yoksa sessizce geç
        pass
