# ----- Stage 1: Builder -----
# Bağımlılıkları bu aşamada kur; üretim image'ına derleyiciler taşınmaz
FROM python:3.12-slim AS builder

WORKDIR /build

# Derleme için gerekli sistem kütüphaneleri
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt


# ----- Stage 2: Runtime -----
# Sadece çalışma zamanı için gereken minimum image
FROM python:3.12-slim

WORKDIR /app

# Sadece çalışma zamanı kütüphanesi (libpq)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Builder aşamasında kurulan paketleri kopyala
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Uygulama kodunu kopyala
COPY app/ ./app/

# Root olmayan kullanıcıyla çalıştır (güvenlik)
RUN adduser --disabled-password --gecos "" appuser
USER appuser

EXPOSE 8000

# Üretimde workers artırılabilir: --workers 4
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
