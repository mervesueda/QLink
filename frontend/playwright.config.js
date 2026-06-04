// playwright.config.js – Playwright E2E test konfigürasyonu.
//
// KÖK NEDEN DÜZELTMESİ (ERR_CONNECTION_REFUSED):
// Windows Hyper-V/WSL2, 2586-3186 port aralığını dynamic reservation ile kilitler.
// Port 3000 ve 3100 bu aralıkta → Docker bind yapamıyor → ERR_CONNECTION_REFUSED.
// Frontend port 3200'e taşındı (güvenli aralık: 3187+).
//
// webServer bloğu:
//   - reuseExistingServer: true → docker-compose zaten çalışıyorsa onu kullanır
//   - Yoksa → npm run dev'i başlatır, localhost:3200 hazır olana kadar bekler

import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './e2e',
  fullyParallel: false,
  retries: process.env.CI ? 2 : 0,
  reporter: process.env.CI ? 'list' : 'html',

  use: {
    baseURL: process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:3200',
    screenshot: 'only-on-failure',
    trace: 'on-first-retry',
    headless: true,
    actionTimeout: 30000,
    navigationTimeout: 30000,
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],

  // webServer: testler başlamadan önce sunucunun hazır olmasını garantiler.
  // reuseExistingServer: true → docker-compose veya npm run dev çalışıyorsa kullanır.
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3200',
    reuseExistingServer: true,
    timeout: 120000,
  },
})
