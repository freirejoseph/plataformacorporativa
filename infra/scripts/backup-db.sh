#!/usr/bin/env bash
set -euo pipefail

ROOT="/home/plataformacorporativa"
DB="$ROOT/portal-data/accesos_menues.sqlite"
BACKUP_DIR="$ROOT/infra/backups"
mkdir -p "$BACKUP_DIR"
STAMP="$(date +%Y%m%d_%H%M%S)"
sqlite3 "$DB" ".backup '$BACKUP_DIR/accesos_menues_$STAMP.sqlite'"
