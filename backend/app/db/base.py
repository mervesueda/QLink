"""
base.py – SQLAlchemy veritabanı motoru ve session yönetimi.

- engine: Veritabanına bağlantı havuzu
- SessionLocal: Her istek için ayrı bir session oluşturur
- Base: Tüm ORM modellerinin miras aldığı temel sınıf
- get_db: FastAPI dependency injection için generator
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

# Bağlantı havuzu boyutunu sınırla: küçük uygulama için yeterli
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,  # Bağlantı sağlıklı mı kontrol et
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Tüm ORM modelleri bu sınıftan miras alır."""
    pass


def get_db():
    """
    FastAPI dependency injection için DB session generator.
    Her HTTP isteği kendi session'ını alır, istek bittikten sonra kapatılır.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
