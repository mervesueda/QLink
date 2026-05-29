// playwright.config.js – Playwright E2E test konfigürasyonu.
//
// Testler çalışmadan önce frontend ve backend'in ayakta olması gerekir.
// CI'da docker-compose ile ortam hazırlandıktan sonra çalıştırılır.

import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  // Testlerin bulunduğu dizin
  testDir: './e2e',

  // Paralel çalıştırma: CI'da false yaparak sıralı çalıştır (kaynak kısıtı)
  fullyParallel: false,

  // CI'da yeniden deneme yapma (flaky testleri maskelemez)
  retries: process.env.CI ? 1 : 0,

  // Raporlama: CI'da list, yerel geliştirmede html
  reporter: process.env.CI ? 'list' : 'html',

  use: {
    // Test edilen uygulama URL'i
    baseURL: process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:3000',

    // Hata durumunda ekran görüntüsü al
    screenshot: 'only-on-failure',

    // İz kaydı: yalnızca ilk yeniden denemede
    trace: 'on-first-retry',

    // Headless mod: CI'da true, yerel geliştirmede false
    headless: true,
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],

  // Yerel geliştirmede dev server'ı otomatik başlat
  // CI'da bu satırı yorum satırı yap (zaten ayakta)
  // webServer: {
  //   command: 'npm run dev',
  //   url: 'http://localhost:3000',
  //   reuseExistingServer: true,
  // },
})
