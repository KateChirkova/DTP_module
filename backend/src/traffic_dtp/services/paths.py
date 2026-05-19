# корень репозитория, скриншоты, загрузка .env
import os
from pathlib import Path

from dotenv import load_dotenv

_REPO_ROOT = Path(__file__).resolve().parents[4]
BACKEND_DIR = _REPO_ROOT / "backend"
PROJECT_ROOT = Path(os.getenv("PROJECT_ROOT", str(_REPO_ROOT))).resolve()
SCREENSHOTS_PATH = os.getenv("SCREENSHOTS_PATH", "data/screenshots")


def load_project_dotenv() -> None:
    load_dotenv(_REPO_ROOT / ".env")
    load_dotenv(BACKEND_DIR / ".env", override=True)
    load_dotenv(override=True)


def resolve_project_path(path: str) -> Path:
    p = Path(path)
    if p.is_absolute():
        return p.resolve()
    return (PROJECT_ROOT / path).resolve()


def resolve_screenshot_path(screenshot_path: str) -> tuple[str, Path]:
    normalized = screenshot_path.replace("\\", "/")
    filename = Path(normalized).name
    if normalized.startswith(SCREENSHOTS_PATH):
        relative = normalized
    else:
        relative = f"{SCREENSHOTS_PATH}/{filename}"
    return filename, resolve_project_path(relative)
