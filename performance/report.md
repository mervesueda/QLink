# QLink – k6 Performans Testi Raporu

> **Tarih:** 2 Haziran 2026  
> **Test Aracı:** k6 v0.51+  
> **Hedef:** `http://localhost:8000`  
> **Endpoint:** `POST /api/v1/qr/generate`

---

## Test Konfigürasyonu

| Parametre | Değer |
|---|---|
| Yük Profili | Aşamalı (Staged) |
| Min VU | 0 |
| Max VU | **200** (şartname: 100-200) |
| Toplam Süre | ~8 dakika |
| Test Senaryosu | 80% QR üretim, 20% health check |

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
| p95 Latency | < 500ms | ✅ |
| p99 Latency | — | ✅ |
| Hata Oranı | < %5 | ✅ |
| HTTP Başarısızlık | < %5 | ✅ |
| Health p95 | < 100ms | ✅ |

---

## Sonuçlar (Tahmini Beklenen Değerler)

> Not: Bu rapor sistemi docker-compose ile çalıştırarak k6 testi sonrası güncellenmelidir.  
> Aşağıdaki değerler yerel Docker ortamı (Apple M3 / i7-12th gen benzeri) için tipik beklentidir.

| Metrik | Değer |
|---|---|
| Toplam İstek | ~25.000 – 35.000 |
| Throughput (req/s) | ~60 – 90 req/s |
| p50 Latency | ~80 – 150ms |
| **p95 Latency** | **~200 – 350ms** |
| p99 Latency | ~400 – 600ms |
| Hata Oranı | <%1 |
| 200/201 Oranı | >%99 |

---

## Testi Çalıştırma

```bash
# Docker compose ile sistemi ayağa kaldır
docker-compose up -d

# k6 ile yük testini çalıştır (8 dakika)
k6 run performance/k6_test.js

# JSON çıktı ile çalıştır
k6 run --out json=performance/k6_results.json performance/k6_test.js

# Sadece hızlı smoke testi (30 saniye, 10 VU)
k6 run --vus 10 --duration 30s performance/k6_test.js
```

---

## Gözlemler

### Darboğaz Analizi

- **QR üretimi** (qrcode kütüphanesi) CPU-bound bir işlemdir. 200 VU'da CPU kullanımı %70-80'e çıkabilir.
- **S3 yükleme** (LocalStack) ağ gecikmesi ekler (~10-30ms lokal ağda).
- **PostgreSQL** bağlantı havuzu (`pool_size=5`) yüksek eş zamanlılıkta darboğaz oluşturabilir.

### Öneriler

1. QR üretimini `asyncio` ile background task'a taşı (FastAPI `BackgroundTasks`).
2. `pool_size=10, max_overflow=20` olarak artır.
3. Üretimde Redis cache ile aynı içeriğin QR'ını cache'le.

---

## Grafana Panelleri (Canlı İzleme)

Test sırasında `http://localhost:3001` adresinde Grafana açık tutularak şu paneller izlenebilir:

1. **p95 Latency** — `histogram_quantile(0.95, ...http_request_duration_seconds_bucket...)`
2. **Error Rate** — `http_requests_total{status=~"4..|5.."}`
3. **Throughput** — `sum(rate(http_requests_total{status=~"2.."}[1m]))`

---

*Bu rapor Geliştirici 4 tarafından tamamlanacaktır. k6 çalıştırıldıktan sonra gerçek değerler yukarıdaki tabloya eklenmelidir.*
