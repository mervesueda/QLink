"""
api/qr.py – QR kod yönetim endpoint'leri.

POST   /qr/create   → QR oluştur (misafir + kayıtlı)
GET    /qr/list     → Kullanıcının QR listesi (auth zorunlu)
GET    /qr/{id}     → Tek QR detayı (auth zorunlu)
DELETE /qr/{id}     → QR sil (auth zorunlu)

Misafir kullanıcılar QR oluşturabilir fakat DB'ye kaydedilmez.
"""

import base64
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.security import get_current_user, get_current_user_optional
from app.db.base import get_db
from app.db.models import QRCode, User
from app.schemas.qr import GuestQRResponse, QRCreate, QRResponse
from app.services.qr_service import generate_qr_png
from app.services.s3_service import delete_from_s3, upload_to_s3

router = APIRouter()


def _png_to_data_url(png_bytes: bytes) -> str:
    """PNG bytes'ı data URL'e çevirir. Browser doğrudan render edebilir."""
    b64 = base64.b64encode(png_bytes).decode("utf-8")
    return f"data:image/png;base64,{b64}"


@router.post(
    "/create",
    summary="QR kod oluştur",
    status_code=status.HTTP_201_CREATED,
)
@router.post(
    "/generate",
    summary="QR kod oluştur (v1 alias)",
    status_code=status.HTTP_201_CREATED,
    include_in_schema=True,
)
def create_qr(
    qr_data: QRCreate,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    """
    PNG formatında QR kod üretir ve LocalStack S3'e yükler.
    Yanıtta hem S3 file_url hem de base64 image_data döner.
    - Giriş yapmış kullanıcı: DB'ye kaydeder, QRResponse döner.
    - Misafir kullanıcı: sadece S3'e yükler, GuestQRResponse döner.
    """
    # 1. QR kodu PNG olarak üret
    png_bytes = generate_qr_png(qr_data.content)

    # 2. Base64 data URL (browser erişimini garanti eder, S3'ten bağımsız)
    image_data = _png_to_data_url(png_bytes)

    # 3. Benzersiz bir dosya adı oluştur
    object_key = f"qr_{uuid.uuid4().hex}.png"

    # 4. S3'e yükle (başarısız olsa bile devam et; image_data zaten mevcut)
    try:
        file_url = upload_to_s3(png_bytes, object_key)
    except Exception:
        # LocalStack henüz hazır değilse image_data ile devam et
        file_url = f"/qr/image/{object_key}"  # Fallback: backend proxy

    # 5. Giriş yapmış kullanıcıysa DB'ye kaydet
    if current_user:
        qr_code = QRCode(
            user_id=current_user.id,
            content=qr_data.content,
            qr_type=qr_data.qr_type,
            file_url=file_url,
            file_format="png",
        )
        db.add(qr_code)
        db.commit()
        db.refresh(qr_code)

        return QRResponse(
            id=str(qr_code.id),
            content=qr_code.content,
            qr_type=qr_code.qr_type,
            file_url=qr_code.file_url,
            file_format=qr_code.file_format,
            created_at=qr_code.created_at,
            user_id=str(qr_code.user_id),
            image_data=image_data,
        )

    # Misafir: DB'ye kaydetme, sadece URL döndür
    return GuestQRResponse(
        file_url=file_url,
        content=qr_data.content,
        qr_type=qr_data.qr_type,
        saved=False,
        image_data=image_data,
    )


@router.get(
    "/list",
    response_model=list[QRResponse],
    summary="QR listesini getir (auth zorunlu)",
)
@router.get(
    "/history",
    response_model=list[QRResponse],
    summary="QR geçmişini getir (v1 alias)",
    include_in_schema=True,
)
def list_qr(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Giriş yapmış kullanıcının tüm QR kodlarını döner, en yeniden eskiye sıralar."""
    qr_codes = (
        db.query(QRCode)
        .filter(QRCode.user_id == current_user.id)
        .order_by(QRCode.created_at.desc())
        .all()
    )
    return [
        QRResponse(
            id=str(qr.id),
            content=qr.content,
            qr_type=qr.qr_type,
            file_url=qr.file_url,
            file_format=qr.file_format,
            created_at=qr.created_at,
            user_id=str(qr.user_id),
        )
        for qr in qr_codes
    ]


@router.get(
    "/{qr_id}/image",
    summary="QR görselini doğrudan sun (auth zorunlu)",
    response_class=Response,
)
def get_qr_image(
    qr_id: str,
    download: bool = Query(default=False, description="True ise tarayıcı dosyayı indirir"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    QR kodunu PNG olarak yeniden üretip doğrudan HTTP yanıtı olarak döner.
    Böylece tarayıcı LocalStack S3 URL'sine erişmek zorunda kalmaz.
    ?download=true → Content-Disposition: attachment → tarayıcı indirir.
    """
    qr_code = (
        db.query(QRCode)
        .filter(QRCode.id == qr_id, QRCode.user_id == current_user.id)
        .first()
    )
    if not qr_code:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="QR bulunamadı")

    png_bytes = generate_qr_png(qr_code.content)
    disposition = f'attachment; filename="qlink-{qr_id}.png"' if download else "inline"
    return Response(
        content=png_bytes,
        media_type="image/png",
        headers={"Content-Disposition": disposition},
    )


@router.get(
    "/{qr_id}",
    response_model=QRResponse,
    summary="Tek QR detayı (auth zorunlu)",
)
def get_qr(
    qr_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Belirli bir QR kodun detayını döner.
    Başka kullanıcının QR'ına erişim 404 ile engellenir.
    """
    qr_code = (
        db.query(QRCode)
        .filter(QRCode.id == qr_id, QRCode.user_id == current_user.id)
        .first()
    )
    if not qr_code:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="QR bulunamadı")

    return QRResponse(
        id=str(qr_code.id),
        content=qr_code.content,
        qr_type=qr_code.qr_type,
        file_url=qr_code.file_url,
        file_format=qr_code.file_format,
        created_at=qr_code.created_at,
        user_id=str(qr_code.user_id),
    )


@router.delete(
    "/{qr_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="QR sil (auth zorunlu)",
)
def delete_qr(
    qr_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    QR'ı hem veritabanından hem S3'ten siler.
    Başka kullanıcının QR'ı 404 ile engellenir.
    """
    qr_code = (
        db.query(QRCode)
        .filter(QRCode.id == qr_id, QRCode.user_id == current_user.id)
        .first()
    )
    if not qr_code:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="QR bulunamadı")

    # S3'ten dosyayı temizle
    object_key = qr_code.file_url.split("/")[-1]
    delete_from_s3(object_key)

    db.delete(qr_code)
    db.commit()
