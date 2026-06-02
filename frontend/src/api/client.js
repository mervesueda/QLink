// api/client.js – Axios instance ve API fonksiyonları.
//
// Tek bir axios instance kullanmak:
//   - Base URL'i bir yerde tutar (env değişkeni)
//   - Token'ı her istekte otomatik ekler (interceptor)
//   - Hata yönetimini merkezileştirir
//
// ÖNEMLI NOT — Neden fetch+Blob kullanıyoruz:
// Browser <img src> ve <a href> tag'leri HTTP isteği yaparken
// custom header (Authorization: Bearer ...) gönderemez.
// Bu nedenle JWT korumalı endpoint'lere bu yollarla erişim 401 döner.
// Çözüm: fetch() API'si header gönderebilir → Blob URL üretilir → img/a'ya verilir.

import axios from 'axios'

// Docker Compose'da backend servisi "backend" adıyla; yerel geliştirmede proxy devreye girer
const BASE_URL = import.meta.env.VITE_API_URL || ''

const api = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 10000,
})

// Her istekte localStorage'daki token'ı Authorization header'ına ekle
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('qlink_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 401 gelirse token'ı temizle (oturum süresi doldu)
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('qlink_token')
      localStorage.removeItem('qlink_user')
    }
    return Promise.reject(err)
  },
)

// ── Auth API ──────────────────────────────────────────────────

export const register = (email, password) =>
  api.post('/auth/register', { email, password })

export const login = (email, password) =>
  api.post('/auth/login', { email, password })

// ── QR API ───────────────────────────────────────────────────

export const createQR = (content, qr_type) =>
  api.post('/qr/create', { content, qr_type })

export const listQR = () =>
  api.get('/qr/list')

export const getQR = (id) =>
  api.get(`/qr/${id}`)

export const deleteQR = (id) =>
  api.delete(`/qr/${id}`)

// Belirli bir QR'ın PNG görselini backend'den sunan URL.
// AuthenticatedImage bileşeni tarafından fetch() ile kullanılır (header gönderilebilir).
export const getQRImageUrl = (id) => `${BASE_URL}/qr/${id}/image`

// QR PNG'yi indirme URL'i — doğrudan kullanılamaz (<a href> header gönderemez).
// downloadQRBlob() fonksiyonu bu URL'i fetch() ile çağırarak güvenli indirme sağlar.
export const getQRDownloadUrl = (id) => `${BASE_URL}/qr/${id}/image?download=true`

/**
 * QR görselini JWT kimlik doğrulamasıyla indirir.
 *
 * Neden <a href> yerine fetch+Blob:
 *   - <a href="/qr/{id}/image?download=true"> navigasyonu Authorization header göndermez
 *   - Backend 401 döner → indirme başlamaz, 401 sayfası açılır
 *   - fetch() API'si header gönderebilir → Blob URL → programmatik download
 *
 * @param {string} id  - QR kod UUID
 * @param {string} filename - İndirilecek dosya adı
 */
export const downloadQRBlob = async (id, filename = `qlink-${id}.png`) => {
  const token = localStorage.getItem('qlink_token')
  const headers = token ? { Authorization: `Bearer ${token}` } : {}

  const response = await fetch(getQRDownloadUrl(id), { headers })

  if (!response.ok) {
    throw new Error(`İndirme başarısız: HTTP ${response.status}`)
  }

  const blob = await response.blob()
  const blobUrl = URL.createObjectURL(blob)

  // Programatik download tetikle
  const a = document.createElement('a')
  a.href = blobUrl
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)

  // Blob URL'ini serbest bırak (bellek sızıntısı önle)
  URL.revokeObjectURL(blobUrl)
}

export default api
