# ----- Stage 1: Build -----
# Node.js ile React uygulamasını derle
FROM node:20-alpine AS builder

WORKDIR /app

# Önce sadece package dosyalarını kopyala (layer cache optimizasyonu)
COPY package*.json ./
RUN npm ci --silent

# Uygulama kodunu kopyala ve üretim build'i oluştur
COPY . .
RUN npm run build


# ----- Stage 2: Serve -----
# Statik dosyaları nginx ile sun; Node.js çalışma zamanı gerekmez
FROM nginx:1.25-alpine

# nginx.conf'u şablon olarak kopyala (BACKEND_HOST değişkeni runtime'da çözülür)
COPY nginx.conf /etc/nginx/templates/default.conf.template

# Özel entrypoint: sadece ${BACKEND_HOST}'u değiştirir,
# nginx'in kendi $değişkenlerini ($host, $remote_addr vb.) bozmaz
COPY docker-entrypoint-nginx.sh /docker-entrypoint-nginx.sh
RUN chmod +x /docker-entrypoint-nginx.sh

# Builder'dan derlenmiş dosyaları kopyala
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

# Özel entrypoint: envsubst çalıştırır, ardından nginx başlatr
ENTRYPOINT ["/docker-entrypoint-nginx.sh"]
