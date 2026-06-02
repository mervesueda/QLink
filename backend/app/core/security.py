"""
security.py – Kimlik doğrulama altyapısı.

- Şifre hash/doğrulama: bcrypt (doğrudan, passlib bypass)
- JWT üretme/çözme: python-jose
- FastAPI dependency: get_current_user (zorunlu) ve get_current_user_optional (misafir izin verilir)

 NOT: passlib 1.7.4, bcrypt>=4.0 ile uyumsuz (ValueError: password cannot be longer
 than 72 bytes). Bu yüzden bcrypt doğrudan kullanılmaktadır. Şifre, bcrypt'e
 verilmeden önce SHA-256 ile hash'lenip base64'e çevrilerek 72-byte limitinin
 altına düşürülür. Bu teknik Stanford'un password hashing önerisiyle uyumludur.
"""

import base64
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.base import get_db

# Bearer token okuyucu (Authorization: Bearer <token>)
bearer_scheme = HTTPBearer(auto_error=False)


def _prepare_password(plain: str) -> bytes:
    """
    Şifreyi bcrypt'e vermeden önce SHA-256 + base64 ile 64 byte'a indirir.
    Bu sayede bcrypt'in 72-byte sınırı aşılmaz ve tüm şifre entropisi korunur.
    """
    digest = hashlib.sha256(plain.encode("utf-8")).digest()
    return base64.b64encode(digest)  # her zaman 44 byte (< 72)


def hash_password(plain: str) -> str:
    """Düz metin şifreyi bcrypt ile hashler."""
    prepared = _prepare_password(plain)
    hashed = bcrypt.hashpw(prepared, bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Gelen şifre ile hash'i karşılaştırır."""
    prepared = _prepare_password(plain)
    return bcrypt.checkpw(prepared, hashed.encode("utf-8"))


def create_access_token(data: dict) -> str:
    """
    JWT access token üretir.
    data içindeki 'sub' alanı kullanıcı ID'si olmalıdır.
    """
    payload = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload["exp"] = expire
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> Optional[str]:
    """
    JWT token'ı çözer ve user_id'yi döner.
    Geçersiz/süresi dolmuş token için None döner.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: Session = Depends(get_db),
):
    """
    Zorunlu auth dependency.
    Token geçersizse 401 döner.
    Auth gerektiren endpoint'lerde kullanılır.
    """
    from app.db.models import User  # circular import önlemek için burada import

    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token gerekli")

    user_id = decode_token(credentials.credentials)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Geçersiz token")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Kullanıcı bulunamadı")

    return user


def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: Session = Depends(get_db),
):
    """
    Opsiyonel auth dependency.
    Token yoksa None döner, varsa doğrular.
    Misafir kullanıcıların QR oluşturabilmesi için kullanılır.
    Gelen token geçersiz veya süresi dolmuşsa 401 döner (silence bypass'ı önler).
    """
    from app.db.models import User

    if not credentials:
        return None

    user_id = decode_token(credentials.credentials)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Geçersiz veya süresi dolmuş token",
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Kullanıcı bulunamadı",
        )

    return user
