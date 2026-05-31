// pages/CreateQR.jsx – QR oluşturma sayfası.
//
// Akış:
//   1. Kullanıcı içerik tipini seçer (URL / Metin / E-posta)
//   2. İçeriği girer
//   3. "Oluştur" butonuna basar → API çağrısı
//   4. QR görüntülenir + indir butonu
//   5. Misafir kullanıcıya "kayıt ol" kartı gösterilir (şartname)

import { useState } from 'react'
import { Link } from 'react-router-dom'
import { createQR } from '../api/client'
import { useAuth } from '../store/authStore.jsx'
import styles from './CreateQR.module.css'

const QR_TYPES = [
  { value: 'url',   label: 'URL',     placeholder: 'https://example.com' },
  { value: 'text',  label: 'Metin',   placeholder: 'Metin içeriğini gir...' },
  { value: 'email', label: 'E-posta', placeholder: 'ornek@eposta.com' },
]

export default function CreateQR() {
  const { isAuthenticated } = useAuth()
  const [qrType, setQrType]     = useState('url')
  const [content, setContent]   = useState('')
  const [result, setResult]     = useState(null)   // API yanıtı
  const [loading, setLoading]   = useState(false)
  const [error, setError]       = useState('')

  const selectedType = QR_TYPES.find((t) => t.value === qrType)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!content.trim()) return

    setLoading(true)
    setError('')
    setResult(null)

    try {
      const res = await createQR(content.trim(), qrType)
      setResult(res.data)
    } catch (err) {
      const msg = err.response?.data?.detail || 'Bir hata oluştu. Tekrar deneyin.'
      setError(Array.isArray(msg) ? msg[0]?.msg : msg)
    } finally {
      setLoading(false)
    }
  }

  const handleDownload = () => {
    // image_data varsa doğrudan indir (S3'ten bağımsız)
    const src = result.image_data || result.file_url
    const a = document.createElement('a')
    a.href = src
    a.download = `qlink-${Date.now()}.png`
    if (!result.image_data) a.target = '_blank'
    a.click()
  }

  const handleReset = () => {
    setResult(null)
    setContent('')
    setError('')
  }

  return (
    <main className="page">
      <div className="container">
        <div className={styles.wrapper}>
          <div className={styles.header}>
            <h1>QR Oluştur</h1>
            <p>URL, metin veya e-posta adresinden QR kodu oluştur</p>
          </div>

          {!result ? (
            /* ── Form ─────────────────────────────────────── */
            <form onSubmit={handleSubmit} className={`card ${styles.form}`} id="qr-form">
              {/* Tip seçici */}
              <div className={styles.typeSelector}>
                {QR_TYPES.map((t) => (
                  <button
                    key={t.value}
                    type="button"
                    className={`${styles.typeBtn} ${qrType === t.value ? styles.typeActive : ''}`}
                    onClick={() => { setQrType(t.value); setContent('') }}
                    id={`type-${t.value}`}
                  >
                    {t.label}
                  </button>
                ))}
              </div>

              {/* İçerik girişi */}
              <div className="form-group">
                <label className="form-label" htmlFor="qr-content">
                  {selectedType.label} İçeriği
                </label>
                <input
                  id="qr-content"
                  className="form-input"
                  type={qrType === 'email' ? 'email' : 'text'}
                  placeholder={selectedType.placeholder}
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  required
                  autoFocus
                />
              </div>

              {error && <div className="alert alert-error">{error}</div>}

              <button
                type="submit"
                className="btn btn-primary w-full"
                disabled={loading || !content.trim()}
                id="submit-qr"
              >
                {loading ? <><span className="spinner" /> Oluşturuluyor...</> : 'QR Oluştur →'}
              </button>
            </form>
          ) : (
            /* ── Sonuç ────────────────────────────────────── */
            <div className={styles.result} id="qr-result">
              <div className={`card ${styles.qrCard}`}>
                <img
                  src={result.image_data || result.file_url}
                  alt="Oluşturulan QR kod"
                  className={styles.qrImage}
                  id="qr-image"
                />
                <div className={styles.qrMeta}>
                  <span className={`badge badge-${result.qr_type}`}>{result.qr_type}</span>
                  <p className={styles.qrContent}>{result.content}</p>
                </div>
                <div className={styles.qrActions}>
                  <button
                    className="btn btn-primary"
                    onClick={handleDownload}
                    id="download-qr"
                  >
                    ↓ İndir (PNG)
                  </button>
                  <button className="btn btn-ghost" onClick={handleReset} id="new-qr">
                    Yeni Oluştur
                  </button>
                </div>
              </div>

              {/* Şartname: Misafir kullanıcıya kayıt ol kartı */}
              {!isAuthenticated && (
                <div className={`card ${styles.saveCard}`} id="save-prompt">
                  <div className={styles.saveCardIcon}>💾</div>
                  <h3>Bu QR kodunu daha sonra da yönetmek ister misiniz?</h3>
                  <p>
                    Ücretsiz hesap açarak tüm QR kodlarınıza istediğiniz zaman ulaşın,
                    yönetin ve paylaşın.
                  </p>
                  <div className="flex gap-2 mt-4">
                    <Link to="/register" className="btn btn-primary" id="save-register">
                      Ücretsiz Kayıt Ol
                    </Link>
                    <Link to="/login" className="btn btn-ghost" id="save-login">
                      Giriş Yap
                    </Link>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </main>
  )
}
