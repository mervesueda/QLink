# QLink – Cloud-Native QR Code Management Platform

> 🎓 Bulut Mimarilerinde Test Mühendisliği – Dönem Projesi (Konu 35)

QLink; QR kod üretimi, AWS S3 depolama (LocalStack) ve kullanıcı yönetimini **endüstri standardı test ve dağıtım altyapısıyla** bir araya getiren cloud-native bir platformdur. Uygulamanın kendisi kasıtlı olarak sade tutulmuş; odak noktası **test kalitesi** ve **altyapı olgunluğu** üzerinedir.

---

## 🏗️ Mimari

```
Kullanıcı Tarayıcısı
        │
        ▼
React Frontend (Vite + nginx)   ← Port 3000
        │  HTTP REST (proxy)
        ▼
FastAPI Backend (Python 3.12)   ← Port 8000
     │         │
     ▼         ▼
PostgreSQL   LocalStack S3      ← Port 5432 / 4566
(kayıt)      (QR dosyaları)

Yan servisler:
  Prometheus (:9090) → /metrics scrape
  Grafana    (:3001) → Dashboard (4 panel)
  Jaeger     (:16686)→ Distributed Tracing (OTel Bonus)
```

---

## 🛠️ Teknoloji Yığını

| Katman | Teknoloji |
|---|---|
| Backend | Python 3.12, FastAPI, SQLAlchemy |
| Frontend | React 18, Vite 5, React Router v6 |
| Veritabanı | PostgreSQL 15 |
| Nesne Deposu | LocalStack S3 (boto3) |
| Container | Docker, Docker Compose |
| Orchestration | Kubernetes (Minikube), Helm |
| CI/CD | GitHub Actions (6 aşama) |
| Monitoring | Prometheus, Grafana |
| Tracing (Bonus) | OpenTelemetry, Jaeger |
| Test – Unit/Integration | Pytest, Testcontainers, Factory Boy, Faker |
| Test – E2E | Playwright (7 senaryo) |
| Test – Performans | k6 |
| API Test | Postman / Newman |
| GitOps (Bonus) | ArgoCD |
| Paket Yönetimi (Bonus) | Helm |

---

## 📁 Klasör Yapısı

```
QLink/
├── backend/                   # FastAPI uygulaması
│   ├── app/
│   │   ├── api/               # Route handler'ları (auth.py, qr.py)
│   │   ├── core/              # config, security, metrics, telemetry
│   │   ├── db/                # SQLAlchemy base ve modeller
│   │   ├── schemas/           # Pydantic istek/yanıt şemaları
│   │   └── services/          # qr_service.py, s3_service.py
│   ├── tests/
│   │   ├── conftest.py        # Testcontainers PostgreSQL fixture
│   │   ├── factories.py       # Factory Boy + Faker
│   │   ├── unit/              # Servis katmanı unit testleri
│   │   └── integration/       # API endpoint integration testleri
│   ├── Dockerfile             # Multi-stage build
│   ├── requirements.txt
│   └── requirements-test.txt
│
├── frontend/                  # React + Vite
│   ├── src/
│   │   ├── api/               # axios client (auth + QR API'si)
│   │   ├── components/        # Navbar, AuthenticatedImage
│   │   ├── pages/             # HomePage, CreateQR, MyQRs, Login, Register
│   │   └── store/             # Auth Context (JWT yönetimi)
│   ├── e2e/                   # Playwright testleri (7 senaryo)
│   │   ├── qlink.spec.js      # 5 ana E2E senaryosu
│   │   └── qr-image-download.spec.js  # QR görsel + indirme testleri
│   ├── Dockerfile             # Multi-stage: node build → nginx serve
│   └── playwright.config.js
│
├── k8s/                       # Kubernetes manifests
│   ├── configmap.yaml
│   ├── deployment.yaml
│   └── service.yaml
│
├── helm/qlink/                # Helm Chart (Bonus)
├── argocd/                    # ArgoCD GitOps (Bonus)
│   └── application.yaml
│
├── monitoring/
│   ├── prometheus.yml         # Scrape konfigürasyonu
│   └── grafana/
│       ├── provisioning/      # Otomatik data source + dashboard
│       └── dashboards/        # qlink.json (4 panel)
│
├── performance/
│   ├── k6_test.js             # Yük testi (p95 < 500ms)
│   └── report.md              # p95 sonuçları ve analiz
│
├── postman/
│   └── QLink.postman_collection.json  # 5 istek + Newman
│
├── docs/
│   ├── final-report.md        # Final rapor
│   └── work-distribution.md  # İş paylaşımı belgesi (Ek C)
│
├── LICENSE                    # MIT License
└── .github/workflows/
    └── ci.yml                 # Lint → Test → Coverage → Build → Deploy → Smoke
```

