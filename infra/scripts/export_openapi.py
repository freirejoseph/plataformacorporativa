from __future__ import annotations

import json
import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "apps" / "accesos-menues" / "backend" / "main.py"
OUTPUT_PATH = ROOT / "docs" / "openapi.json"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def load_app() -> object:
    spec = spec_from_file_location("accesos_menues_main", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("No se pudo cargar el modulo del portal madre.")
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.app


def main() -> None:
    app = load_app()
    OUTPUT_PATH.write_text(
        json.dumps(app.openapi(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"OPENAPI_EXPORTED={OUTPUT_PATH}")


if __name__ == "__main__":
    main()
