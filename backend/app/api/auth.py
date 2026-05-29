"""
api/auth.py – Kimlik doğrulama endpoint'leri.

POST /auth/register  → Yeni kullanıcı kaydı
POST /auth/login     → JWT token alma
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.db.base import get_db
from app.db.models import User
from app.schemas.auth import Token, UserCreate, UserLogin, UserResponse

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Yeni kullanıcı kaydı",
)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    E-posta ve şifreyle yeni hesap oluşturur.
    Aynı e-posta zaten kayıtlıysa 400 döner.
    Şifre bcrypt ile hashlenip saklanır; düz metin asla kaydedilmez.
    """
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu e-posta adresi zaten kayıtlı",
        )

    user = User(
        email=user_data.email,
        password_hash=hash_password(user_data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return UserResponse(id=str(user.id), email=user.email)


@router.post(
    "/login",
    response_model=Token,
    summary="Giriş yap ve JWT al",
)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    E-posta + şifre doğrular ve JWT access token döner.
    Yanlış kimlik bilgisi durumunda 401 döner (hangi alanın yanlış olduğu açıklanmaz).
    """
    user = db.query(User).filter(User.email == credentials.email).first()

    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-posta veya şifre hatalı",
        )

    token = create_access_token({"sub": str(user.id)})
    return Token(access_token=token)