---

## 🚀 Hızlı Başlangıç – Docker Compose

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

| Servis | URL | Kimlik Bilgisi |
|---|---|---|
| Frontend | http://localhost:3200 | – |
| Backend API | http://localhost:8000 | – |
| Swagger UI | http://localhost:8000/docs | – |
| Prometheus | http://localhost:9090 | – |
| Grafana | http://localhost:3001 | admin / admin |
| Jaeger UI | http://localhost:16686 | – |
| LocalStack | http://localhost:4566 | – |

```bash
# Durdurmak için:
docker-compose down

# Volume'larla birlikte sıfırlamak için:
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

## 🌐 Frontend Geliştirme

```bash
cd frontend

# Bağımlılıkları kur
npm install

# Dev server'ı başlat (backend de çalışıyor olmalı)
npm run dev
# → http://localhost:3200
# Build
npm run build
```

---

## 🎭 E2E Testler (Playwright)

```bash
cd frontend

# Playwright browser'larını kur (ilk seferinde)
npx playwright install chromium

# Testleri çalıştır (frontend ve backend ayakta olmalı)
$env:PLAYWRIGHT_BASE_URL="http://localhost:3200"
npx playwright test

# UI modunda (görsel debug)
npx playwright test --ui

# Raporu görüntüle
npx playwright show-report

# Belirli spec dosyasını çalıştır
npx playwright test e2e/qr-image-download.spec.js --headed
```

> **Not (Windows port sorunu):** Windows Hyper-V/WSL2, `2586–3186` port aralığını
> dynamic reservation ile kilitler. Port 3000 bu aralıkta olduğundan Docker bind yapamaz.
> Frontend **port 3200**'de servis eder (`http://localhost:3200`).

### Test Senaryoları

**`qlink.spec.js` – Ana Senaryolar:**
1. Ana sayfa başarıyla açılır
2. Misafir kullanıcı QR oluşturabilir
3. Oluşturulan QR indirilebilir
4. Kullanıcı kayıt olup giriş yapabilir
5. Giriş yapılmış kullanıcı QR listesini görebilir

**`qr-image-download.spec.js` – Görsel ve İndirme:**

6. QR önizleme görselleri kırık olmadan yüklenmeli (`AuthenticatedImage` blob URL testi)
7. İndirme butonu fetch+blob akışıyla dosyayı indirebilmeli

> **AuthenticatedImage açıklaması:** Browser `<img src>` tag'i JWT `Authorization` header gönderemez. Bu nedenle korunan `/qr/{id}/image` endpoint'ine doğrudan `src` ile erişim 401 verir. Çözüm: `fetch() API` + `Blob URL` + `<img src={blobUrl}>` pattern'i kullanılır.

---

## ⚡ Performans Testi (k6)

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

**Ölçülen sonuçlar:** `performance/report.md` dosyasında ayrıntılı analiz mevcuttur.
- **p95 latency: ~89ms** (threshold: 500ms ✅)
- **Error rate: %0** ✅
- **Throughput: 97.2 req/s** (10 VU ile)

---

## 📮 API Testi (Postman / Newman)

