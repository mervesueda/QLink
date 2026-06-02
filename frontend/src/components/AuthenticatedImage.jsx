// components/AuthenticatedImage.jsx
//
// Problem: Browser <img src="..."> tag'i Authorization header gönderemez.
// Bu nedenle JWT korumalı /qr/{id}/image endpoint'i <img> ile kullanılamaz.
//
// Çözüm: fetch() API'si Authorization header gönderebilir.
// Akış:
//   1. fetch('/qr/{id}/image', { headers: { Authorization: 'Bearer ...' } })
//   2. Response → Blob
//   3. URL.createObjectURL(blob) → blobUrl
//   4. <img src={blobUrl}> olarak render et
//   5. Component unmount'ta URL.revokeObjectURL(blobUrl) → bellek sızıntısı önle
//
// Bu desen; korunan görselleri authentication kaldırmadan render etmenin
// SaaS uygulamalarında (GitHub, Notion) standart yöntemidir.

import { useEffect, useRef, useState } from 'react'

/**
 * @param {string}  src       - Backend image URL'i (Authorization header gerektirir)
 * @param {string}  alt       - <img> alt text
 * @param {string}  className - CSS class
 * @param {...any}  rest      - Diğer img prop'ları
 */
export default function AuthenticatedImage({ src, alt = 'QR kod', className = '', ...rest }) {
  const [blobUrl, setBlobUrl] = useState(null)
  const [status, setStatus]   = useState('loading') // 'loading' | 'success' | 'error'
  const currentBlobUrl        = useRef(null)

  useEffect(() => {
    // src değiştiğinde önceki blob URL'ini temizle
    if (currentBlobUrl.current) {
      URL.revokeObjectURL(currentBlobUrl.current)
      currentBlobUrl.current = null
    }

    if (!src) {
      setStatus('error')
      return
    }

    let cancelled = false // Component unmount sonrası state güncellemesini önle

    const fetchImage = async () => {
      setStatus('loading')

      // localStorage'dan JWT token'ı al
      const token = localStorage.getItem('qlink_token')
      const headers = token ? { Authorization: `Bearer ${token}` } : {}

      try {
        const response = await fetch(src, { headers })

        if (!response.ok) {
          if (!cancelled) setStatus('error')
          return
        }

        const blob = await response.blob()
        if (cancelled) return // Unmount olduysa işlemi bırak

        const url = URL.createObjectURL(blob)
        currentBlobUrl.current = url
        setBlobUrl(url)
        setStatus('success')
      } catch {
        if (!cancelled) setStatus('error')
      }
    }

    fetchImage()

    // Cleanup: component unmount olduğunda veya src değiştiğinde
    return () => {
      cancelled = true
      if (currentBlobUrl.current) {
        URL.revokeObjectURL(currentBlobUrl.current)
        currentBlobUrl.current = null
      }
    }
  }, [src])

  if (status === 'loading') {
    return (
      <div
        className={className}
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          background: 'var(--surface-2, #1e1e2e)',
          borderRadius: 'var(--radius-sm, 6px)',
          border: '1px solid var(--border-subtle, #2d2d44)',
        }}
        {...rest}
        aria-label="Yükleniyor..."
      >
        <span
          style={{
            width: 20,
            height: 20,
            borderRadius: '50%',
            border: '2px solid var(--accent, #7c3aed)',
            borderTopColor: 'transparent',
            animation: 'spin 0.8s linear infinite',
            display: 'inline-block',
          }}
        />
      </div>
    )
  }

  if (status === 'error') {
    return (
      <div
        className={className}
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          background: 'var(--surface-2, #1e1e2e)',
          borderRadius: 'var(--radius-sm, 6px)',
          border: '1px solid var(--border-subtle, #2d2d44)',
          fontSize: '1.5rem',
          color: 'var(--text-muted, #6b7280)',
        }}
        {...rest}
        aria-label="Görsel yüklenemedi"
        title="QR görseli yüklenemedi"
      >
        🔲
      </div>
    )
  }

  return (
    <img
      src={blobUrl}
      alt={alt}
      className={className}
      {...rest}
    />
  )
}
