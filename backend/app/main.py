"""
main.py – FastAPI uygulama giriş noktası.

Uygulama başladığında (lifespan):
  1. Veritabanı tabloları oluşturulur
  2. S3 bucket var mı kontrol edilir, yoksa oluşturulur
  3. Prometheus instrumentasyonu devreye girer
  4. OpenTelemetry tracing başlatılır (OTEL_ENABLED=true ise)

Route'lar prefix'li olarak eklenir:
  /auth/... → auth router
  /qr/...   → qr router
  /metrics  → Prometheus scrape endpoint
  /health   → Liveness probe (K8s için)
  /docs     → Swagger UI (FastAPI otomatik üretir)
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth as auth_router
from app.api import qr as qr_router
from app.core.config import settings
from app.core.metrics import setup_metrics
from app.core.telemetry import setup_tracing
from app.db.base import Base, engine
from app.services.s3_service import create_bucket_if_not_exists


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Uygulama açılış/kapanış yaşam döngüsü."""
    # --- Başlangıç ---
    # Tabloları oluştur (migrations yerine; proje için yeterli)
    Base.metadata.create_all(bind=engine)

    # LocalStack'te bucket yoksa oluştur
    try:
        create_bucket_if_not_exists()
    except Exception as e:
        # LocalStack henüz hazır değilse uyarı ver ama çökme
        print(f"[Uyarı] S3 bucket oluşturulamadı: {e}")

    yield  # Uygulama burada çalışır

    # --- Kapanış ---
    engine.dispose()


app = FastAPI(
    title="QLink API",
    description="Cloud-Native QR Code Management Platform",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS: Frontend'in (React) backend'e erişmesine izin ver
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Üretimde frontend domain'iyle sınırlandırılmalı
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Route'ları kaydet
app.include_router(auth_router.router, prefix="/auth", tags=["Auth"])
app.include_router(qr_router.router, prefix="/qr", tags=["QR Codes"])

# Prometheus: /metrics endpoint'ini ekle
setup_metrics(app)

# OpenTelemetry: OTEL_ENABLED=true ise tracing'i başlat
setup_tracing(app)


@app.get("/health", tags=["System"])
def health_check():
    """
    Kubernetes liveness/readiness probe için kullanılır.
    Prometheus scrape'e dahil edilmez.
    """
    return {"status": "healthy", "service": settings.APP_NAME}
