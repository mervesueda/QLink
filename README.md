# QLink – Cloud-Native QR Code Management Platform

> Bulut Mimarilerinde Test Mühendisliği dersi dönem projesi.

QLink; QR kod üretimi, AWS S3 depolama ve kullanıcı yönetimini endüstri standardı test ve dağıtım altyapısıyla bir araya getiren **cloud-native** bir platformdur. Uygulamanın kendisi kasıtlı olarak sade tutulmuş; odak nokta **test kalitesi** ve **altyapı** üzerinedir.

---

## Mimari

```
Kullanıcı Tarayıcısı
        │
        ▼
React Frontend (Vite + nginx)
        │  HTTP REST
        ▼
FastAPI Backend (Python 3.12)
     │         │
     ▼         ▼
PostgreSQL   LocalStack S3
(kayıt)      (QR dosyaları)

Yan servisler:
  Prometheus → /metrics scrape
  Grafana    → Dashboard
  Jaeger     → Distributed Tracing (OTel Bonus)
```

---

## Teknoloji Yığını

| Katman | Teknoloji |
|---|---|
| Backend | Python 3.12, FastAPI, SQLAlchemy |
| Frontend | React 18, Vite 5, React Router v6 |
| Veritabanı | PostgreSQL 15 |
| Nesne Deposu | LocalStack S3 (boto3) |
| Container | Docker, Docker Compose |
| Orchestration | Kubernetes (Minikube), Helm |
| CI/CD | GitHub Actions |
| Monitoring | Prometheus, Grafana |
| Tracing (Bonus) | OpenTelemetry, Jaeger |
| Test – Unit/Integration | Pytest, Testcontainers, Factory Boy, Faker |
| Test – E2E | Playwright |
| Test – Performans | k6 |
| API Test | Postman / Newman |
| GitOps (Bonus) | ArgoCD |

---

## Klasör Yapısı

```
QLink/
├── backend/              # FastAPI uygulaması
│   ├── app/
│   │   ├── api/          # Route handler'ları (auth.py, qr.py)
│   │   ├── core/         # config, security, metrics, telemetry
│   │   ├── db/           # SQLAlchemy base ve modeller
│   │   ├── schemas/      # Pydantic istek/yanıt şemaları
│   │   └── services/     # qr_service.py, s3_service.py
│   ├── tests/
│   │   ├── conftest.py   # Testcontainers PostgreSQL fixture
│   │   ├── factories.py  # Factory Boy + Faker
│   │   ├── unit/         # Servis katmanı unit testleri
│   │   └── integration/  # API endpoint integration testleri
│   ├── Dockerfile        # Multi-stage build
│   └── requirements.txt
│
├── frontend/             # React + Vite
│   ├── src/
│   │   ├── api/          # axios client
│   │   ├── components/   # Navbar
│   │   ├── pages/        # HomePage, CreateQR, MyQRs, Login, Register
│   │   └── store/        # Auth Context
│   ├── e2e/              # Playwright testleri (5 senaryo)
│   ├── Dockerfile        # Multi-stage: node build → nginx serve
│   └── nginx.conf
│
├── k8s/                  # Kubernetes manifests
│   ├── configmap.yaml
│   ├── deployment.yaml
│   └── service.yaml
│
├── helm/qlink/           # Helm Chart (Bonus)
├── argocd/               # ArgoCD GitOps (Bonus)
│
├── monitoring/
│   ├── prometheus.yml
│   └── grafana/
│       ├── provisioning/ # Otomatik data source + dashboard
│       └── dashboards/   # qlink.json (3 panel)
│
├── performance/
│   └── k6_test.js        # Yük testi (p95 < 500ms)
│
├── postman/
│   └── QLink.postman_collection.json
│
└── .github/workflows/
    └── ci.yml            # Lint → Test → Coverage → Build → Deploy → Smoke
```

---

## Hızlı Başlangıç – Docker Compose

**Ön gereksinim:** Docker ve Docker Compose kurulu olmalı.

```bash
# 1. Repo'yu klonla
git clone https://github.com/mervesueda/QLink.git
cd QLink

# 2. Tüm servisleri başlat (ilk seferinde image build edilir, ~3-5 dk)
docker-compose up --build

# Arka planda çalıştırmak için:
docker-compose up -d --build
```

Servisler hazır olduğunda:

| Servis | URL |
|---|---|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3001 (admin/admin) |
| Jaeger UI | http://localhost:16686 |
| LocalStack | http://localhost:4566 |

```bash
# Durdurmak için:
docker-compose down

# Volume'larla birlikte sıfırlamak için:
docker-compose down -v
```

---

## Backend Testleri (Pytest)

```bash
cd backend

# Sanal ortam kur
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/macOS

# Bağımlılıkları kur
pip install -r requirements.txt -r requirements-test.txt

# Testleri çalıştır (Testcontainers Docker'a ihtiyaç duyar)
pytest tests/ -v

# Coverage raporu ile
pytest tests/ --cov=app --cov-report=term-missing

# Sadece unit testler (Docker gerekmez)
pytest tests/unit/ -v

# Sadece integration testler
pytest tests/integration/ -v
```