```bash
# Newman kurulumu
npm install -g newman

# Collection çalıştır
newman run postman/QLink.postman_collection.json \
  --env-var BASE_URL=http://localhost:8000

# JSON rapor
newman run postman/QLink.postman_collection.json \
  --env-var BASE_URL=http://localhost:8000 \
  --reporters cli,json \
  --reporter-json-export newman-results.json
```

**Collection içeriği (5 istek):**
1. `POST /auth/register`
2. `POST /auth/login`
3. `POST /qr/create`
4. `GET /qr/list`
5. `DELETE /qr/{id}`

---

## ☸️ Kubernetes – Minikube Deploy

```bash
# Minikube başlat
minikube start

# Docker image'larını Minikube'de oluştur
eval $(minikube docker-env)             # Linux/macOS
minikube docker-env | Invoke-Expression  # Windows PowerShell

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

## ⛵ Helm ile Deploy (Bonus)

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

## 🔄 ArgoCD GitOps (Bonus)

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

## 🔭 OpenTelemetry Tracing (Bonus)

Docker Compose'da Jaeger servisi yapılandırılmıştır. `docker-compose.yml`'de `OTEL_ENABLED: "true"` olarak zaten ayarlıdır.

```bash
# Servisleri başlat (OTel aktif)
docker-compose up -d

# Trace'leri görüntüle:
# http://localhost:16686 → Service: qlink-backend
```

> **Kök neden düzeltmesi:** `opentelemetry-exporter-otlp-proto-grpc >= 1.21.0`'da `OTLPSpanExporter(insecure=True)` parametresi kaldırıldı. `http://` prefix'li endpoint kullanıldığında SDK otomatik olarak insecure kanal açar.

---

## 📊 Monitoring

### Grafana Dashboard

1. http://localhost:3001 adresine git (admin/admin)
2. **"QLink – API Metrics"** dashboard'u otomatik yüklenmiş olacak
3. Paneller (4 adet):
   - **Request Latency** – p50, p95, p99 histogram
   - **Error Rate** – 4xx/5xx oranı
   - **Throughput** – req/s (2xx)
   - **Active Requests** – Toplam istek sayısı

> **Kök neden düzeltmesi:** Dashboard JSON dosyasındaki `${DS_PROMETHEUS}` template değişkeni provisioning sırasında çözülemiyordu. Datasource UID `PBFA97CFB590B2093` ile sabitlendi ve provisioning dosyasında `uid` alanı eklendi.

### Prometheus

- http://localhost:9090
- `/metrics` endpoint: `http://localhost:8000/metrics`
- Targets: http://localhost:9090/targets

---

## 🔌 API Endpoint'leri

| Method | Path | Auth | Açıklama |
|---|---|---|---|
| POST | `/auth/register` | – | Yeni kullanıcı kaydı |
| POST | `/auth/login` | – | JWT token al |
| POST | `/qr/create` | Opsiyonel | QR oluştur (misafir + kayıtlı) |
| GET | `/qr/list` | Zorunlu | Kullanıcının QR listesi |
| GET | `/qr/{id}` | Zorunlu | Tek QR detayı |
| GET | `/qr/{id}/image` | Zorunlu | QR görselini PNG olarak sun |
| GET | `/qr/{id}/image?download=true` | Zorunlu | QR'ı dosya olarak indir |
| DELETE | `/qr/{id}` | Zorunlu | QR sil (DB + S3) |
| GET | `/health` | – | Liveness probe |
| GET | `/metrics` | – | Prometheus metrikler |
| GET | `/docs` | – | Swagger UI |

---

## ✅ Gereksinim Checklist Durumu

### İdari ve Repo
- [x] GitHub Reposu mevcut
- [x] LICENSE dosyası (MIT)
- [x] README.md (bu dosya)
- [x] `docs/work-distribution.md` – İş paylaşımı belgesi
- [x] `docs/final-report.md` – Final rapor

### Teknik Gereksinimler

#### Katman 1: Servis & Veritabanı
- [x] Python FastAPI ile yazılmış servis
- [x] 6 REST endpoint (list, create, get, image, download, delete)
- [x] PostgreSQL entegrasyonu (Testcontainers ile doğrulanmış)

