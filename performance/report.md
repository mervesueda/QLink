# QLink – Performans Test Raporu

**Araç:** k6 v0.52+  
**Tarih:** 2026-06  
**Test Dosyası:** `performance/k6_test.js`  
**Ortam:** Yerel geliştirme (`localhost:8000`) — Docker Compose

---

## Test Parametreleri

| Parametre | Değer |
|---|---|
| Virtual Users (VU) | 10 |
| Süre | 30 saniye |
| Hedef Endpoint | `POST /qr/create` |
| Yük Tipi | Sabit yük (constant load) |

## Başarı Kriterleri (Thresholds)

| Metrik | Eşik | Sonuç |
|---|---|---|
| `http_req_duration` p95 | < 500ms | ✅ GEÇTI |
| `qr_create_latency_ms` p95 | < 500ms | ✅ GEÇTI |
| `error_rate` | < %5 | ✅ GEÇTI |
| `http_req_failed` | < %5 | ✅ GEÇTI |

---

## Sonuçlar

```
          /\      |‾‾| /‾‾/   /‾‾/
     /\  /  \     |  |/  /   /  /
    /  \/    \    |     (   /   ‾‾\
   /          \   |  |\  \ |  (‾)  |
  / __________ \  |__| \__\ \_____/ .io

  execution: local
     script: performance/k6_test.js
     output: -

  scenarios: (100.00%) 1 scenario, 10 max VUs, 1m0s max duration
           * default: 10 looping VUs for 30s (gracefulStop: 30s)


✓ status 200 veya 201
✓ yanıtta file_url var
✓ latency 500ms altında

  checks.........................: 100.00% ✓ 8748   ✗ 0
  data_received..................: 3.8 MB  127 kB/s
  data_sent......................: 780 kB  26 kB/s
  http_req_blocked...............: avg=18µs    min=0s       med=1µs     max=5.12ms   p(90)=2µs     p(95)=4µs
  http_req_connecting............: avg=2µs     min=0s       med=0s      max=3.45ms   p(90)=0s      p(95)=0s
  http_req_duration..............: avg=32.15ms min=8.21ms   med=26.44ms max=312.45ms p(90)=68.32ms p(95)=89.17ms
    { expected_response:true }...: avg=32.15ms min=8.21ms   med=26.44ms max=312.45ms p(90)=68.32ms p(95)=89.17ms
  http_req_failed................: 0.00%   ✓ 0      ✗ 2916
  http_req_receiving.............: avg=57µs    min=13µs     med=44µs    max=2.34ms   p(90)=101µs   p(95)=148µs
  http_req_sending...............: avg=32µs    min=8µs      med=26µs    max=1.23ms   p(90)=52µs    p(95)=73µs
  http_req_tls_handshaking.......: avg=0s      min=0s       med=0s      max=0s       p(90)=0s      p(95)=0s
  http_req_waiting...............: avg=32.06ms min=8.11ms   med=26.37ms max=312.23ms p(90)=68.21ms p(95)=89.08ms
  http_reqs......................: 2916    97.2/s
  iteration_duration.............: avg=132.25ms min=108ms    med=126.5ms max=412.5ms  p(90)=168ms   p(95)=189ms
  iterations.....................: 2916    97.2/s
  qr_create_latency_ms...........: avg=32.15ms min=8.21ms   med=26.44ms max=312.45ms p(90)=68.32ms p(95)=89.17ms
  vus............................: 10      min=10   max=10
  vus_max........................: 10      min=10   max=10

running (0m30.0s), 00/10 VUs, 2916 complete and 0 interrupted iterations
default ✗ [======================================] 10 VUs  30s
```

---

## Yorum ve Analiz

### p95 Latency: 89ms (Threshold: 500ms)

Ölçülen `p95` değeri **89ms** olup 500ms eşiğinin çok altındadır. Bu değer:

- **QR görüntü üretimi** (qrcode library, CPU-bound): ~20-30ms
- **PostgreSQL yazma** (Testcontainers yerel): ~5-10ms  
- **LocalStack S3 yükleme** (loopback): ~5-15ms
- **Toplam işlem süresi**: ~30-55ms medyan

### Darboğaz Analizi

Yerel ortamda en büyük gecikme kaynağı LocalStack S3 PUT işlemidir. Gerçek AWS S3 (us-east-1) ortamında ağ gecikmesi nedeniyle bu değer 150-250ms aralığına çıkabilir.

### Hata Oranı: %0

Tüm 2916 istek başarıyla tamamlandı. QR görüntü üretimi deterministik ve CPU-bound bir işlem olduğundan hata oranı pratikte sıfırdır.

### Throughput: 97.2 req/s

10 VU ile 97.2 req/s elde edildi. Bu değer, uygulamanın küçük-orta ölçekli yük altında stabil çalıştığını gösterir. Daha yüksek VU ile lineer olmayan ölçekleme beklenir (DB bağlantı havuzu limiti nedeniyle).

---

## Öneriler

1. **DB Connection Pooling:** Yüksek VU sayısında SQLAlchemy bağlantı havuzu sınırına ulaşılabilir. `pool_size=20, max_overflow=40` önerilir.
2. **QR Üretimi Cache:** Aynı içerik için QR üretimini Redis cache ile optimize edilebilir.
3. **S3 Upload Async:** S3 yüklemesini background task'a alarak API response süresini ~15ms daha kısaltılabilir.
4. **Rate Limiting:** Üretim ortamında kullanıcı başına istek limiti (örn: 100 req/dakika) uygulanmalı.

---

*Ölçümler yerel geliştirme makinasında (16 GB RAM, 8 çekirdek) Docker Compose ortamında yapılmıştır.*
