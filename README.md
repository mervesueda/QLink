# QLink – Cloud-Native QR Code Management Platform

> **Marmara Üniversitesi — Mühendislik Fakültesi — Bilgisayar Mühendisliği Bölümü**  
> **MTH2526-B25 — Bulut Mimarilerinde Test Mühendisliği | 2025–2026 Bahar Yarıyılı**  
> **Konu #35:** QR Code Generator Service — QR üret, S3'e kaydet, link ver

---

🎥 **Yedek Canlı Demo Videosu:** [YouTube/Drive linki — sunum öncesi eklenecek]

---

## 👥 Grup Üyeleri

| İsim | Rol & Sorumluluk |
|---|---|
| Merve Sueda Aydın | Backend Core, Veritabanı, LocalStack, K8s, Helm & ArgoCD |
| Elif Seda Demirhan | UI, Unit/Integration Testler, CI/CD, E2E, Monitoring & k6 |

> **Not:** Şartname gereği proje 2 kişilik ekip tarafından tüm adımlarıyla eşit iş dağılımı yapılarak tamamlanmıştır.

---

## 📋 Proje Hakkında

QLink; URL, metin ve e-posta içeriklerinden **QR kod** üreten, bunları **AWS S3 (LocalStack)** üzerinde depolayan ve kullanıcı bazlı yönetim sunan cloud-native bir platformdur.

> Amaç: "Karmaşık bir uygulama yazmak değil, basit bir uygulama için endüstri standardında test ve dağıtım altyapısı kurmak."

---

## 🏗️ Mimari

```
Kullanıcı Tarayıcısı
        │
        ▼
React Frontend (Vite + nginx)  :3000
        │  HTTP REST
        ▼
FastAPI Backend (Python 3.12)  :8000
     │         │
     ▼         ▼
PostgreSQL   LocalStack S3
(kayıt)      (QR PNG dosyaları)

Yan servisler:
  Prometheus :9090  → /metrics scrape
  Grafana    :3001  → Dashboard (3 panel)
  Jaeger     :16686 → Distributed Tracing (OTel Bonus)
```

> Mimari diyagram: `docs/architecture.png`

---

## 🗂️ Repo Yapısı

