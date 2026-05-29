// components/Navbar.jsx – Üst navigasyon çubuğu.
//
// Misafir: Anasayfa, QR Oluştur, Giriş Yap, Kayıt Ol
// Giriş yapılmış: Anasayfa, QR Oluştur, QR'larım, Çıkış

import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../store/authStore'
import styles from './Navbar.module.css'

export default function Navbar() {
  const { isAuthenticated, user, logout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  const handleLogout = () => {
    logout()
    navigate('/')
  }

  const isActive = (path) => location.pathname === path

  return (
    <nav className={styles.navbar}>
      <div className={styles.inner}>
        {/* Logo */}
        <Link to="/" className={styles.logo} id="navbar-logo">
          <span className={styles.logoIcon}>Q</span>
          <span className={styles.logoText}>Link</span>
        </Link>

        {/* Nav linkleri */}
        <div className={styles.links}>
          <Link
            to="/"
            className={`${styles.link} ${isActive('/') ? styles.active : ''}`}
            id="nav-home"
          >
            Anasayfa
          </Link>
          <Link
            to="/create"
            className={`${styles.link} ${isActive('/create') ? styles.active : ''}`}
            id="nav-create"
          >
            QR Oluştur
          </Link>
          {isAuthenticated && (
            <Link
              to="/my-qrs"
              className={`${styles.link} ${isActive('/my-qrs') ? styles.active : ''}`}
              id="nav-my-qrs"
            >
              QR'larım
            </Link>
          )}
        </div>

        {/* Auth alanı */}
        <div className={styles.auth}>
          {isAuthenticated ? (
            <>
              <span className={styles.userEmail} id="navbar-user-email">
                {user?.email}
              </span>
              <button
                className="btn btn-ghost"
                onClick={handleLogout}
                id="navbar-logout"
              >
                Çıkış
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="btn btn-ghost" id="nav-login">
                Giriş Yap
              </Link>
              <Link to="/register" className="btn btn-primary" id="nav-register">
                Kayıt Ol
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  )
}
