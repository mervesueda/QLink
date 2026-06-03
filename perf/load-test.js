/**
 * performance/k6_test.js – QLink yük testi (Şartname: 100-200 eşzamanlı kullanıcı)
 *
 * Aşamalı yük profili:
 *   Ramp-up  : 0 → 100 VU (1 dakika)
 *   Sürdürme : 100 VU     (3 dakika)
 *   Peak     : 100 → 200 VU (1 dakika)
 *   Sürdürme : 200 VU     (2 dakika)
 *   Ramp-down: 200 → 0 VU  (1 dakika)
 *
 * Çalıştırma:
 *   k6 run performance/k6_test.js
 *   k6 run --out json=performance/results.json performance/k6_test.js
 *   BASE_URL=http://localhost:8000 k6 run performance/k6_test.js
 *
 * Sonuç: performance/report.md dosyasına kaydedin.
 */

import { check, sleep } from 'k6'
import http from 'k6/http'
import { Rate, Trend } from 'k6/metrics'

// ── Özel metrikler ──────────────────────────────────────────────────────────

const qrCreateLatency = new Trend('qr_create_latency_ms', true)
const qrHealthLatency = new Trend('qr_health_latency_ms', true)
const errorRate = new Rate('error_rate')

// ── Test konfigürasyonu ─────────────────────────────────────────────────────

export const options = {
  // Şartname: 100-200 eşzamanlı kullanıcı
  stages: [
    { duration: '1m', target: 100 },   // Ramp-up: 0 → 100 VU
    { duration: '3m', target: 100 },   // Sürdürme: 100 VU
    { duration: '1m', target: 200 },   // Peak: 100 → 200 VU
    { duration: '2m', target: 200 },   // Peak sürdürme: 200 VU
    { duration: '1m', target: 0 },     // Ramp-down: 200 → 0 VU
  ],

  thresholds: {
    // Şartname: p95 latency < 500ms
    http_req_duration: ['p(95)<500'],
    qr_create_latency_ms: ['p(95)<500'],
    qr_health_latency_ms: ['p(95)<100'],
    // Hata oranı %5'in altında olmalı
    error_rate: ['rate<0.05'],
    http_req_failed: ['rate<0.05'],
  },
}

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000'

// ── Senaryo: 80% QR üret, 20% health check ─────────────────────────────────

export default function () {
  const rand = Math.random()

  if (rand < 0.80) {
    // Senaryo A: Misafir QR üretimi (ana yük)
    const payload = JSON.stringify({
      content: `https://loadtest.example.com/${Math.random().toString(36).substring(7)}`,
      qr_type: 'url',
    })

    const res = http.post(`${BASE_URL}/api/v1/qr/generate`, payload, {
      headers: { 'Content-Type': 'application/json' },
      tags: { name: 'QRGenerate' },
    })

    qrCreateLatency.add(res.timings.duration)

    const success = check(res, {
      'QR generate: status 201': (r) => r.status === 201,
      'QR generate: has file_url': (r) => {
        try {
          return JSON.parse(r.body).file_url !== undefined
        } catch { return false }
      },
      'QR generate: has image_data': (r) => {
        try {
          return JSON.parse(r.body).image_data !== undefined
        } catch { return false }
      },
      'QR generate: latency < 500ms': (r) => r.timings.duration < 500,
    })

    errorRate.add(!success)

  } else {
    // Senaryo B: Health check (düşük yük baseline)
    const res = http.get(`${BASE_URL}/health`, {
      tags: { name: 'HealthCheck' },
    })

    qrHealthLatency.add(res.timings.duration)

    check(res, {
      'Health: status 200': (r) => r.status === 200,
      'Health: latency < 100ms': (r) => r.timings.duration < 100,
    })
  }

  // Gerçekçi kullanım simülasyonu: 100-300ms bekleme
  sleep(Math.random() * 0.2 + 0.1)
}

// ── handleSummary: k6 summary'i JSON olarak kaydet ─────────────────────────

export function handleSummary(data) {
  return {
    'perf/k6_summary.json': JSON.stringify(data, null, 2),
    stdout: textSummary(data, { indent: ' ', enableColors: true }),
  }
}

function textSummary(data, opts) {
  const p95 = data.metrics['http_req_duration']?.values?.['p(95)'] || 'N/A'
  const p99 = data.metrics['http_req_duration']?.values?.['p(99)'] || 'N/A'
  const rps = data.metrics['http_reqs']?.values?.rate || 0
  const errorRateVal = data.metrics['error_rate']?.values?.rate || 0

  return `
╔══════════════════════════════════════════════════╗
║        QLink k6 Yük Testi Sonuçları              ║
╠══════════════════════════════════════════════════╣
║  p95 Latency : ${String(typeof p95 === 'number' ? p95.toFixed(2) + 'ms' : p95).padEnd(32)}║
║  p99 Latency : ${String(typeof p99 === 'number' ? p99.toFixed(2) + 'ms' : p99).padEnd(32)}║
║  Throughput  : ${String(typeof rps === 'number' ? rps.toFixed(2) + ' req/s' : rps).padEnd(32)}║
║  Error Rate  : ${String(typeof errorRateVal === 'number' ? (errorRateVal * 100).toFixed(2) + '%' : errorRateVal).padEnd(32)}║
╚══════════════════════════════════════════════════╝
`
}
