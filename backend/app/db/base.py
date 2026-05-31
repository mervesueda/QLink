"""
base.py – SQLAlchemy veritabanı motoru ve session yönetimi.

- engine: Veritabanına bağlantı havuzu
- SessionLocal: Her istek için ayrı bir session oluşturur
- Base: Tüm ORM modellerinin miras aldığı temel sınıf
- get_db: FastAPI dependency injection için generator

NOT: engine lazy olarak oluşturulur (get_engine() çağrısında).
Bu sayede test ortamında DATABASE_URL env değişkeni set edildikten
sonra modül import edildiğinde doğru URL kullanılır.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

_engine = None
_SessionLocal = None


def get_engine():
    """Engine'i ilk çağrıda oluşturur (lazy init)."""
    global _engine
    if _engine is None:
        # settings.DATABASE_URL yerine os.environ'ı önceliklendiriyoruz;
        # böylece test conftest.py DATABASE_URL'yi set ettiğinde bu fonksiyon
        # doğru URL'yi kullanır.
        import os
        db_url = os.environ.get("DATABASE_URL", settings.DATABASE_URL)
        _engine = create_engine(
            db_url,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,  # Bağlantı sağlıklı mı kontrol et
        )
    return _engine


def get_session_local():
    """SessionLocal factory'sini ilk çağrıda oluşturur."""
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return _SessionLocal


# Geriye dönük uyumluluk: eski importlar için alias'lar
# (main.py: from app.db.base import Base, engine)
@property
def _engine_proxy():
    return get_engine()


engine = get_engine  # callable; main.py'deki Base.metadata.create_all(bind=engine) çalışmaz


class Base(DeclarativeBase):
    """Tüm ORM modelleri bu sınıftan miras alır."""
    pass


def get_db():
    """
    FastAPI dependency injection için DB session generator.
    Her HTTP isteği kendi session'ını alır, istek bittikten sonra kapatılır.
    """
    db = get_session_local()()
    try:
        yield db
    finally:
        db.close()