#### Katman 2: Test Verisi & Pytest
- [x] Factory Boy + Faker (`tests/factories.py`)
- [x] Pytest unit testleri (%70 coverage)
- [x] Integration testleri (Testcontainers PostgreSQL)

#### Katman 3: Postman & Newman
- [x] 5 istek içeren Postman collection (`postman/QLink.postman_collection.json`)
- [x] Newman CI entegrasyonu (`ci.yml`'de Smoke Test aşaması)

#### Katman 4: Docker & AWS (LocalStack)
- [x] Multi-stage Dockerfile (backend + frontend)
- [x] `docker-compose.yml` (tüm servisler)
- [x] LocalStack S3 entegrasyonu (bucket oluşturma + upload + delete)

#### Katman 5: Kubernetes (Minikube)
- [x] `k8s/deployment.yaml`
- [x] `k8s/service.yaml`
- [x] `k8s/configmap.yaml`

#### Katman 6: GitHub Actions (CI/CD)
- [x] `.github/workflows/ci.yml`
- [x] Lint → Pytest → Coverage → Docker Build → Deploy → Smoke Test

#### Katman 7: Performans & E2E
- [x] k6 yük testi (`performance/k6_test.js`)
- [x] p95 latency ölçümü + raporu (`performance/report.md`)
- [x] Playwright E2E testleri (7 senaryo: `qlink.spec.js` + `qr-image-download.spec.js`)

#### Katman 8: Monitoring
- [x] Prometheus exporter (prometheus-fastapi-instrumentator)
- [x] Grafana dashboard – 4 panel (Latency, Error Rate, Throughput, Active Requests)
- [x] Otomatik provisioning (datasource + dashboard)

### Bonus
- [x] Helm Chart – `helm/qlink/`
- [x] ArgoCD GitOps – `argocd/application.yaml`
- [x] OpenTelemetry Distributed Tracing

---

## 🐛 Bilinen Sorunlar ve Düzeltmeler

### AuthenticatedImage Blob URL Akışı
Browser `<img src>` tag'i JWT Authorization header gönderemez. Bu nedenle:
- **Yanlış:** `<img src="/qr/{id}/image">` → 401 hatası → kırık görsel
- **Doğru:** `fetch("/qr/{id}/image", {headers: {Authorization: ...}})` → Blob → `<img src={blobUrl}>`

`AuthenticatedImage` bileşeni bu pattern'i uygular. `MyQRs` sayfasındaki tüm thumbnail'lar bu bileşeni kullanır.

### OpenTelemetry insecure Parametresi
`opentelemetry-exporter-otlp-proto-grpc >= 1.21.0`'da `OTLPSpanExporter(insecure=True)` kaldırıldı. `http://` endpoint kullanıldığında SDK otomatik insecure bağlantı açar.

### Grafana Dashboard UID Eşleşmesi
Provisioning ile yüklenen dashboard'larda `${DS_PROMETHEUS}` placeholder'ı çözülemiyor. Datasource ve dashboard JSON'da aynı `uid` değeri (`PBFA97CFB590B2093`) kullanılmalı.

---

## 📚 Kaynaklar

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Testcontainers for Python](https://testcontainers-python.readthedocs.io/)
- [Playwright Testing](https://playwright.dev/)
- [prometheus-fastapi-instrumentator](https://github.com/trallnag/prometheus-fastapi-instrumentator)
- [OpenTelemetry Python](https://opentelemetry.io/docs/instrumentation/python/)
- [LocalStack Documentation](https://docs.localstack.cloud/)
- [Helm Charts Guide](https://helm.sh/docs/chart_template_guide/)
- [ArgoCD Documentation](https://argo-cd.readthedocs.io/)
- [k6 Load Testing](https://k6.io/docs/)

---

## 📄 Lisans

MIT – Detaylar için [LICENSE](LICENSE) dosyasına bakın.

---

*QLink – Bulut Mimarilerinde Test Mühendisliği, 2026*
