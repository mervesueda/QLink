// generate-pdfs.js – slides.html ve final-report.md'yi PDF'e çevirir
// Çalıştırma: node docs/generate-pdfs.js (frontend/node_modules Playwright kullanır)

const { chromium } = require('../frontend/node_modules/@playwright/test')
const fs = require('fs')
const path = require('path')

;(async () => {
  const browser = await chromium.launch()
  const page = await browser.newPage()

  // 1. slides.html → slides.pdf
  console.log('slides.pdf oluşturuluyor...')
  const slidesPath = path.resolve(__dirname, 'slides.html')
  await page.goto(`file:///${slidesPath.replace(/\\/g, '/')}`, { waitUntil: 'networkidle' })
  await page.pdf({
    path: path.resolve(__dirname, 'slides.pdf'),
    format: 'A4',
    landscape: true,
    printBackground: true,
    margin: { top: '0', right: '0', bottom: '0', left: '0' },
  })
  console.log('✅ docs/slides.pdf oluşturuldu')

  // 2. final-report.md → final-report.pdf (Markdown'u HTML'e çevir)
  console.log('final-report.pdf oluşturuluyor...')
  const mdContent = fs.readFileSync(path.resolve(__dirname, 'final-report.md'), 'utf8')
  
  // Basit Markdown → HTML dönüşümü (başlıklar, paragraflar, listeler, tablolar, kod blokları)
  let html = mdContent
    // Kod blokları (önce işle)
    .replace(/```[\w]*\n([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
    // Inline kod
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    // Başlıklar
    .replace(/^### (.+)$/gm, '<h3>$1</h3>')
    .replace(/^## (.+)$/gm, '<h2>$1</h2>')
    .replace(/^# (.+)$/gm, '<h1>$1</h1>')
    // Bold + italic
    .replace(/\*\*\*(.+?)\*\*\*/g, '<strong><em>$1</em></strong>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    // Horizontal rules
    .replace(/^---$/gm, '<hr>')
    // Tablolar
    .replace(/^\|(.+)\|$/gm, (match) => {
      if (match.includes('---')) return ''
      const cells = match.split('|').filter(c => c.trim())
      return '<tr>' + cells.map(c => `<td>${c.trim()}</td>`).join('') + '</tr>'
    })
    // Listeler
    .replace(/^- (.+)$/gm, '<li>$1</li>')
    .replace(/^\d+\. (.+)$/gm, '<li>$1</li>')
    // Paragraflar
    .replace(/\n\n/g, '</p><p>')
    // Blockquotes
    .replace(/^> (.+)$/gm, '<blockquote>$1</blockquote>')
    // Linkler
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>')

  const reportHtml = `<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<title>QLink – Final Rapor</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: 'Inter', sans-serif; font-size: 11pt; color: #1a1a2e; line-height: 1.7; padding: 40px 60px; max-width: 800px; margin: 0 auto; }
  h1 { font-size: 22pt; color: #7c3aed; margin: 24px 0 8px; border-bottom: 2px solid #7c3aed; padding-bottom: 6px; }
  h2 { font-size: 16pt; color: #4f46e5; margin: 20px 0 6px; }
  h3 { font-size: 13pt; color: #374151; margin: 16px 0 4px; }
  p { margin: 8px 0; }
  li { margin: 4px 0 4px 24px; list-style: disc; }
  code { background: #f3f4f6; padding: 1px 5px; border-radius: 3px; font-size: 10pt; font-family: monospace; }
  pre { background: #1e1e2e; color: #cdd6f4; padding: 14px 18px; border-radius: 8px; margin: 12px 0; overflow-x: auto; }
  pre code { background: none; color: inherit; padding: 0; }
  hr { border: none; border-top: 1px solid #e5e7eb; margin: 20px 0; }
  blockquote { border-left: 4px solid #7c3aed; padding: 8px 16px; background: #f5f3ff; margin: 12px 0; border-radius: 0 6px 6px 0; }
  table { border-collapse: collapse; width: 100%; margin: 12px 0; }
  td, th { border: 1px solid #d1d5db; padding: 6px 12px; text-align: left; font-size: 10pt; }
  tr:nth-child(even) { background: #f9fafb; }
  strong { color: #111827; }
  a { color: #7c3aed; }
  .header { text-align: center; padding: 20px 0 30px; border-bottom: 3px solid #7c3aed; margin-bottom: 30px; }
  .header h1 { border: none; font-size: 26pt; }
  .header p { color: #6b7280; margin: 4px 0; }
</style>
</head>
<body>
<div class="header">
  <h1>QLink</h1>
  <p>Cloud-Native QR Code Management Platform</p>
  <p>MTH2526-B25 · Bulut Mimarilerinde Test Mühendisliği · 2025–2026 Bahar</p>
  <p>Marmara Üniversitesi · Bilgisayar Mühendisliği Bölümü</p>
</div>
<p>${html}</p>
</body>
</html>`

  await page.setContent(reportHtml, { waitUntil: 'networkidle' })
  await page.pdf({
    path: path.resolve(__dirname, 'final-report.pdf'),
    format: 'A4',
    printBackground: true,
    margin: { top: '20mm', right: '15mm', bottom: '20mm', left: '15mm' },
  })
  console.log('✅ docs/final-report.pdf oluşturuldu')

  await browser.close()
  console.log('\n🎉 Her iki PDF hazır: docs/slides.pdf ve docs/final-report.pdf')
})()
