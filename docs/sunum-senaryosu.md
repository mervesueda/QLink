# QLink – Dönem Projesi Sunum Senaryosu (10 Dakika)

**Grup Üyeleri:** Merve Sueda Aydın & Elif Seda Demirhan  
**Proje:** QR Code Generator Service (Konu 35)  
**Toplam Süre:** 10 Dakika (Sunum + Canlı Demo) + 3 Dakika Q&A  

---

## 🎯 Dağılım ve Zaman Çizelgesi
- **Merve (Toplam ~5 Dk):** Slayt 1, Slayt 3, Slayt 5, Canlı Demo Bölüm 1
- **Elif (Toplam ~5 Dk):** Slayt 2, Slayt 4, Slayt 6, Canlı Demo Bölüm 2

---

## 📽️ Slayt 1: Problem & Çözüm (0 - 1. Dakika)
**Ekranda Ne Var:** Proje başlığı (QLink), grup üyelerinin isimleri, kısa bir misyon cümlesi ("Basit Bir Uygulama, Güçlü Bir Test Boru Hattı").

**Merve:**
> "Değerli hocamız ve arkadaşlarımız, hoş geldiniz. Ben Merve, ekip arkadaşım Elif ile birlikte geliştirdiğimiz cloud-native QR Code Generator projemiz QLink'i sunacağız. 
> Biliyorsunuz ki bu projedeki asıl amacımız karmaşık bir iş mantığı yazmak değil; aksine basit ve anlaşılır bir mikroservis etrafında endüstri standardı bir **uçtan uca test ve dağıtım altyapısı** kurmaktı. Biz de bu yüzden URL veya metinleri QR koda çevirip S3 üzerinde saklayan, dışa dönük API'leri olan bu projeyi seçtik. Böylece hem cloud native depolamayı test ettik, hem de test piramidinin tüm katmanlarını projemize başarıyla uyguladık."

---

## 📽️ Slayt 2: Mimari Diyagram (1. - 2.5 Dakika)
**Ekranda Ne Var:** `docs/architecture.png` dosyası (React, FastAPI, PostgreSQL, LocalStack, Grafana bileşenlerinin iletişimi).

**Elif:**
> "Sistem mimarimize bakacak olursak; frontend tarafında React ve Vite kullandık. Asıl odak noktamız olan Backend'de ise **FastAPI**'ı tercih ettik. Neden FastAPI derseniz; asenkron yapısı sayesinde yüksek performans veriyor ve Pydantic ile veri doğrulama işlemlerini çok kolay test edebiliyoruz.
> Veritabanı olarak PostgreSQL kullandık. Ancak asıl kritik nokta bulut depolama katmanıydı. Gerçek bir AWS hesabı açıp maliyet ve güvenlik riski yaratmak yerine, S3 bucket'ımızı simüle etmek için **LocalStack** kullandık. QR kodlarımız üretildiği an LocalStack S3'e yükleniyor. Yan servisler olarak da sistemimizi izlemek için Prometheus ve Grafana ikilisini docker-compose ile mimarimize entegre ettik."

---

## 📽️ Slayt 3: Test Stratejisi (2.5 - 4. Dakika)
**Ekranda Ne Var:** Test Piramidi Görseli. Yanında istatistikler (Coverage >%70, 43 Unit, 20+ Integration).

**Merve:**
> "Test stratejimizi klasik test piramidi üzerine inşa ettik. En altta Pytest ile yazdığımız 40'tan fazla Unit test var. Burada S3 bağlantılarımızı 'moto' kütüphanesiyle mock'layarak AWS bağımlılığını kopardık.
> Bir üst katman olan Integration (Entegrasyon) testlerinde kesinlikle mock kullanmadık! Bunun yerine **Testcontainers** kullandık. Testcontainers sayesinde test koşarken arka planda izole, gerçek bir PostgreSQL ayağa kalkıyor. Bu sayede 'benim makinemde çalışıyordu' problemini tamamen çözmüş olduk. Test verilerimizi de manuel girmek yerine **Factory Boy ve Faker** ile dinamik olarak ürettik. Bu sağlam test altyapısı sayesinde kod kapsamımızı (Coverage) %70'in üzerine çıkardık."