```
QLink/                             # ← Proje kök dizini
├── README.md                      # Bu dosya
├── LICENSE                        # MIT Lisansı
├── docker-compose.yml             # 7 servis: postgres, localstack, backend, frontend, prometheus, grafana, jaeger
│
├── backend/                       # FastAPI uygulaması
│   ├── Dockerfile                 # Multi-stage: builder (pip) + runtime (python-slim)
│   ├── requirements.txt
│   ├── requirements-test.txt
│   └── app/
│       ├── main.py                # FastAPI app, lifespan, router kayıtları
│       ├── api/
│       │   ├── auth.py            # POST /auth/register, POST /auth/login
│       │   └── qr.py             # POST /qr/generate, GET /qr/{id}, GET /qr/history, DELETE /qr/{id}
│       ├── core/
│       │   ├── config.py          # pydantic-settings ile env yönetimi
│       │   ├── security.py        # JWT + bcrypt
│       │   ├── metrics.py         # Prometheus instrumentasyonu
│       │   └── telemetry.py       # OpenTelemetry + Jaeger (Bonus)
│       ├── db/
│       │   ├── base.py            # SQLAlchemy engine, get_db()
│       │   └── models.py          # User, QRCode ORM modelleri
│       ├── schemas/
│       │   ├── auth.py            # RegisterRequest, LoginResponse
│       │   └── qr.py             # QRCreate, GuestQRResponse, QRRecord
│       └── services/
│           ├── qr_service.py      # generate_qr_png() — saf QR üretimi
│           └── s3_service.py      # boto3 ile LocalStack S3 yükleme/silme
│
├── tests/                         # Tüm testler (şartname: src/ yerine backend/tests/)
│   ├── conftest.py                # Testcontainers PostgreSQL + S3 mock fixture
│   ├── factories.py               # Factory Boy: UserFactory, QRCodeFactory
│   ├── unit/                      # 43 unit test (auth, qr_service, s3_service, schemas)
│   └── integration/               # 20+ integration test (Testcontainers + DB)
│
├── frontend/                      # React 18 + Vite 5
│   ├── Dockerfile                 # Multi-stage: node build → nginx serve
│   ├── nginx.conf
│   ├── src/
│   │   ├── api/                   # axios client
│   │   ├── components/            # Navbar
│   │   ├── pages/                 # HomePage, CreateQR, MyQRs, Login, Register
│   │   └── store/                 # Auth Context
│   ├── e2e/                       # Playwright E2E testleri
│   │   ├── qlink.spec.js          # 5 kullanıcı senaryosu
│   │   └── qr-image-download.spec.js
│   └── playwright.config.js
│
├── postman/
│   └── QLink.postman_collection.json  # 14 istek, Newman ile CI'da koşar
│
├── k8s/
│   ├── deployment.yaml            # Backend, Frontend, PostgreSQL, LocalStack
│   ├── service.yaml               # NodePort (frontend) + ClusterIP (diğerleri)
│   └── configmap.yaml             # Tüm env değişkenleri
│
├── perf/                          # Şartname uyumlu klasör adı
│   ├── load-test.js               # k6 yük testi (200 VU, aşamalı)
│   └── report.md                  # p95 latency sonuçları
│
├── monitoring/
│   ├── prometheus.yml             # Scrape config (qlink-backend:8000/metrics)
│   ├── grafana-dashboard.json     # 3 panel: Latency, Error Rate, Throughput
│   └── grafana/
│       ├── provisioning/          # Otomatik datasource + dashboard yükleme
│       └── dashboards/qlink.json  # Grafana dashboard tanımı
│
├── helm/qlink/                    # Helm Chart (Bonus +5)
├── argocd/                        # ArgoCD GitOps (Bonus +5)
│   └── application.yaml
│
├── .github/
│   └── workflows/
│       └── ci-cd.yml              # Lint → Test → Docker Build → Deploy → Smoke → Newman → E2E
│
└── docs/
    ├── architecture.png           # Mimari diyagram ✅
    ├── work-distribution.md       # İş paylaşımı dokümanı ✅
    ├── slides.pdf                 # Sunum slaytları ✅
    └── final-report.pdf           # Final rapor 4-6 sayfa ✅
```

---

## 🚀 Hızlı Başlangıç — Docker Compose

**Ön gereksinim:** Docker Desktop kurulu ve çalışıyor olmalı.

```bash
# 1. Repoyu klonla
git clone https://github.com/[KULLANICI_ADI]/QLink.git
cd QLink

# 2. Tüm servisleri başlat (ilk seferde ~3-5 dk)
docker-compose up -d --build
```

Servisler hazır olduğunda:

| Servis | URL | Açıklama |
|---|---|---|
| 🌐 Frontend | http://localhost:3000 | React web arayüzü |
| ⚙️ Backend API | http://localhost:8000 | FastAPI |
| 📖 Swagger UI | http://localhost:8000/docs | API belgeleri |
| 📊 Grafana | http://localhost:3001 | admin / admin |
| 🔍 Prometheus | http://localhost:9090 | Metrik toplayıcı |
| 🔭 Jaeger UI | http://localhost:16686 | Distributed tracing |
| ☁️ LocalStack | http://localhost:4566 | AWS S3 simülasyonu |

```bash
# Durdurmak için
docker-compose down

# Tüm veriyle sıfırlamak için
docker-compose down -v
```

---

## 🧪 Backend Testleri (Pytest)

```bash
cd backend

# Sanal ortam kur
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/macOS

# Bağımlılıkları yükle
pip install -r requirements.txt -r requirements-test.txt

# Tüm testler (Docker çalışıyor olmalı — Testcontainers kullanır)
pytest tests/ -v

# Coverage raporu ile (%70 gate)
pytest tests/ --cov=app --cov-report=term-missing --cov-fail-under=70

# Sadece unit testler (Docker gerekmez)
pytest tests/unit/ -v

# Sadece integration testler (Docker gerekir)
pytest tests/integration/ -v
```

> **Not:** Integration testler Testcontainers kullanır; Docker daemon çalışıyor olmalı.  
> Beklenen coverage: **≥ %70**

### Test Özeti

