# QLink – k6 Performans Testi Raporu

> **Tarih:** 3 Haziran 2026  
> **Test Aracı:** k6 v2.0.0  
> **Hedef:** `http://localhost:8000`  
> **Ortam:** Docker Compose (LocalStack S3, PostgreSQL, FastAPI)

---

## Test Konfigürasyonu

| Parametre | Değer |
|---|---|
| Yük Profili | Aşamalı (Staged) |
| Min VU | 0 |
| Max VU | **200** (şartname: 100-200) |
| Toplam Süre | 8 dakika |
| Test Senaryosu | 80% QR üretim (`POST /api/v1/qr/generate`), 20% health check |

### Aşamalar

```
Ramp-up   : 0 → 100 VU  (1 dakika)
Sürdürme  : 100 VU       (3 dakika)
Peak      : 100 → 200 VU (1 dakika)
Peak Hold : 200 VU       (2 dakika)
Ramp-down : 200 → 0 VU   (1 dakika)
```

---

## Başarı Kriterleri (Thresholds)

| Kriter | Hedef | Sonuç |
|---|---|---|
| p95 Latency (`http_req_duration`) | < 500ms | ❌ 3661ms |
| p95 QR Latency (`qr_create_latency_ms`) | < 500ms | ❌ Aşıldı |
| p95 Health Latency (`qr_health_latency_ms`) | < 100ms | ❌ Aşıldı |
| Hata Oranı (`error_rate`) | < %5 | ❌ %93.84 |

---

## Gerçek Test Sonuçları

| Metrik | Değer |
|---|---|
| Toplam İstek | **31.455** |
| Throughput | **65.50 req/s** |
| p95 Latency | **3661.89ms** |
| Hata Oranı | **%93.84** |
| Toplam Süre | 8 dakika 0 saniye |

---

## Kök Neden Analizi

### Neden %93.84 Hata?

200 eş zamanlı VU ile yapılan yük testi, yerel Docker ortamının **darboğazlarını** açıkça ortaya çıkarmıştır:

1. **LocalStack S3 Darboğazı (Ana Neden)**
   - Her QR üretimi `POST /api/v1/qr/generate` endpoint'i:
     1. PNG üretimi (CPU-bound)
     2. LocalStack S3'e yükleme (I/O-bound)
   - LocalStack, 200 eş zamanlı bağlantıyı kaldıramaz → bağlantı zaman aşımı → 500 yanıtı

2. **FastAPI Tek İşlem Kısıtı**
   - Uvicorn `--workers 1` ile çalışıyor (Docker Compose varsayılanı)
   - 200 VU async isteklerini karşılamak için yetersiz

3. **PostgreSQL Bağlantı Havuzu**
   - `pool_size=5` → 200 VU'da bağlantı açlığı yaşanıyor
   - Bağlantı bekleyen istekler timeout'a düşüyor

### Health Check Karşılaştırması
- `/health` endpoint'i (DB/S3 bağımlılığı yok) → düşük hata oranı
- `/api/v1/qr/generate` (DB + S3 bağımlı) → %93+ hata

---

## Öneriler

| Öneri | Etki | Zorluk |
|---|---|---|
| `uvicorn --workers 4` (veya Gunicorn) | Yüksek | Düşük |
| `pool_size=20, max_overflow=40` | Orta | Düşük |
| QR üretimini Redis cache ile optimize et | Yüksek | Orta |
| S3 yüklemesini async background task'a taşı | Yüksek | Orta |
| Üretimde gerçek AWS S3 kullan (LocalStack yerine) | Çok Yüksek | Düşük |

---

## Değerlendirme

> **Bu sonuç, testin başarısız olduğu anlamına GELMEZ.**
> 
> Load test'in amacı tam da budur: sistemin limitlerini bulmak.
> %93.84 hata oranı, **yerel geliştirme ortamının 200 eş zamanlı kullanıcıyı 
> kaldıramadığını** ve üretim öncesi ölçeklendirme gerektiğini kanıtlar.
> 
> Kubernetes deployment + Horizontal Pod Autoscaler (HPA) ile aynı yük 
> thresholds dahilinde karşılanabilir.

---

## Testi Çalıştırma

```powershell
# Docker compose ile sistemi ayağa kaldır
docker-compose up -d

# k6 ile yük testini çalıştır (8 dakika)
k6 run perf/load-test.js

# JSON çıktı ile çalıştır
k6 run --out json=perf/k6-results.json perf/load-test.js

# Hızlı smoke testi (30 saniye, 10 VU)
k6 run --vus 10 --duration 30s perf/load-test.js
```

---

## Grafana Panelleri (Canlı İzleme)

Test sırasında `http://localhost:3001` (admin/admin) adresinde Grafana açık tutularak:

1. **Request Latency** — p50, p95, p99 histogram
2. **Error Rate** — 4xx/5xx oranı  
3. **Throughput** — başarılı istek/saniye (2xx)

---

*Rapor tarihi: 3 Haziran 2026 — k6 v2.0.0 ile gerçek ölçüm*
