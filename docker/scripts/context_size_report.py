# размер каталогов для отладки docker build context
from __future__ import annotations

import os
import sys
from pathlib import Path


def dir_size(path: Path) -> int:
    total = 0
    for root, _dirs, files in os.walk(path):
        for name in files:
            fp = Path(root) / name
            try:
                total += fp.stat().st_size
            except OSError:
                pass
    return total


def section(title: str, paths: list[tuple[Path, str]]) -> None:
    print(title)
    rows = [(dir_size(p), label) for p, label in paths if p.is_dir()]
    rows.sort(reverse=True)
    for size, label in rows:
        print(f"  {size / (1024 * 1024):10.1f} MB  {label}")
    print()


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    if not (root / "backend").is_dir():
        print("Запустите из репозитория DTP_Akaito (рядом должна быть папка backend/).", file=sys.stderr)
        sys.exit(1)

    print("Размеры на диске (в .dockerignore могут быть исключены — тогда в Docker context не попадут).\n")

    top = [
        (root / name, name)
        for name in sorted(os.listdir(root))
        if (root / name).is_dir() and not name.startswith(".")
    ]
    section("Корень репозитория:", top)

    be = root / "backend"
    if be.is_dir():
        sub = [(be / name, f"backend/{name}") for name in sorted(os.listdir(be)) if (be / name).is_dir()]
        section("backend/: ", sub)

    ml = root / "backend" / "src" / "traffic_dtp" / "ml"
    if ml.is_dir():
        sub = [(ml / name, f".../traffic_dtp/ml/{name}") for name in sorted(os.listdir(ml)) if (ml / name).is_dir()]
        section("backend/src/traffic_dtp/ml/: ", sub)


if __name__ == "__main__":
    main()
