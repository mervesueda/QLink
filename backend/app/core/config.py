"""
config.py – Uygulama konfigürasyonu.

pydantic-settings kullanarak ortam değişkenlerini okur.
.env dosyasından veya gerçek env'den değerleri alır.
Tüm servisler (db, s3, jwt) bu tek yerden konfigüre edilir.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # --- Uygulama ---
    APP_NAME: str = "QLink"
    DEBUG: bool = False

    # --- JWT ---
    # Üretimde mutlaka değiştirilmeli (openssl rand -hex 32)
    SECRET_KEY: str = "changeme-use-openssl-rand-hex-32-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # --- Veritabanı ---
    DATABASE_URL: str = "postgresql://qlink:qlink@localhost:5432/qlink"

    # --- LocalStack / S3 ---
    AWS_ENDPOINT_URL: str = "http://localhost:4566"
    AWS_BUCKET_NAME: str = "qlink-qrcodes"
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: str = "test"
    AWS_SECRET_ACCESS_KEY: str = "test"

    # --- OpenTelemetry (Bonus) ---
    OTEL_ENABLED: bool = False
    OTEL_EXPORTER_OTLP_ENDPOINT: str = "http://localhost:4317"
    OTEL_SERVICE_NAME: str = "qlink-backend"

    class Config:
        # Docker Compose veya yerel geliştirmede .env dosyasından oku
        env_file = ".env"
        env_file_encoding = "utf-8"


# Uygulama boyunca tek bir settings nesnesi kullanılır (singleton)
settings = Settings()
