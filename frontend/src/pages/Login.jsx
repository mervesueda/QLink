// pages/Login.jsx – Giriş sayfası.

import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../store/authStore.jsx'
import styles from './Auth.module.css'

export default function Login() {
  const { login, isAuthenticated } = useAuth()
  const navigate = useNavigate()

  const [email, setEmail]       = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading]   = useState(false)
  const [error, setError]       = useState('')

  // Zaten giriş yapılmışsa yönlendir
  if (isAuthenticated) { navigate('/my-qrs'); return null }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      await login(email, password)
      navigate('/my-qrs')
    } catch (err) {
      setError(err.response?.data?.detail || 'Giriş başarısız.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="page">
      <div className="container">
        <div className={styles.wrapper}>
          <div className={styles.header}>
            <h1>Giriş Yap</h1>
            <p>Hesabınıza giriş yapın</p>
          </div>

          <form onSubmit={handleSubmit} className={`card ${styles.form}`} id="login-form">
            <div className="form-group">
              <label className="form-label" htmlFor="login-email">E-posta</label>
              <input
                id="login-email"
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
              <label className="form-label" htmlFor="login-password">Şifre</label>
              <input
                id="login-password"
                className="form-input"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>

            {error && <div className="alert alert-error">{error}</div>}

            <button
              type="submit"
              className="btn btn-primary w-full"
              disabled={loading}
              id="login-submit"
            >
              {loading ? <><span className="spinner" /> Giriş yapılıyor...</> : 'Giriş Yap'}
            </button>

            <p className={styles.switchLink}>
              Hesabınız yok mu?{' '}
              <Link to="/register" id="goto-register">Kayıt Ol</Link>
            </p>
          </form>
        </div>
      </div>
    </main>
  )
}
