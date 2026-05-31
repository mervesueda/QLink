// pages/HomePage.jsx – Landing page.
// Projeyi tanıtan basit ama temiz bir karşılama ekranı.

import { Link } from 'react-router-dom'
import { useAuth } from '../store/authStore.jsx'
import styles from './HomePage.module.css'

const FEATURES = [
  {
    icon: '⚡',
    title: 'Anında Oluştur',
    desc: 'URL, metin veya e-posta içeriğini saniyeler içinde QR koda dönüştür.',
  },
  {
    icon: '☁️',
    title: 'Bulutta Sakla',
    desc: 'Oluşturulan QR kodlar AWS S3 üzerinde güvenle depolanır.',
  },
  {
    icon: '📋',
    title: 'Geçmişini Yönet',
    desc: 'Giriş yapan kullanıcılar tüm QR kodlarını görüntüleyip silebilir.',
  },
]

export default function HomePage() {
  const { isAuthenticated } = useAuth()

  return (
    <main className="page">
      <div className="container">
        {/* Hero */}
        <section className={styles.hero} id="hero">
          <div className={styles.badge}>Cloud-Native QR Platform</div>
          <h1>
            QR kodlarını oluştur,{' '}
            <span className="gradient-text">bulutta sakla</span>
          </h1>
          <p className={styles.subtitle}>
            Hızlı, güvenilir ve açık kaynaklı QR kod yönetim platformu.
            Misafir olarak oluştur ya da kaydol, geçmişini koru.
          </p>
          <div className={styles.actions}>
            <Link to="/create" className="btn btn-primary" id="hero-cta">
              QR Oluştur →
            </Link>
            {!isAuthenticated && (
              <Link to="/register" className="btn btn-ghost" id="hero-register">
                Ücretsiz Kayıt Ol
              </Link>
            )}
          </div>
        </section>

        {/* Özellikler */}
        <section className={styles.features} id="features">
          {FEATURES.map((f) => (
            <div key={f.title} className={`card ${styles.featureCard}`}>
              <span className={styles.featureIcon}>{f.icon}</span>
              <h3>{f.title}</h3>
              <p>{f.desc}</p>
            </div>
          ))}
        </section>

        {/* Misafir bilgi kartı */}
        {!isAuthenticated && (
          <section className={`card ${styles.guestBanner}`} id="guest-banner">
            <div>
              <h3>Hesap açmadan dene</h3>
              <p>
                Kayıt olmadan QR oluşturabilirsin. Geçmişini kaydetmek istersen{' '}
                <Link to="/register" className={styles.inlineLink}>ücretsiz hesap aç</Link>.
              </p>
            </div>
            <Link to="/create" className="btn btn-primary" id="guest-try">
              Hemen Dene
            </Link>
          </section>
        )}
      </div>
    </main>
  )
}
