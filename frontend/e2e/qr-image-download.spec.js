// e2e/qr-image-download.spec.js – QR Görsel Görüntüleme ve İndirme E2E Testleri
//
// Bu testler mevcut E2E testlerinin eksik bıraktığı şu senaryoları kapsar:
// 1. MyQRs sayfasında "broken image" olup olmadığının kontrolü (AuthenticatedImage).
// 2. İndirme butonunun programatik download akışının (fetch+blob) düzgün çalışması.
//
// KÖK NEDEN DÜZELTMELERİ:
// - TEST_EMAIL modül seviyesinde tek bir Date.now() kullanıyordu → her iki test
//   aynı e-posta ile kayıt olmaya çalışıyor → ikincisi "zaten kayıtlı" alıyor → timeout.
// - Her test için farklı benzersiz e-posta üretmek üzere beforeEach içine taşındı.
// - Port 3200 (Windows 2586-3186 port reservation çakışmasından kaçınmak için)
// - webServer ile Playwright otomatik olarak sunucuyu bekler

import { expect, test } from '@playwright/test'

const TEST_PASSWORD = 'SecureTest123!'

test.describe('QR Görsel ve İndirme Akışı', () => {
  // Bu test grubu ağır network işlemleri (blob fetch) içerdiğinden timeout artır
  test.setTimeout(90000)

  // Her test için benzersiz e-posta — Date.now() + random ile çakışma önlenir
  let testEmail

  test.beforeEach(async ({ page }) => {
    // Her test çalışmasında yeni benzersiz e-posta üret
    testEmail = `img_test_${Date.now()}_${Math.random().toString(36).slice(2, 7)}@test.com`

    // 1. Kayıt ol ve giriş yap
    await page.goto('/register')
    await page.fill('#register-email', testEmail)
    await page.fill('#register-password', TEST_PASSWORD)
    await page.click('#register-submit')

    await page.waitForURL(/login/, { timeout: 20000 })
    await page.fill('#login-email', testEmail)
    await page.fill('#login-password', TEST_PASSWORD)
    await page.click('#login-submit')
    await page.waitForURL(/my-qrs/, { timeout: 20000 })

    // 2. Bir QR oluştur
    await page.goto('/create')
    await page.fill('#qr-content', 'https://playwright.dev/test-image')
    await page.click('#submit-qr')
    await expect(page.locator('#qr-image')).toBeVisible({ timeout: 20000 })

    // 3. MyQRs sayfasına dön (navbar link kullan)
    await page.click('#nav-my-qrs')
    await expect(page).toHaveURL(/my-qrs/, { timeout: 10000 })

    // 4. QR listesinin yüklenmesini bekle
    // #qr-list sadece qrs.length > 0 iken render edilir.
    await page.waitForLoadState('networkidle', { timeout: 15000 })
    await expect(page.locator('#qr-list')).toBeVisible({ timeout: 15000 })
  })

  test('QR önizleme görselleri kırık olmadan yüklenmeli (AuthenticatedImage)', async ({ page }) => {
    // Tüm qr-thumb-* id'li resimleri bul
    const thumbnails = page.locator('[id^="qr-thumb-"]')
    await expect(thumbnails).toHaveCount(1, { timeout: 10000 })

    const thumb = thumbnails.first()

    // AuthenticatedImage blob URL üretmek için fetch yapıyor.
    // loading state'inde <div> render edilir, success state'inde <img>.
    // <img> tag'i görünür hale gelene kadar bekle (polling ile)
    await page.waitForFunction(
      (selector) => {
        const el = document.querySelector(selector)
        return el && el.tagName.toLowerCase() === 'img'
      },
      '[id^="qr-thumb-"]',
      { timeout: 20000, polling: 500 }
    )

    // Elementin gerçekten bir img tagi olduğunu doğrula
    const tagName = await thumb.evaluate(el => el.tagName.toLowerCase())
    expect(tagName).toBe('img')

    // src attribute'unun blob: URL'i olduğunu doğrula
    const src = await thumb.getAttribute('src')
    expect(src).toMatch(/^blob:/)
  })

  test('İndirme butonu fetch+blob akışıyla dosyayı indirebilmeli', async ({ page }) => {
    // Playwright'ın download listener'ını kur
    const downloadPromise = page.waitForEvent('download', { timeout: 30000 })

    // İndir butonuna tıkla
    const downloadBtns = page.locator('[id^="download-"]')
    await expect(downloadBtns.first()).toBeVisible({ timeout: 10000 })
    await downloadBtns.first().click()

    // İndirme tetiklendi mi bekle
    const download = await downloadPromise

    // İnen dosyanın adının doğru formatta olduğunu doğrula
    expect(download.suggestedFilename()).toMatch(/^qlink-[a-f0-9\-]+\.png$/)

    // Hata olmadığından emin ol (Sayfada hâlâ görünür liste var)
    await expect(page.locator('#qr-list')).toBeVisible()
  })
})
