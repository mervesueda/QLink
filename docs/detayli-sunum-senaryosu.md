# QLink – 25 Dakikalık İleri Seviye Mühendislik Sunumu ve Demo Senaryosu

**Grup Üyeleri:** Merve Sueda Aydın & Elif Seda Demirhan  
**Proje:** QR Code Generator Service (MTH2526-B25 - Konu 35)  
**Toplam Süre:** ~25 Dakika (Sunum + Arayüz Demoları + Teknik Derinlemesine İnceleme)

---

## BÖLÜM 1: GİRİŞ VE PROJE FELSEFESİ (0. - 3. Dakika)
*[Ekranda: QLink Başlık Slaydı ve Misyonumuz]*

**Merve:**
"Sayın hocamız, değerli jüri üyeleri ve sevgili arkadaşlar, hoş geldiniz. Ben Merve, ekip arkadaşım Elif ile birlikte 'Bulut Mimarilerinde Test Mühendisliği' projemiz olan **QLink**'i sunmaktan gurur duyuyoruz.

Projemize başlarken kendimize şu kısıtı koyduk: 'İçerisinde yüzlerce tablosu olan karmaşık bir monolit yazılım geliştirmek yerine; sektörde 'Cloud-Native' (Bulut Doğuşlu) standartları belirleyen, izlenebilirliği (observability) yüksek, tam otomatik bir CI/CD boru hattına sahip ve en önemlisi **Test Piramidi'nin tüm katmanlarını eksiksiz barındıran** bir mikroservis inşa edeceğiz.'

Uygulamamızın iş mantığı bilinçli olarak sade tutulmuştur: Sistemimiz URL, metin veya e-posta verilerini alarak QR kodlar üretmekte, bu görselleri bulut nesne deposunda (Object Storage) saklamakta ve kullanıcılara geçmişe dönük erişim sağlamaktadır. Şimdi bu sade mantığın etrafına nasıl endüstri standardı bir mühendislik ağı ördüğümüzü adım adım inceleyeceğiz."

---

## BÖLÜM 2: MİMARİ KARARLAR VE TEKNOLOJİ YIĞINI (3. - 8. Dakika)
*[Ekranda: Mimari Diyagram (architecture.png)]*

**Elif:**
"Sistemimizin mimari bileşenlerini seçerken tamamen güncel endüstri standartlarını hedefledik.

**Frontend (İstemci) Katmanı:**
Arayüzümüzü React.js ile geliştirdik. Ancak eski nesil Webpack gibi hantal derleyiciler yerine, modül tabanlı (ESM) anlık derleme yapan **Vite** aracını tercih ettik. Vite sayesinde derleme sürelerimizi saniyenin altına indirdik. Prodüksiyon ortamında ise bu statik dosyaları sunmak ve reverse-proxy (ters vekil sunucu) görevi görmek üzere **Nginx** kullandık.

**Backend (Sunucu) Katmanı:**
Backend tarafında geleneksel Django veya Flask yerine, Python 3.12 üzerinde **FastAPI** framework'ünü seçtik. Neden FastAPI? Çünkü FastAPI, asenkron (asyncio) yapısı üzerine kuruludur. Bizim sistemimiz S3'e dosya yüklemek veya veritabanına sorgu atmak gibi yoğun I/O (girdi/çıktı) işlemleri yapıyor. Asenkron yapı sayesinde CPU, bu I/O işlemlerini beklerken bloke olmaz ve diğer isteklere yanıt vermeye devam eder. Bu da sistemimizin verimini (throughput) dramatik şekilde artırır. Ayrıca FastAPI'ın kalbinde yatan **Pydantic** kütüphanesi sayesinde, API'mize gelen tüm veri payload'ları, önceden tanımladığımız statik veri şemalarına göre otomatik doğrulanır (validation) ve geçersiz veri içeri sızamaz.

**Merve:**
"Veri katmanına gelirsek; ilişkisel veri bütünlüğünü korumak için kullanıcı ve QR metadatalarını **PostgreSQL 15** üzerinde tutuyoruz.

