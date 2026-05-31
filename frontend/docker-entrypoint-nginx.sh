#!/bin/sh
# docker-entrypoint-nginx.sh
#
# nginx resmi image'ının envsubst mekanizması TÜM env değişkenlerini işler.
# Bu, nginx'in kendi değişkenlerini ($host, $remote_addr vb.) bozabilir.
# Bu script sadece BACKEND_HOST'u değiştirir, diğer nginx değişkenlerine dokunmaz.

set -e

TEMPLATE=/etc/nginx/templates/default.conf.template
OUTPUT=/etc/nginx/conf.d/default.conf

# Sadece ${BACKEND_HOST} değişkenini değiştir, nginx'in kendi $değişkenlerine dokunma
envsubst '${BACKEND_HOST}' < "$TEMPLATE" > "$OUTPUT"

echo "[entrypoint] BACKEND_HOST=${BACKEND_HOST} → nginx proxy hedefi ayarlandı"

# nginx'i başlat
exec nginx -g "daemon off;"