> **Not:** Integration testler Testcontainers kullanır. Docker daemon'ın çalışıyor olması gerekir.

Beklenen coverage: **≥ %70**

---

## Frontend Geliştirme

```bash
cd frontend

# Bağımlılıkları kur
npm install

# Dev server'ı başlat (backend de çalışıyor olmalı)
npm run dev
# → http://localhost:3000

# Build
npm run build
```

---

## E2E Testler (Playwright)

```bash
cd frontend

# Playwright browser'larını kur (ilk seferinde)
npx playwright install chromium

# Testleri çalıştır (frontend ve backend ayakta olmalı)
PLAYWRIGHT_BASE_URL=http://localhost:3000 npx playwright test

# UI modunda (görsel debug)
npx playwright test --ui

# Raporu görüntüle
npx playwright show-report
```

### Test Senaryoları
1. Ana sayfa açılır
2. Misafir kullanıcı QR oluşturabilir
3. QR indirilebilir
4. Kullanıcı kayıt olup giriş yapabilir
5. Giriş yapmış kullanıcı QR listesini görebilir

---

## Performans Testi (k6)

```bash
# k6 kurulumu: https://k6.io/docs/get-started/installation/

# Varsayılan (localhost:8000)
k6 run performance/k6_test.js

# Farklı URL
BASE_URL=http://localhost:8000 k6 run performance/k6_test.js

# JSON rapor
k6 run --out json=results.json performance/k6_test.js
```

**Test parametreleri:**
- 10 Virtual User, 30 saniye
- Threshold: p95 latency < 500ms
- Threshold: error rate < %5

---

## API Testi (Postman / Newman)

```bash
# Newman kurulumu
npm install -g newman

# Collection çalıştır
newman run postman/QLink.postman_collection.json \
  --env-var BASE_URL=http://localhost:8000

# HTML rapor
newman run postman/QLink.postman_collection.json \
  --env-var BASE_URL=http://localhost:8000 \
  --reporters html \
  --reporter-html-export newman-report.html
```

---

## Kubernetes – Minikube Deploy

```bash
# Minikube başlat
minikube start

# Docker image'larını Minikube'de oluştur
eval $(minikube docker-env)   # Linux/macOS
# Windows PowerShell: minikube docker-env | Invoke-Expression

docker build -t qlink-backend:latest ./backend
docker build -t qlink-frontend:latest ./frontend

# Manifest'leri uygula
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Pod durumunu kontrol et
kubectl get pods
kubectl get services

# Frontend'e erişim
minikube service qlink-frontend

# Logları görüntüle
kubectl logs deployment/qlink-backend -f
```

---

## Helm ile Deploy (Bonus)

```bash
# Helm kurulumu: https://helm.sh/docs/intro/install/

# Chart'ı doğrula
helm lint helm/qlink/

# Dry-run (ne oluşturulacağını göster)
helm install qlink ./helm/qlink --dry-run --debug

# Deploy
helm install qlink ./helm/qlink

# Güncelle
helm upgrade qlink ./helm/qlink

# Kaldır
helm uninstall qlink
```

---

## ArgoCD GitOps (Bonus)

```bash
# ArgoCD kurulumu (Minikube)
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# argocd/application.yaml içindeki repoURL'i kendi repo adresinle güncelle
# Ardından uygula:
kubectl apply -f argocd/application.yaml

# ArgoCD UI
kubectl port-forward svc/argocd-server -n argocd 8080:443
# → https://localhost:8080

# İlk admin şifresi
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
```

---

## OpenTelemetry Tracing (Bonus)

Docker Compose'da Jaeger servisi zaten yapılandırılmıştır. Etkinleştirmek için:

```bash
# docker-compose.yml içinde backend servisinde:
OTEL_ENABLED: "true"

# Ardından yeniden başlat:
docker-compose up -d backend

# Trace'leri görüntüle:
# http://localhost:16686 → Service: qlink-backend
```

---

## Monitoring

### Grafana Dashboard

1. http://localhost:3001 adresine git (admin/admin)
2. "QLink – API Metrics" dashboard'u otomatik yüklenmiş olacak
3. Paneller:
   - **Request Latency** – p50, p95, p99 histogram
   - **Error Rate** – 4xx/5xx oranı
   - **Throughput** – req/s (2xx)

### Prometheus

- http://localhost:9090
- `/metrics` endpoint: `http://localhost:8000/metrics`

---

## API Endpoint'leri

| Method | Path | Auth | Açıklama |
|---|---|---|---|
| POST | `/auth/register` | – | Yeni kullanıcı kaydı |
| POST | `/auth/login` | – | JWT token al |
| POST | `/qr/create` | Opsiyonel | QR oluştur (misafir + kayıtlı) |
| GET | `/qr/list` | Zorunlu | Kullanıcının QR listesi |
| GET | `/qr/{id}` | Zorunlu | Tek QR detayı |
| DELETE | `/qr/{id}` | Zorunlu | QR sil |
| GET | `/health` | – | Liveness probe |
| GET | `/metrics` | – | Prometheus metrikler |
| GET | `/docs` | – | Swagger UI |

---

## Lisans

MIT

---

*QLink – Bulut Mimarilerinde Test Mühendisliği, 2026*