| Katman | Araç | Test Sayısı |
|---|---|---|
| Unit | Pytest + moto[s3] | 43 test |
| Integration | Pytest + Testcontainers | 20+ test |
| E2E | Playwright | 6 senaryo |
| API | Newman (Postman) | 14 istek, 27 assertion |
| Performans | k6 | 200 VU, aşamalı yük |

---

## 🎭 E2E Testler (Playwright)

```bash
cd frontend

# Browser'ları kur (ilk seferinde)
npx playwright install chromium

# Testleri çalıştır (frontend + backend ayakta olmalı)
npm exec playwright test

# UI modunda (görsel debug)
#npx playwright test --ui

# Raporu görüntüle
npx playwright show-report
```

**Test Senaryoları:**
1. Ana sayfa açılır ve QR oluştur butonu görünür
2. Misafir kullanıcı QR oluşturabilir (content + type)
3. QR kodu PNG olarak indirilebilir
4. Kullanıcı kayıt olup giriş yapabilir
5. Giriş yapmış kullanıcı QR geçmişini görebilir

---

## 📈 Performans Testi (k6)

```bash
# k6 kurulumu: https://k6.io/docs/get-started/installation/

# Varsayılan (localhost:8000)
k6 run perf/load-test.js

# Farklı URL
BASE_URL=http://localhost:8000 k6 run perf/load-test.js

# JSON rapor ile
k6 run --out json=perf/k6-results.json perf/load-test.js
```

**Test Profili (şartname: 100-200 eşzamanlı kullanıcı):**
```
Ramp-up   : 0 → 100 VU  (1 dakika)
Sürdürme  : 100 VU       (3 dakika)
Peak      : 100 → 200 VU (1 dakika)
Peak Hold : 200 VU       (2 dakika)
Ramp-down : 200 → 0 VU   (1 dakika)
```

**Threshold'lar:** p95 < 500ms | error rate < %5

Sonuçlar: `perf/report.md`

---

## 📬 API Testi (Postman / Newman)

```bash
# Newman kurulumu
npm install -g newman newman-reporter-htmlextra

# Koleksiyonu çalıştır
newman run postman/QLink.postman_collection.json \
  --env-var BASE_URL=http://localhost:8000

# HTML rapor ile (PowerShell'de tek tırnak zorunlu)
newman run postman/QLink.postman_collection.json `
  --env-var BASE_URL=http://localhost:8000 `
  --reporters 'cli,htmlextra' `
  --reporter-htmlextra-export newman-report.html

# Raporu tarayıcıda aç
Invoke-Item newman-report.html
```

---

## ☸️ Kubernetes — Minikube Deploy

```bash
# 1. Minikube başlat
minikube start

# 2. Docker image'larını Minikube içinde oluştur
minikube docker-env | Invoke-Expression   # Windows PowerShell
# eval $(minikube docker-env)             # Linux/macOS

docker build -t qlink-backend:latest ./backend
docker build -t qlink-frontend:latest ./frontend

# 3. Manifest'leri uygula
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# 4. Pod durumunu izle
kubectl get pods -w

# 5. Frontend'e eriş
minikube service qlink-frontend

# Loglar
kubectl logs deployment/qlink-backend -f
```

---

## ⛵ Helm ile Deploy (Bonus +5)

```bash
# Chart doğrula
helm lint helm/qlink/

# Dry-run (ne oluşturulacak göster)
helm install qlink ./helm/qlink --dry-run --debug

# Deploy
helm install qlink ./helm/qlink

# Güncelle
helm upgrade qlink ./helm/qlink

# Kaldır
helm uninstall qlink
```

---

## 🔄 ArgoCD GitOps (Bonus +5)

```bash
# ArgoCD kurulumu
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# argocd/application.yaml içindeki repoURL'i kendi repo adresinle güncelle
kubectl apply -f argocd/application.yaml

# ArgoCD UI
kubectl port-forward svc/argocd-server -n argocd 8080:443
# → https://localhost:8080

# İlk admin şifresi
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
```

---

## 🔭 OpenTelemetry Tracing (Bonus +5)

Jaeger docker-compose içinde hazır. Etkinleştirmek için:

