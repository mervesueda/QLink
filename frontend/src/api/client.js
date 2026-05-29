// api/client.js – Axios instance ve API fonksiyonları.
//
// Tek bir axios instance kullanmak:
//   - Base URL'i bir yerde tutar (env değişkeni)
//   - Token'ı her istekte otomatik ekler (interceptor)
//   - Hata yönetimini merkezileştirir

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

export default api
