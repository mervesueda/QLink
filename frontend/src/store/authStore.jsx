// store/authStore.jsx – Auth state yönetimi (React Context).
//
// Zustand veya Redux yerine Context tercih edildi:
// Bu büyüklükteki proje için yeterli; ek bağımlılık gerektirmez.

import { createContext, useCallback, useContext, useMemo, useState } from 'react'
import { login as apiLogin, register as apiRegister } from '../api/client'

const AuthContext = createContext(null)

// localStorage'dan başlangıç state'ini yükle (sayfa yenilemede oturum korunur)
function loadInitialState() {
  try {
    const token = localStorage.getItem('qlink_token')
    const user = JSON.parse(localStorage.getItem('qlink_user') || 'null')
    return { token, user }
  } catch {
    return { token: null, user: null }
  }
}

export function AuthProvider({ children }) {
  const initial = loadInitialState()
  const [token, setToken] = useState(initial.token)
  const [user, setUser] = useState(initial.user)

  const loginFn = useCallback(async (email, password) => {
    const res = await apiLogin(email, password)
    const { access_token } = res.data
    localStorage.setItem('qlink_token', access_token)
    // Basit kullanıcı bilgisi sakla (token decode etmiyoruz, güvenli)
    const userData = { email }
    localStorage.setItem('qlink_user', JSON.stringify(userData))
    setToken(access_token)
    setUser(userData)
    return res.data
  }, [])

  const registerFn = useCallback(async (email, password) => {
    const res = await apiRegister(email, password)
    return res.data
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem('qlink_token')
    localStorage.removeItem('qlink_user')
    setToken(null)
    setUser(null)
  }, [])

  const value = useMemo(
    () => ({
      token,
      user,
      isAuthenticated: !!token,
      login: loginFn,
      register: registerFn,
      logout,
    }),
    [token, user, loginFn, registerFn, logout],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

// Custom hook: bileşenlerde useAuth() ile kullanılır
export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider')
  return ctx
}
