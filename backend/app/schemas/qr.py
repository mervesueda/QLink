"""
schemas/qr.py – QR kod Pydantic şemaları.

QRCreate: Kullanıcının gönderdiği içerik ve tip.
QRResponse: API'nin döndürdüğü QR verisi (S3 URL dahil).
"""

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, field_validator


class QRCreate(BaseModel):
    """POST /qr/create isteği"""

    # Encode edilecek içerik: URL, metin ya da e-posta adresi
    content: str
    # Şartnamede belirtilen üç tip
    qr_type: Literal["url", "text", "email"]

    @field_validator("content")
    @classmethod
    def content_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("İçerik boş olamaz")
        return v.strip()


class QRResponse(BaseModel):
    """GET /qr/list, GET /qr/{id} ve POST /qr/create yanıtı"""

    id: str
    content: str
    qr_type: str
    file_url: str
    file_format: str
    created_at: datetime
    user_id: Optional[str] = None
    # Base64 PNG verisi: browser doğrudan görüntüleyebilir (S3 URL'si erişilemez olsa bile)
    image_data: Optional[str] = None

    model_config = {"from_attributes": True}


class GuestQRResponse(BaseModel):
    """
    Misafir kullanıcı yanıtı.
    DB kaydı olmadığı için id ve user_id içermez.
    """

    file_url: str
    content: str
    qr_type: str
    file_format: str = "png"
    saved: bool = False  # Kullanıcıya "kaydedilmedi" bilgisini ilet
    # Base64 PNG verisi
    image_data: Optional[str] = None
