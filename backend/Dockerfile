# ----- Stage 1: Builder -----
FROM python:3.12-alpine AS builder

WORKDIR /build

# Derleme için gerekli kütüphaneleri Alpine paket yöneticisiyle (apk) kuruyoruz
RUN apk add --no-cache gcc musl-dev postgresql-dev curl

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ----- Stage 2: Runtime -----
FROM python:3.12-alpine

WORKDIR /app

# Çalışma zamanı için gerekli kütüphaneler
RUN apk add --no-cache libpq curl

COPY --from=builder /install /usr/local
COPY . .

EXPOSE 8000

HEALTHCHECK --interval=15s --timeout=5s --retries=5 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]