Fakat en kritik mimari kararımız dosya depolama tarafındaydı. Bulut mimarisi kuralları gereği (12-Factor App), Docker container'larının içi 'stateless' (durumsuz) olmalıdır. Yani üretilen QR PNG dosyalarını container içine kaydedemeyiz, aksi takdirde container yeniden başlatıldığında dosyalar silinir. Bu yüzden verileri AWS S3 gibi bir Nesne Depolama (Object Storage) servisine göndermeliydik.
Ancak yerel geliştirme ve CI ortamlarımızda gerçek AWS'ye bağlanmak; hem ağ gecikmesi, hem kredi kartı güvenliği hem de maliyet oluşturacaktı. Bu sorunu çözmek için **LocalStack** kullandık. LocalStack, gerçek AWS S3 API'sinin birebir aynısını bilgisayarımızda bir Docker container'ı olarak simüle eder. Backend kodumuzda `boto3` kütüphanesini kullanırken 'endpoint_url' parametresini değiştirerek, kodumuzu gram değiştirmeden lokaldeki S3'e bağlanmasını sağladık. Üretime (Production) çıkarken tek yapmamız gereken bu ortam değişkenini kaldırmaktır."

---

## BÖLÜM 3: TEST PİRAMİDİ VE ENTEGRASYON STRATEJİSİ (8. - 12. Dakika)
*[Ekranda: Test Piramidi ve Pytest Coverage Terminal Görüntüsü]*

**Elif:**
"Yazdığımız bu mimarinin çökmemesi için uyguladığımız Test Mühendisliği stratejimize geçelim.
Martin Fowler'ın 'Test Piramidi' modelini baz aldık. Piramidin en alt ve en geniş tabanında **Birim (Unit) Testlerimiz** yer alıyor.

Unit testler hızlıdır ve dış bağımlılık içermez. Pytest kullanarak yazdığımız 40'tan fazla unit testimiz var. Peki dış bağımlılıkları nasıl soyutladık? Örneğin S3'e dosya yükleme fonksiyonumuzu test ederken, gerçek veya LocalStack bir S3'e gitmek unit testin doğasına aykırıdır. Bu yüzden **'moto'** adında bir kütüphane kullandık. Moto, Python'da AWS servislerini hafızada (in-memory) 'Mock'lar (taklit eder). Böylece testlerimiz milisaniyeler içinde dış ağa hiç çıkmadan doğrulanır.

**Merve:**
"Ancak sadece Mock'lara güvenemeyiz. Bir fonksiyonun Mock ile çalışması, gerçek veritabanında da düzgün çalışacağı anlamına gelmez. Bu noktada piramidin bir üst katmanı olan **Entegrasyon (Integration) Testlerine** geçtik.

Entegrasyon testlerinin felsefesi Mock kullanmamaktır! Fakat 'Geliştiricinin makinesindeki DB'de test verisi farklıydı, CI sunucusunda farklıydı' (It works on my machine) problemini önlememiz gerekiyordu.
Bu devasa problemi **Testcontainers** aracı ile çözdük. Biz Pytest'i çalıştırdığımız anda, Testcontainers kodu araya girer; bilgisayarımızda sıfır, temiz ve rastgele portlardan dinleyen bir PostgreSQL ve bir LocalStack Docker container'ı ayağa kaldırır. Testlerimiz bu gerçek container'lara bağlanır, QR oluşturup S3'e yükler, veritabanına yazar, doğrulamaları bitirir ve son adımda container'ları yok edip ortamı temizler.

*[Merve terminali açıp canlı olarak şu komutu çalıştırır]*
`pytest tests/ --cov=app --cov-report=term-missing`

Gördüğünüz gibi, kodumuzun her bir satırı gerçek veritabanı ve S3 üzerinde test ediliyor. Bu sayede kod kapsama oranımızı (Coverage) güvenle %70'in üzerine çıkardık."

---

## BÖLÜM 4: CI/CD PİPELİNE VE DOCKER MULTI-STAGE (12. - 15. Dakika)
*[Ekranda: GitHub Actions Akış Şeması ve Dockerfile İçeriği]*

**Elif:**
"Kodumuzun kalitesinden emin olduktan sonra, bunu sunucuya paketleme ve dağıtma sürecini otomatize etmemiz gerekiyordu. GitHub Actions ile bir CI/CD Boru Hattı (Pipeline) kurduk.

Geliştirici kodu GitHub'a gönderdiğinde (Push veya PR); sistem önce kod formatını Lint eder, ardından Testcontainers destekli Pytest testlerimizi çalıştırır. Testler geçerse Docker imajlarımız oluşturulur.

