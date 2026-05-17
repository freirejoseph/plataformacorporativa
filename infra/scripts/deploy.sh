#!/usr/bin/env bash
set -euo pipefail

ROOT="/home/plataformacorporativa"
NGINX_AVAILABLE="/etc/nginx/sites-available/plataforma.conf"
NGINX_ENABLED="/etc/nginx/sites-enabled/plataforma.conf"
SYSTEMD_SERVICE="/etc/systemd/system/plataforma-accesos-menues.service"

cd "$ROOT"

if [ -d ".git" ]; then
  git pull --rebase
fi

python infra/scripts/sync_plataforma.py --direction both

if [ -w /etc/nginx ] || [ "${EUID:-$(id -u)}" -eq 0 ]; then
  install -Dm644 infra/systemd/plataforma-accesos-menues.service "$SYSTEMD_SERVICE"
  install -Dm644 infra/nginx/plataforma.conf "$NGINX_AVAILABLE"
  ln -sfn "$NGINX_AVAILABLE" "$NGINX_ENABLED"
  systemctl daemon-reload
  nginx -t
  systemctl enable --now plataforma-accesos-menues.service
  systemctl reload nginx
  systemctl restart plataforma-accesos-menues.service
  echo "Portal publicado en http://192.168.1.40/"
else
  echo "Ejecuta este script con sudo en el Ubuntu para publicar Nginx y el servicio."
fi
