"""
security.py – Kimlik doğrulama altyapısı.

- Şifre hash/doğrulama: passlib + bcrypt
- JWT üretme/çözme: python-jose
- FastAPI dependency: get_current_user (zorunlu) ve get_current_user_optional (misafir izin verilir)
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.base import get_db

# bcrypt şifre hash bağlamı
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Bearer token okuyucu (Authorization: Bearer <token>)
bearer_scheme = HTTPBearer(auto_error=False)


def hash_password(plain: str) -> str:
    """Düz metin şifreyi bcrypt ile hashler."""
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Gelen şifre ile hash'i karşılaştırır."""
    return pwd_context.verify(plain, hashed)


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
    """
    from app.db.models import User

    if not credentials:
        return None

    user_id = decode_token(credentials.credentials)
    if not user_id:
        return None

    return db.query(User).filter(User.id == user_id).first()