Burada Dockerfile yapımıza özellikle dikkatinizi çekmek istiyorum. İmajlarımızı **Multi-stage build (Çok Aşamalı Derleme)** tekniğiyle yazdık. 
Python projelerinde `psycopg2` gibi veritabanı sürücülerini derlemek için işletim sisteminde `gcc`, `musl-dev` gibi C/C++ derleyicilerine ihtiyaç vardır. Eğer imajı tek aşamalı yapsaydık, bu derleyiciler nihai sunucuya kadar gidecek, imaj boyutunu yüzlerce megabayt şişirecek ve en kötüsü hackerlara sunucu içinde kod derleme imkanı verecek bir 'saldırı yüzeyi' (attack surface) yaratacaktı.

Biz ise Dockerfile'ımızda birinci katmanı (Builder) tüm derleyicilerle donattık. İkinci katmanda ise 'Alpine' veya 'Slim' tabanlı bomboş bir işletim sistemi açıp, sadece birinci katmandan derlenmiş olan saf Python dosyalarını (wheels) kopyaladık. Bu sayede imaj boyutumuz güvenlik standartlarında ve minimal oldu."

---

## BÖLÜM 5: KALİTE GÜVENCESİ: PLAYWRIGHT VE NEWMAN (15. - 19. Dakika)
*[Ekranda: Playwright Arayüzü ve Newman HTML Raporu]*

**Merve:**
"Uygulama sunucuya yüklendiğinde kalite güvence (QA) süreçlerimiz başlar. Backend API'mizin dış dünyaya verdiği tepkileri ölçmek için **Postman** koleksiyonları hazırladık ve bunu CI hattımızda terminalden koşabilmek için **Newman** kullandık.

*[Merve tarayıcıda `newman-report.html` dosyasını açar ve grafiklerin üzerinden fareyle geçer]*
Gördüğünüz bu detaylı htmlextra raporunda; sistemimizin yetkilendirme (JWT Token), hata yakalama (Yanlış şifre girildiğinde 401 dönmesi) ve S3 entegrasyonu dahil olmak üzere 14 farklı uç nokta üzerinden 27 adet assertion (doğrulama) yaptığını görüyorsunuz.

**Elif:**
"API'miz mükemmel çalışıyor olabilir ama son kullanıcı tarayıcıda butona tıkladığında sistem yanıt veriyor mu? Bu soruyu cevaplamak için piramidin en üst noktası olan **E2E (Uçtan Uca) Testleri** kullandık. Eski nesil Selenium yerine, Microsoft'un modern aracı **Playwright**'ı tercih ettik. Neden Playwright? Çünkü asenkron DOM render işlemlerini, elementlerin ekranda görünmesini otomatik bekleyerek test kırılganlığını (flakiness) sıfıra indiriyor.

*[Elif terminalde `npx playwright test --ui` komutunu çalıştırır ve Play butonuna basar]*
Hemen canlı bir demo ile gösterelim. Ekranda Play tuşuna bastığım an; arka planda Chromium motoru sıfırdan ayağa kalkıyor. Robotumuz, gerçek bir insan gibi React arayüzümüze giriyor, formları dolduruyor, API'ye isteği gönderiyor ve ekranda beliren QR resmini DOM (Document Object Model) seviyesinde denetliyor. Biz buna tam otomasyon diyoruz."

---

