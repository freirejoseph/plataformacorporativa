#!/usr/bin/env bash
set -euo pipefail

ROOT="/home/plataformacorporativa"
cd "$ROOT"
/home/plataformacorporativa/.venv/bin/python - <<'PY'
from pathlib import Path
from apps.accesos_menues.backend.main import init_db
init_db()
print("seeded")
PY
