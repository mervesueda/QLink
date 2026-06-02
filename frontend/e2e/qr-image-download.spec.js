// e2e/qr-image-download.spec.js – QR Görsel Görüntüleme ve İndirme E2E Testleri
//
// Bu testler mevcut E2E testlerinin eksik bıraktığı şu senaryoları kapsar:
// 1. MyQRs sayfasında "broken image" olup olmadığının kontrolü (AuthenticatedImage).
// 2. İndirme butonunun programatik download akışının (fetch+blob) düzgün çalışması.

import { expect, test } from '@playwright/test'

const TEST_EMAIL = `image_test_${Date.now()}@test.com`
const TEST_PASSWORD = 'SecureTest123!'

test.describe('QR Görsel ve İndirme Akışı', () => {
  test.beforeEach(async ({ page }) => {
    // 1. Kayıt ol ve giriş yap
    await page.goto('/register')
    await page.fill('#register-email', TEST_EMAIL)
    await page.fill('#register-password', TEST_PASSWORD)
    await page.click('#register-submit')
    
    await page.waitForURL(/login/)
    await page.fill('#login-email', TEST_EMAIL)
    await page.fill('#login-password', TEST_PASSWORD)
    await page.click('#login-submit')
    await page.waitForURL(/my-qrs/)

    // 2. Bir QR oluştur
    await page.goto('/create')
    await page.fill('#qr-content', 'https://playwright.dev/test-image')
    await page.click('#submit-qr')
    await expect(page.locator('#qr-image')).toBeVisible({ timeout: 15000 })
    
    // 3. MyQRs sayfasına dön
    await page.click('#nav-my-qrs')
    await expect(page).toHaveURL(/my-qrs/)
    await expect(page.locator('#qr-list')).toBeVisible()
  })

  test('QR önizleme görselleri kırık olmadan yüklenmeli (AuthenticatedImage)', async ({ page }) => {
    // Tüm qr-thumb-* id'li resimleri bul
    const thumbnails = page.locator('[id^="qr-thumb-"]')
    await expect(thumbnails).toHaveCount(1)

    // Resmin yükleme spinner'ı değil (loading label yok) ve error icon (🔲) olmadığını doğrula.
    // Başarılı yüklenen resimler `<img>` tagi olmalıdır.
    const thumb = thumbnails.first()
    
    // Elementin gerçekten bir img tagi olup olmadığını doğrula (hata state'i <div> render eder)
    const tagName = await thumb.evaluate(el => el.tagName.toLowerCase())
    expect(tagName).toBe('img')

    // src attribute'unun blob: URL'i olduğunu doğrula (AuthenticatedImage fetch+blob kullanır)
    const src = await thumb.getAttribute('src')
    expect(src).toMatch(/^blob:/)
  })

  test('İndirme butonu fetch+blob akışıyla dosyayı indirebilmeli', async ({ page }) => {
    // Playwright'ın download listener'ını kur
    const downloadPromise = page.waitForEvent('download')
    
    // İndir butonuna tıkla
    const downloadBtns = page.locator('[id^="download-"]')
    await downloadBtns.first().click()

    // İndirme tetiklendi mi bekle
    const download = await downloadPromise
    
    // İnen dosyanın adının doğru formatta olduğunu doğrula
    expect(download.suggestedFilename()).toMatch(/^qlink-[a-f0-9\-]+\.png$/)
    
    // Hata olmadığından emin ol (Sayfada hâlâ görünür liste var)
    await expect(page.locator('#qr-list')).toBeVisible()
  })
})
