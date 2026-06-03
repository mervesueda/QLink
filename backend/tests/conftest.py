"""
conftest.py – Pytest fixtures ve test altyapısı.

Bu dosya Pytest tarafından otomatik olarak yüklenir.
Testcontainers ile gerçek bir PostgreSQL container'ı başlatır;
böylece integration testler mock değil, gerçek DB üzerinde çalışır.

Fixture scoping:
  - postgres_container, test_engine → session scope (tüm test boyunca 1 kez başlar)
  - db_session → function scope (her test kendi transaction'ında çalışır)
  - client → function scope (her test temiz bir HTTP client alır)

ÖNEMLI: app.db.base modülü import edildiği anda module-level bir SQLAlchemy
engine oluşturur (settings.DATABASE_URL kullanarak). Bu nedenle testcontainers
container URL'sini os.environ'a yazmak, app modüllerini import etmeden ÖNCE
yapılmalıdır. postgres_container fixture'ı bu sorunu çözer.
"""

import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from testcontainers.postgres import PostgresContainer

# ── PostgreSQL container (session genelinde 1 kez başlatılır) ──────────────

@pytest.fixture(scope="session")
def postgres_container():
    """
    Testcontainers ile geçici bir PostgreSQL container başlatır.
    Container URL'si os.environ['DATABASE_URL']'e yazılır; böylece
    app modülleri import edilmeden önce doğru URL kullanılır.
    Test oturumu bitince container otomatik silinir.
    """
    with PostgresContainer("postgres:15-alpine") as pg:
        raw_url = pg.get_connection_url()
        # Testcontainers varsayılan olarak postgresql+psycopg2 dönebilir veya düz postgresql.
        db_url = raw_url.replace("postgresql+psycopg2://", "postgresql+psycopg://", 1)
        if db_url.startswith("postgresql://"):
            db_url = db_url.replace("postgresql://", "postgresql+psycopg://", 1)

        # App modülleri bu env'i okur — import öncesinde set edilmeli
        os.environ["DATABASE_URL"] = db_url
        yield pg


@pytest.fixture(scope="session")
def test_engine(postgres_container):
    """
    Test veritabanı için SQLAlchemy engine oluşturur.
    Tüm tablolar oluşturulur, session sonunda kaldırılır.

    postgres_container fixture'ı DATABASE_URL env'ini set ettiğinden
    burada aynı URL'yi tekrar türetiriz.
    """
    db_url = os.environ["DATABASE_URL"]
    engine = create_engine(
        db_url,
        echo=False,
        pool_pre_ping=True,  # bağlantı kesilmelerinde otomatik reconnect
    )

    # App modüllerini şimdi import ediyoruz; env ayarlandığı için doğru URL kullanılır
    from app.db.base import Base  # noqa: PLC0415
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


# ── DB session (her test için izole transaction) ───────────────────────────

@pytest.fixture
def db_session(test_engine):
    """
    Her test için yeni bir DB session açar.
    Test bitince rollback yaparak izolasyon sağlar.
    """
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestingSession()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


# ── FastAPI test client ────────────────────────────────────────────────────

@pytest.fixture
def client(db_session):
    """
    FastAPI'nin get_db dependency'sini test session'ıyla override eder.
    Böylece API istekleri gerçek test DB'sine gider.
    lifespan devre dışı bırakılır (LocalStack bağlantısı gerektirmez).
    """
    from app.db.base import get_db  # noqa: PLC0415
    from app.main import app  # noqa: PLC0415

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    # raise_server_exceptions=True → test hatalarını açık gösterir
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c

    app.dependency_overrides.clear()


# ── S3 mock (integration testler için) ────────────────────────────────────

@pytest.fixture
def mock_s3(monkeypatch):
    """
    S3 servisini monkeypatch ile mock'lar.
    Integration testlerde LocalStack'e gerçek bağlantı gerekmez.
    """
    def fake_upload(file_bytes: bytes, object_key: str, content_type: str = "image/png") -> str:
        return f"http://localhost:4566/qlink-qrcodes/{object_key}"

    def fake_delete(object_key: str) -> None:
        pass

    def fake_create_bucket() -> None:
        pass

    monkeypatch.setattr("app.services.s3_service.upload_to_s3", fake_upload)
    monkeypatch.setattr("app.services.s3_service.delete_from_s3", fake_delete)
    monkeypatch.setattr("app.services.s3_service.create_bucket_if_not_exists", fake_create_bucket)
    monkeypatch.setattr("app.api.qr.upload_to_s3", fake_upload)
    monkeypatch.setattr("app.api.qr.delete_from_s3", fake_delete)
