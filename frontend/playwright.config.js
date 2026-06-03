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

  // Global test timeout: 60sn (QR üretimi + S3 yükleme süresi)
  timeout: 60000,

  use: {
    // Test edilen uygulama URL'i
    baseURL: process.env.BASE_URL || process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:3000',

    // Hata durumunda ekran görüntüsü al
    screenshot: 'only-on-failure',

    // Video: yalnızca hata durumunda kaydet
    video: 'retain-on-failure',

    // İz kaydı: yalnızca ilk yeniden denemede
    trace: 'on-first-retry',

    // Headless mod
    headless: true,

    // Varsayılan timeout: QR üretimi biraz sürebilir
    actionTimeout: 30000,
    navigationTimeout: 30000,
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],

  // Frontend ve backend ayaktayken testleri çalıştır.
  // docker-compose ile tüm servisler zaten ayaktaysa bu servis yeni bir şey başlatmaz.
  webServer: {
    command: 'echo "Checking services..."',
    url: 'http://localhost:3000',
    reuseExistingServer: true,  // Zaten ayakta olan frontend'i kullan
    timeout: 30000,
  },
})