## BÖLÜM 6: PERFORMANS TESTLERİ VE K6 DARBOĞAZ ANALİZİ (19. - 22. Dakika)
*[Ekranda: Grafana Dashboard'ları ve k6 Terminal Çıktısı]*

**Merve:**
"Fonksiyonel olarak sistemimiz kusursuz. Peki ya 'Kara Cuma' gibi ani bir yüklenme anında sistemimiz nasıl tepki verecek?
Performans ölçümleri için Java tabanlı JMeter yerine, günümüzün modern yük test aracı olan, Go diliyle yazılmış **k6**'yı kullandık. Go'nun goroutines mimarisi sayesinde tek bir makineden binlerce eşzamanlı sanal kullanıcı (Virtual User - VU) üretebiliyoruz.

Sisteme birdenbire yüklenmek yerine aşamalı bir test profili oluşturduk: 0'dan 100 kullanıcıya 1 dakikalık Ramp-up (tırmanma), ardından Peak (zirve) noktasında 200 eşzamanlı kullanıcı.

Şartnamemizde başarılı sayılmak için `p95 Latency` (isteklerin %95'inin yanıt süresi) değerinin 500 milisaniyenin altında olması gerekiyordu. 

*[Elif Grafana ekranını açar ve grafikleri gösterir]*
Yük testi anında sistemimizin nabzını tutmak için mimarimize kattığımız **Prometheus** ve **Grafana** devreye giriyor. Prometheus, FastAPI üzerinden saniyede bir metrikleri (scrape) çekerken, Grafana bu verileri görselleştiriyor. 
Yük testimizde bir şey fark ettik: Veritabanı sorgularımız saniyenin onda biri hızında çalışırken, saniyede 200 kişi aynı anda S3'e (LocalStack) görsel yüklemeye çalıştığında sistemin **Darboğaz (Bottleneck)** oluşturduğunu tespit ettik. İsteklerin p95 yanıt süresi 500ms'nin üzerine çıktı ve HTTP 500 hataları almaya başladık. 

Biz bu sonucu bir hata olarak değil, sistemin limitinin keşfi olarak raporumuza kaydettik. Çünkü iyi bir test mühendisi sistemi başarılı göstermeye çalışmaz; sistemin nerede kırılacağını bulmaya çalışır."

---

## BÖLÜM 7: KUBERNETES VE GITOPS (ARGOCD) İLE DEPLOYMENT (22. - 25. Dakika)
*[Ekranda: ArgoCD Arayüzü ve K8s Terminal Çıktısı]*

**Elif:**
"Son olarak bu sistemi canlıya nasıl aldığımıza (Deployment) değinmek istiyoruz. Tüm mimarimizi **Minikube** üzerinde yerel bir Kubernetes kümesine dağıttık. Backend, Frontend, Postgres ve S3 container'larımız Kubernetes 'Deployment' ve 'Service' manifestoları ile ayağa kaldırıldı. 

Ancak bu konfigürasyon dosyalarını (YAML) düz metin olarak yönetmek zor olduğu için **Helm** paket yöneticisini kullandık. Helm sayesinde Kubernetes manifestolarımızı şablon (template) haline getirip, dinamik değişkenler (values.yaml) ile tek komutta yüzlerce satırlık K8s objesi üretebiliyoruz.

Ve projemizin 'Bonus' ama bize göre en değerli mimari kararı: **GitOps ve ArgoCD.**
Klasik CI/CD yöntemlerinde (Push model), GitHub Actions biter ve sunucuya SSH ile bağlanıp kodu zorla oraya basar (kubectl apply). Bu güvenli değildir.
Biz ise Pull tabanlı 'GitOps' modelini benimsedik. ArgoCD aracını Kubernetes kümemizin içine kurduk.

*[Merve ArgoCD arayüzünü açar]*
ArgoCD, 7/24 bizim GitHub repomuzu gözetliyor. Biz GitHub'daki bir konfigürasyonu değiştirdiğimiz an (örneğin k6 testinde bulduğumuz o darboğazı çözmek için backend pod sayısını 1'den 3'e çıkardığımızda), ArgoCD bu değişikliği algılıyor. Kendi kümesini GitHub'daki duruma eşitleyerek (Sync), arayüzde gördüğünüz gibi anında pod sayısını artırıyor. Bu sayede sunucuya insan eli değmiyor ve tüm sistem altyapımız versiyon kontrollü (Infrastructure as Code) hale geliyor."

**Merve & Elif:**
"Biz bu projeyle; bir kodun yazılmasından test edilmesine, güvenliğinden paketlenmesine, darboğaz analizinden son bulut sunucusunda yayınlanmasına kadar geçen devasa DevOps ve Test Mühendisliği yolculuğunu başarıyla tamamladık. Sektöre çıkmadan önce endüstrinin tam merkezindeki teknolojilerle bu mimariyi kurmak bize inanılmaz bir vizyon kattı. Bizi dinlediğiniz ve projemize bu fırsatı sunduğunuz için teşekkür ederiz. Şimdi teknik sorularınız varsa büyük bir memnuniyetle detaylandırabiliriz."

---
*(Sunum biter, Q&A başlar. Hocalar ArgoCD, Multi-stage veya Testcontainers detaylarını sorarsa sunum içinde anlattığınız detaylar yeterli olacaktır.)*
