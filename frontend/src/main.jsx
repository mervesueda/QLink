// main.jsx – React uygulamasının DOM'a bağlandığı nokta.
// StrictMode: geliştirmede çift render yaparak yan etkileri erken yakalar.

import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
