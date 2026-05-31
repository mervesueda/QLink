// pages/MyQRs.jsx – Kullanıcının QR listesi (auth-gated).
// ProtectedRoute tarafından sarmalandığından burada auth kontrolü yok.

import { useCallback, useEffect, useState } from 'react'
import { deleteQR, getQRDownloadUrl, getQRImageUrl, listQR } from '../api/client'
import styles from './MyQRs.module.css'

function QRItem({ qr, onDelete }) {
  const [deleting, setDeleting] = useState(false)

  const handleDelete = async () => {
    if (!window.confirm('Bu QR kodu silinsin mi?')) return
    setDeleting(true)
    try {
      await deleteQR(qr.id)
      onDelete(qr.id)
    } catch {
      alert('Silme işlemi başarısız oldu.')
    } finally {
      setDeleting(false)
    }
  }

  const handleDownload = () => {
    // Backend'den doğrudan PNG olarak indirir (S3 URL'si yerine backend proxy kullanılır)
    const a = document.createElement('a')
    a.href = getQRDownloadUrl(qr.id)
    a.download = `qlink-${qr.id}.png`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
  }

  const formatDate = (dateStr) =>
    new Date(dateStr).toLocaleDateString('tr-TR', {
      day: '2-digit', month: 'short', year: 'numeric',
    })

  return (
    <div className={`card ${styles.qrItem}`} id={`qr-item-${qr.id}`}>
      <img
        src={getQRImageUrl(qr.id)}
        alt="QR kod"
        className={styles.thumbnail}
        loading="lazy"
      />
      <div className={styles.info}>
        <span className={`badge badge-${qr.qr_type}`}>{qr.qr_type}</span>
        <p className={styles.content} title={qr.content}>{qr.content}</p>
        <span className="text-muted">{formatDate(qr.created_at)}</span>
      </div>
      <div className={styles.actions}>
        <button className="btn btn-ghost" onClick={handleDownload} id={`download-${qr.id}`}>
          ↓ İndir
        </button>
        <button
          className="btn btn-danger"
          onClick={handleDelete}
          disabled={deleting}
          id={`delete-${qr.id}`}
        >
          {deleting ? '...' : 'Sil'}
        </button>
      </div>
    </div>
  )
}

export default function MyQRs() {
  const [qrs, setQrs]       = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError]   = useState('')

  const fetchQRs = useCallback(async () => {
    setLoading(true)
    try {
      const res = await listQR()
      setQrs(res.data)
    } catch {
      setError('QR kodları yüklenirken bir hata oluştu.')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetchQRs() }, [fetchQRs])

  const handleDelete = (id) => setQrs((prev) => prev.filter((q) => q.id !== id))

  if (loading) {
    return (
      <main className="page">
        <div className="container flex-center" style={{ minHeight: 300 }}>
          <span className="spinner" style={{ width: 36, height: 36 }} />
        </div>
      </main>
    )
  }

  return (
    <main className="page">
      <div className="container">
        <div className={styles.header}>
          <h1>QR'larım</h1>
          <p>{qrs.length > 0 ? `${qrs.length} QR kod bulundu` : 'Henüz QR kodunuz yok'}</p>
        </div>

        {error && <div className="alert alert-error mt-4">{error}</div>}

        {qrs.length === 0 && !error ? (
          <div className={`card ${styles.empty}`} id="empty-state">
            <span style={{ fontSize: '3rem' }}>🔲</span>
            <h3>Henüz QR kodunuz yok</h3>
            <p>İlk QR kodunuzu oluşturmak için <a href="/create" style={{ color: '#c4b5fd' }}>buraya tıklayın</a>.</p>
          </div>
        ) : (
          <div className={styles.list} id="qr-list">
            {qrs.map((qr) => (
              <QRItem key={qr.id} qr={qr} onDelete={handleDelete} />
            ))}
          </div>
        )}
      </div>
    </main>
  )
}