---

## 📽️ Slayt 4: CI/CD Pipeline & K8s (4. - 5.5 Dakika)
**Ekranda Ne Var:** GitHub Actions Akış Şeması (Lint -> Test -> Build -> Deploy -> Newman -> E2E) ve Kubernetes ikonları.

**Elif:**
> "Geliştirdiğimiz kodun canlıya çıkış sürecini GitHub Actions ile tam otomatik hale getirdik. Pipeline'ımız lint, test, build ve smoke test adımlarından oluşuyor.
> Dockerfile'ımızı yazarken güvenlik ve boyut optimizasyonu için **Multi-stage build** kullandık. Yani kodu build ederken kullandığımız bağımlılıkları, son çalışan (runtime) imaja dahil etmedik. Bu sayede imaj boyutumuz inanılmaz küçüldü ve attack surface (saldırı yüzeyi) azaldı.
> Dağıtım (Deploy) tarafında ise K8s manifestlerimizi **Helm Chart** haline getirerek esneklik sağladık ve Minikube üzerinde çalışır hale getirdik."

---

## 📽️ Slayt 5: Performans & Observability (5.5 - 6.5 Dakika)
**Ekranda Ne Var:** Grafana Dashboard ekran görüntüsü (Latency, Error Rate) ve k6 tablosu (200 VU, p95 < 500ms).

**Merve:**
> "Bir sistemin sadece çalışması yetmez, yük altında da ayakta kalması gerekir. **k6** aracıyla sistemimize aşamalı olarak 200 eşzamanlı kullanıcı (VU) yükü bindirdik. Şartnamedeki hedefimiz p95 gecikme süresinin 500 milisaniyenin altında olmasıydı; başarılı bir şekilde bu hedefin altında kaldık.
> Tüm bu anlık performansı, hataları (Error Rate) ve throughput'u izlemek için kodumuza Prometheus exporter entegre ettik ve Grafana dashboard'ları üzerinden 3 farklı panelle canlı olarak takip edilebilir hale getirdik."

---

## 📽️ Slayt 6: Öğrendiklerimiz & Zorluklar (6.5 - 7. Dakika)
**Ekranda Ne Var:** 3 maddelik kısa bir özet (Testcontainers gücü, Multi-stage avantajı, Pipeline zorlukları).

**Elif:**
> "Bu projeden çıkardığımız en büyük ders; integration testler için Testcontainers kurmanın başlangıçta zor olsa da, uzun vadede veritabanı hatalarını sıfıra indirdiği oldu. Ayrıca uçtan uca bir pipeline kurmanın, kodu yazmaktan daha meşakkatli ama çok daha değerli bir süreç olduğunu gördük."

---

## 💻 Bölüm 2: CANLI DEMO AKIŞI (7. - 10. Dakika)
> **Hazırlık:** Sunumdan hemen önce `docker-compose up -d` yapılmış, Minikube ayakta, GitHub Actions sayfası, Grafana ve QLink web arayüzü sekmelerde açık olmalıdır.

### Adım 1: CI Pipeline Tetikleme (Merve - 1 Dakika)
*Merve, GitHub ekranını açar ve sahte bir PR'ı merge eder.*
**Merve:** "Şimdi sistemin nasıl otomatik deploy olduğunu göstermek için küçük bir değişikliği merge ediyorum. Gördüğünüz gibi GitHub Actions pipeline'ımız lint ve Pytest adımlarıyla koşmaya başladı. Arka planda testler geçerse multi-stage docker imajımız build edilecek."

### Adım 2: API ve S3 (LocalStack) Kontrolü (Merve - 30 Saniye)
*Merve, Postman veya Newman terminal ekranını açar.*
**Merve:** "Pipeline ilerlerken, API'mizin Postman koleksiyonunu **Newman** üzerinden terminalde tek komutla koşuyoruz. Gördüğünüz gibi tüm endpoint'ler ve LocalStack S3 yüklemeleri yeşil yanarak başarılı oluyor."

