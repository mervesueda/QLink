"""
models.py – SQLAlchemy ORM modelleri.

Şartnamede tanımlanan iki entity:
  1. User      – Kullanıcı hesabı
  2. QRCode    – Oluşturulan QR kodları

İlişki: Bir User'ın birden fazla QRCode'u olabilir (one-to-many).
user_id nullable: misafir kullanıcıların QR'ları DB'ye kaydedilmez,
ancak gelecekte admin görüntüsü için nullable bıraktık.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Cascade: kullanıcı silinince QR'ları da silinir
    qr_codes: Mapped[list["QRCode"]] = relationship(
        "QRCode", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email}>"


class QRCode(Base):
    __tablename__ = "qr_codes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    # Misafir QR'lar DB'ye kaydedilmez; kayıtlı kullanıcılar için zorunlu
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    # QR'ın encode ettiği içerik (URL, metin, e-posta)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    # İçerik tipi: 'url' | 'text' | 'email'
    qr_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # S3'teki public dosya URL'i
    file_url: Mapped[str] = mapped_column(Text, nullable=False)
    # Şimdilik sadece 'png' destekleniyor
    file_format: Mapped[str] = mapped_column(String(10), default="png")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user: Mapped["User"] = relationship("User", back_populates="qr_codes")

    def __repr__(self) -> str:
        return f"<QRCode id={self.id} type={self.qr_type}>"
