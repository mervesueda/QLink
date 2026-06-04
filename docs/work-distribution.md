# QLink – İş Paylaşımı Belgesi

**Proje:** QLink – Cloud-Native QR Code Management Platform  
**Ders:** Bulut Mimarilerinde Test Mühendisliği  
**Şablon:** Şartname Ek C

---

## Grup Üyeleri ve Sorumluluklar

| Üye | Modüller | Sorumluluk |
|---|---|---|
| mervesueda | Backend, Frontend, CI/CD, K8s, Monitoring, Testing | Tüm teknik geliştirme |

---

## Modül Bazlı İş Dağılımı

### Backend (FastAPI)
- `backend/app/api/` – Auth ve QR endpoint'leri
- `backend/app/core/` – Security, config, metrics, telemetry
- `backend/app/db/` – SQLAlchemy modeller ve migrations
- `backend/app/services/` – QR üretimi, S3 entegrasyonu
- `backend/tests/` – Unit ve integration testler

### Frontend (React)
- `frontend/src/` – Tüm React bileşenleri ve sayfalar
- `frontend/e2e/` – Playwright E2E testleri

### Altyapı
- `docker-compose.yml` – Tüm servisler
- `backend/Dockerfile` + `frontend/Dockerfile` – Multi-stage build
- `k8s/` – Kubernetes manifestleri
- `helm/qlink/` – Helm Chart
- `argocd/` – ArgoCD GitOps

### CI/CD
- `.github/workflows/ci.yml` – 6 aşamalı pipeline

### Monitoring
- `monitoring/prometheus.yml` – Prometheus konfigürasyonu
- `monitoring/grafana/` – Grafana dashboard ve provisioning

### Performans & API Test
- `performance/k6_test.js` – Yük testi
- `postman/QLink.postman_collection.json` – Newman collection

---

## Sunum Süre Dağılımı

| Bölüm | Süre |
|---|---|
| Proje Tanıtımı | 2 dakika |
| CI/CD Demo | 3 dakika |
| K8s + Grafana Demo | 3 dakika |
| E2E + Performans Demo | 4 dakika |
| Q&A | 8 dakika |
| **Toplam** | **20 dakika** |

---

*Bu belge şartname Ek C şablonuna göre hazırlanmıştır.*
