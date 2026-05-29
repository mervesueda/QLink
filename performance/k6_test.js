/**
 * performance/k6_test.js – QLink performans testi
 *
 * k6 ile POST /qr/create endpoint'i üzerinde yük testi yapılır.
 * Şartname gereksinimleri:
 *   - p95 latency ölçülür
 *   - Sonuçlar raporlanır
 *
 * Çalıştırma:
 *   k6 run performance/k6_test.js
 *   k6 run --out json=results.json performance/k6_test.js
 *   BASE_URL=http://localhost:8000 k6 run performance/k6_test.js
 */

import { check, sleep } from 'k6'
import http from 'k6/http'
import { Rate, Trend } from 'k6/metrics'

// ── Özel metrikler ──────────────────────────────────────────────────────────

// QR oluşturma endpoint'i için ayrı latency ölçümü
const qrCreateLatency = new Trend('qr_create_latency_ms', true)

// Başarısız istek oranı
const errorRate = new Rate('error_rate')

// ── Test konfigürasyonu ─────────────────────────────────────────────────────

export const options = {
  // Yük profili: 10 virtual user, 30 saniye boyunca
  vus: 10,
  duration: '30s',

  // Başarı eşikleri: bunlardan herhangi biri ihlallenirse test BAŞARISIZ sayılır
  thresholds: {
    // p95 latency 500ms altında olmalı (şartname)
    http_req_duration: ['p(95)<500'],
    qr_create_latency_ms: ['p(95)<500'],
    // Hata oranı %5'in altında olmalı
    error_rate: ['rate<0.05'],
    // HTTP istek başarı oranı %95'in üzerinde olmalı
    http_req_failed: ['rate<0.05'],
  },
}

// ── Yardımcı: URL ortam değişkeninden al veya varsayılanı kullan ─────────────

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000'

// ── Test senaryosu ──────────────────────────────────────────────────────────

export default function () {
  // Test payload'ı: misafir kullanıcı QR oluşturur (auth gerektirmez)
  const payload = JSON.stringify({
    content: `https://loadtest.example.com/${Math.random().toString(36).substring(7)}`,
    qr_type: 'url',
  })

  const params = {
    headers: { 'Content-Type': 'application/json' },
    tags: { name: 'QRCreate' },  // Grafana'da gruplayabilmek için tag
  }

  const res = http.post(`${BASE_URL}/qr/create`, payload, params)

  // Özel metriğe latency değerini ekle
  qrCreateLatency.add(res.timings.duration)

  // Hata kontrolü
  const success = check(res, {
    'status 200 veya 201': (r) => r.status === 200 || r.status === 201,
    'yanıtta file_url var': (r) => {
      try {
        const body = JSON.parse(r.body)
        return typeof body.file_url === 'string' && body.file_url.length > 0
      } catch {
        return false
      }
    },
    'latency 500ms altında': (r) => r.timings.duration < 500,
  })

  // Başarısızsa error_rate metriğine kaydet
  errorRate.add(!success)

  // Virtual user'lar arasında kısa bekleme (gerçekçi kullanım simülasyonu)
  sleep(0.1)
}

// ── Test sonu özeti ─────────────────────────────────────────────────────────
// k6 otomatik olarak stdout'a summary basar:
//   - http_req_duration (min, avg, max, p90, p95, p99)
//   - qr_create_latency_ms
//   - error_rate
//   - http_reqs (toplam istek sayısı)
