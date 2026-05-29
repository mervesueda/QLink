// App.jsx – Uygulama kök bileşeni: router ve auth provider sarmalayıcısı.

import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import Navbar from './components/Navbar'
import { AuthProvider, useAuth } from './store/authStore'
import CreateQR from './pages/CreateQR'
import HomePage from './pages/HomePage'
import Login from './pages/Login'
import MyQRs from './pages/MyQRs'
import Register from './pages/Register'

// Auth gerektiren rotaları koruyan wrapper bileşen
function ProtectedRoute({ children }) {
  const { isAuthenticated } = useAuth()
  return isAuthenticated ? children : <Navigate to="/login" replace />
}

function AppRoutes() {
  return (
    <>
      <Navbar />
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/create" element={<CreateQR />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route
          path="/my-qrs"
          element={
            <ProtectedRoute>
              <MyQRs />
            </ProtectedRoute>
          }
        />
        {/* Bilinmeyen rota → ana sayfa */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </AuthProvider>
  )
}