```bash
# docker-compose.yml içindeki backend environment'ına ekle:
OTEL_ENABLED: "true"

# Yeniden başlat
docker-compose up -d backend

# Trace'leri gör
# http://localhost:16686 → Service: qlink-backend
```

---

## 📊 Monitoring

### Grafana Dashboard

1. http://localhost:3001 → admin / admin
2. **"QLink – API Metrics"** dashboard'u otomatik yüklü
3. Paneller:
   - **Request Latency** — p50, p95, p99 histogram
   - **Error Rate** — 4xx/5xx oranı
   - **Throughput** — başarılı istek/saniye (2xx)

Dashboard JSON: `monitoring/grafana-dashboard.json`

### Prometheus

- http://localhost:9090
- Metrics endpoint: http://localhost:8000/metrics

---

## 🔌 API Endpoint'leri

| Method | Path | Auth | Açıklama |
|---|---|---|---|
| POST | `/auth/register` | — | Kullanıcı kaydı |
| POST | `/auth/login` | — | JWT token al |
| POST | `/api/v1/qr/generate` | Opsiyonel | QR oluştur (misafir + kayıtlı) |
| GET | `/api/v1/qr/history` | Zorunlu | Kullanıcının QR geçmişi |
| GET | `/api/v1/qr/{id}` | Zorunlu | Tek QR detayı |
| DELETE | `/api/v1/qr/{id}` | Zorunlu | QR sil (DB + S3) |
| GET | `/health` | — | Liveness probe |
| GET | `/metrics` | — | Prometheus metrikleri |
| GET | `/docs` | — | Swagger UI |

---

## 🏆 Değerlendirme Rubric'i (100 + 15 Puan)

| Kalem | Puan | Durumumuz |
|---|---|---|
| Repo + Kod Kalitesi (coverage ≥%70) | 20 | ✅ |
| Test Çeşitliliği (Unit + Integration + E2E + Perf) | 15 | ✅ |
| CI/CD Pipeline (GitHub Actions yeşil) | 15 | ✅ |
| Container & K8s (Dockerfile + Minikube) | 15 | ✅ |
| AWS / LocalStack (S3 + testlerle doğrulama) | 5 | ✅ |
| Monitoring (Grafana ≥3 panel) | 5 | ✅ |
| Performans Raporu (k6 p95) | 5 | ✅ perf/report.md |
| Final Demo + Sunum (20 dk) | 15 | — |
| Final Rapor (docs/final-report.pdf) | 5 | ✅ |
| **TOPLAM** | **100** | |
| Helm Chart Bonus | +5 | ✅ |
| ArgoCD GitOps Bonus | +5 | ✅ |
| OpenTelemetry Bonus | +5 | ✅ |
| **BONUS** | **+15** | |

---

## 📝 Sunum Hazırlık Notları

### 20 Dakika Slot Yapısı
- **0-10 dk:** Slayt — Problem, Mimari, Test Stratejisi, Pipeline, Sayılar (7 slayt)
- **10-17 dk:** Canlı demo — PR → CI → Deploy → Grafana → k6 → E2E
- **17-20 dk:** Q&A

### Sunum Öncesi Kontrol Listesi
- [ ] Minikube başlatıldı, image'lar build edildi
- [ ] docker-compose up -d çalıştırıldı
- [ ] Grafana ve Jaeger tarayıcıda açık
- [ ] Terminal hazır (5 dk öncesi Meet'e girildi)
- [ ] `docs/slides.pdf` hazır

### Q&A'da Sorulabilecekler
- "Bu Dockerfile'da neden multi-stage kullandın?"
- "Coverage neden %70'in üzerinde?"
- "Deploy çökerse rollback nasıl yapılır?"
- "LocalStack gerçek S3'ten ne farkı var?"

---

## 📚 Teknoloji Yığını

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
| Unit/Integration Test | Pytest, Testcontainers, Factory Boy, Faker, moto |
| E2E Test | Playwright |
| Performans | k6 |
| API Test | Postman / Newman |
| GitOps (Bonus) | ArgoCD |

---

## 📄 Lisans

MIT — Detaylar için `LICENSE` dosyasına bakın.

---

*QLink — MTH2526-B25 Bulut Mimarilerinde Test Mühendisliği | Marmara Üniversitesi 2026*