### Adım 3: Yük Testi (k6) Koşumu (Elif - 45 Saniye)
*Elif terminale geçer ve k6 komutunu çalıştırır: `k6 run perf/load-test.js`*
**Elif:** "Şu an sisteme k6 ile anlık bir load testi başlatıyorum. Kullanıcı sayısı sıfırdan 100'e doğru çıkıyor. Ekranda gördüğünüz p95 metrikleri şu an doğrudan API'nin yanıt süresini ölçüyor."

### Adım 4: Grafana İzleme (Elif - 30 Saniye)
*Elif tarayıcıda Grafana sekmesine geçer.*
**Elif:** "k6 arka planda sisteme yük bindirirken, Grafana dashboard'umuza geçiyoruz. Gördüğünüz gibi Request Latency grafiği hareketlenmeye başladı ve Throughput (saniyedeki istek sayısı) anlık olarak metriklerimize yansıyor."

### Adım 5: E2E Playwright Testi (Elif - 15 Saniye)
*Elif terminalde `npx playwright test --ui` komutunu çalıştırır veya direkt web sayfasını açıp bir QR üretir.*
**Elif:** "Son adımda ise kullanıcının yaşadığı uçtan uca deneyimi **Playwright** E2E testlerimiz otomatik olarak UI üzerinden tıklayarak doğruluyor. Bizi dinlediğiniz için teşekkür ederiz, sorularınızı yanıtlamaktan memnuniyet duyarız."

---

## 🛡️ Q&A İÇİN SAVUNMA ARGÜMANLARI (Bonus Hazırlık)

Hoca sunum sonrasında şu soruları sorabilir, hazırlıklı olun:

**Soru 1: "Neden FastAPI kullandınız?"**
**Cevap:** "Asenkron mimarisi sayesinde I/O bound işlemlerde (örneğin S3'e dosya yüklerken) çok daha performanslı. Ayrıca Pydantic entegrasyonu sayesinde request body validasyonlarını ek bir koda ihtiyaç duymadan, şemalar üzerinden otomatik yapabiliyoruz ve Swagger dokümanı kendiliğinden oluşuyor."

**Soru 2: "Testcontainers nedir, neden mock kullanmadınız?"**
**Cevap:** "Unit testlerde S3 için 'moto' ile mock kullandık. Ancak Integration testlerinde veritabanını mock'lamak, 'benim makinemde çalışıyordu' riskini doğurur. Testcontainers arka planda sıfırdan bir PostgreSQL docker container'ı ayağa kaldırıyor. Bu sayede testlerimiz gerçekten bir veritabanına bağlanarak en gerçekçi (production-like) sonucu veriyor."

**Soru 3: "Dockerfile'ınızdaki Multi-stage build'in avantajı ne?"**
**Cevap:** "Python bağımlılıklarını kurarken derleyici araçlarına (gcc vb.) ihtiyaç duyarız. Eğer tek stage yapsaydık bu araçlar final imajda da olurdu; bu hem imaj boyutunu (MB olarak) şişirir hem de güvenlik zafiyeti yaratır. Multi-stage ile bağımlılıkları birinci adımda (builder) kurup, sadece derlenmiş kütüphaneleri ikinci (runtime) imaja kopyaladık."

**Soru 4: "LocalStack'in gerçek S3'ten farkı nedir?"**
**Cevap:** "LocalStack, AWS S3 API'sini yerel docker container'ımızda %100 uyumlu bir şekilde taklit eder. Gerçek S3'ten tek farkı ağ gecikmesi (network latency) olmaması ve cloud faturası getirmemesidir. Kodumuzda `endpoint_url` parametresini kaldırırsak, sistemimiz hiçbir kod değişikliği olmadan direkt gerçek AWS S3'te çalışmaya hazırdır."
