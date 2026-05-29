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

# Özel nginx konfigürasyonu: SPA routing için gerekli
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Builder'dan derlenmiş dosyaları kopyala
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
