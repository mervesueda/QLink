"""
conftest.py – Pytest fixtures ve test altyapısı.

Bu dosya Pytest tarafından otomatik olarak yüklenir.
Testcontainers ile gerçek bir PostgreSQL container'ı başlatır;
böylece integration testler mock değil, gerçek DB üzerinde çalışır.

Fixture scoping:
  - postgres_container, test_engine → session scope (tüm test boyunca 1 kez başlar)
  - db_session → function scope (her test kendi transaction'ında çalışır)
  - client → function scope (her test temiz bir HTTP client alır)
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from testcontainers.postgres import PostgresContainer

from app.db.base import Base, get_db
from app.main import app


# ── PostgreSQL container (session genelinde 1 kez başlatılır) ──────────────

@pytest.fixture(scope="session")
def postgres_container():
    """
    Testcontainers ile geçici bir PostgreSQL container başlatır.
    Test oturumu bitince container otomatik silinir.
    """
    with PostgresContainer("postgres:15-alpine") as pg:
        yield pg


@pytest.fixture(scope="session")
def test_engine(postgres_container):
    """
    Test veritabanı için SQLAlchemy engine oluşturur.
    Tüm tablolar oluşturulur, session sonunda kaldırılır.
    """
    url = postgres_container.get_connection_url()
    engine = create_engine(url, echo=False)
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
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app, raise_server_exceptions=True) as c:
        yield c

    app.dependency_overrides.clear()


# ── S3 mock (unit testler için) ────────────────────────────────────────────

@pytest.fixture
def mock_s3(monkeypatch):
    """
    S3 servisini monkeypatch ile mock'lar.
    Unit testlerde LocalStack'e gerçek bağlantı gerekmez.
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
