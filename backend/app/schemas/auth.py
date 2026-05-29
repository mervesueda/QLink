"""
schemas/auth.py – Kimlik doğrulama Pydantic şemaları.

API katmanı ile iş mantığı arasındaki veri sözleşmesi.
ORM modellerinden bağımsızdır; sadece HTTP istek/yanıt formatını tanımlar.
"""

from pydantic import BaseModel, EmailStr, field_validator


class UserCreate(BaseModel):
    """POST /auth/register isteği"""
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Şifre en az 8 karakter olmalıdır")
        return v


class UserLogin(BaseModel):
    """POST /auth/login isteği"""
    email: EmailStr
    password: str


class Token(BaseModel):
    """Başarılı login yanıtı"""
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """Kullanıcı bilgisi yanıtı (şifre hash döndürülmez)"""
    id: str
    email: str

    model_config = {"from_attributes": True}
