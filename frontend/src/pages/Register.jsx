// pages/Register.jsx – Kayıt sayfası.

import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../store/authStore'
import styles from './Auth.module.css'

export default function Register() {
  const { register, isAuthenticated } = useAuth()
  const navigate = useNavigate()

  const [email, setEmail]       = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading]   = useState(false)
  const [error, setError]       = useState('')

  if (isAuthenticated) { navigate('/my-qrs'); return null }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      await register(email, password)
      // Kayıt sonrası giriş sayfasına yönlendir
      navigate('/login')
    } catch (err) {
      const detail = err.response?.data?.detail
      setError(Array.isArray(detail) ? detail[0]?.msg : detail || 'Kayıt başarısız.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="page">
      <div className="container">
        <div className={styles.wrapper}>
          <div className={styles.header}>
            <h1>Kayıt Ol</h1>
            <p>Ücretsiz hesap oluşturun</p>
          </div>

          <form onSubmit={handleSubmit} className={`card ${styles.form}`} id="register-form">
            <div className="form-group">
              <label className="form-label" htmlFor="register-email">E-posta</label>
              <input
                id="register-email"
                className="form-input"
                type="email"
                placeholder="ornek@eposta.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                autoFocus
              />
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="register-password">Şifre</label>
              <input
                id="register-password"
                className="form-input"
                type="password"
                placeholder="En az 8 karakter"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                minLength={8}
                required
              />
            </div>

            {error && <div className="alert alert-error">{error}</div>}

            <button
              type="submit"
              className="btn btn-primary w-full"
              disabled={loading}
              id="register-submit"
            >
              {loading ? <><span className="spinner" /> Kayıt yapılıyor...</> : 'Kayıt Ol'}
            </button>

            <p className={styles.switchLink}>
              Zaten hesabınız var mı?{' '}
              <Link to="/login" id="goto-login">Giriş Yap</Link>
            </p>
          </form>
        </div>
      </div>
    </main>
  )
}
