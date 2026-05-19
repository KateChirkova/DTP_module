import logging
import os
import time
from pathlib import Path

import requests

logger = logging.getLogger(__name__)
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from src.traffic_dtp.services.paths import PROJECT_ROOT, SCREENSHOTS_PATH, load_project_dotenv

load_project_dotenv()

SCREENSHOTS_DIR = PROJECT_ROOT / SCREENSHOTS_PATH
API_URL = os.getenv("NEXT_PUBLIC_API_BASE", "http://127.0.0.1:8080") + "/api/v1/detections"
INTERNAL_API_KEY = (os.getenv("DTP_INTERNAL_API_KEY") or "").strip()

print(f"PROJECT_ROOT: {PROJECT_ROOT}")
print(f"SCREENSHOTS_DIR: {SCREENSHOTS_DIR}")
print(f"API_URL: {API_URL}")
if INTERNAL_API_KEY:
    print(f"DTP_INTERNAL_API_KEY: задан ({len(INTERNAL_API_KEY)} символов)")
else:
    print(
        "ВНИМАНИЕ: DTP_INTERNAL_API_KEY не задан — POST /detections вернёт 403. "
        "Скопируйте значение из .env в корне репозитория в backend/.env или перезапустите watchdog."
    )

if not PROJECT_ROOT.exists():
    raise ValueError(f"PROJECT_ROOT не существует: {PROJECT_ROOT}")

_USE_POLLING = os.getenv("WATCHDOG_USE_POLLING", "").lower() in ("1", "true", "yes")
_STABLE_TIMEOUT = float(
    os.getenv("WATCHDOG_STABLE_TIMEOUT", "8.0" if _USE_POLLING else "1.5")
)
_STABLE_INTERVAL = float(
    os.getenv("WATCHDOG_STABLE_INTERVAL", "0.2" if _USE_POLLING else "0.05")
)
_STABLE_READS = int(os.getenv("WATCHDOG_STABLE_READS", "2" if _USE_POLLING else "1"))
_DEDUPE_SECONDS = float(
    os.getenv("WATCHDOG_DEDUPE_SECONDS", "2.0" if _USE_POLLING else "0.5")
)

_HTTP = requests.Session()


# дождаться дописанного файла (Docker bind mount — дольше)
def _wait_until_stable(path: Path) -> bool:
    deadline = time.monotonic() + _STABLE_TIMEOUT
    last_size = -1
    stable_reads = 0
    while time.monotonic() < deadline:
        if not path.is_file():
            time.sleep(min(_STABLE_INTERVAL, 0.1))
            continue
        try:
            size = path.stat().st_size
        except OSError:
            time.sleep(min(_STABLE_INTERVAL, 0.1))
            continue
        if size > 0 and size == last_size:
            stable_reads += 1
            if stable_reads >= _STABLE_READS:
                return True
        else:
            stable_reads = 0
        last_size = size
        time.sleep(_STABLE_INTERVAL)
    return path.is_file() and path.stat().st_size > 0


# новый кадр в папке скриншотов -> POST /detections
class ScreenshotHandler(FileSystemEventHandler):

    def __init__(self) -> None:
        self._recent: dict[str, float] = {}
        self._dedupe_seconds = _DEDUPE_SECONDS

    def _should_process(self, src: str) -> bool:
        if not src.lower().endswith((".jpg", ".jpeg", ".png")):
            return False
        now = time.monotonic()
        last = self._recent.get(src)
        if last is not None and now - last < self._dedupe_seconds:
            return False
        self._recent[src] = now
        return True

    def _process_path(self, src: str) -> None:
        if isinstance(src, bytes):
            src = src.decode("utf-8", errors="replace")
        if not self._should_process(src):
            return

        path = Path(src)
        filename = path.name
        print(f"Скриншот: {filename}")

        if not _wait_until_stable(path):
            print(f"Пропуск (файл пустой или не дописан): {filename}")
            return

        try:
            payload = {"screenshot_path": filename}
            headers = {}
            if INTERNAL_API_KEY:
                headers["X-Internal-Key"] = INTERNAL_API_KEY
            print(f"Отправляем: {payload}")
            response = _HTTP.post(API_URL, json=payload, headers=headers, timeout=120)
            response.raise_for_status()

            result = response.json()
            print(
                f"API: detections={result.get('detections_found', 0)}, "
                f"new_accidents={result.get('new_accidents', 0)}"
            )

        except requests.exceptions.RequestException as e:
            print(f"API Ошибка: {e}")
            body = ""
            if hasattr(e, "response") and e.response is not None and hasattr(e.response, "text"):
                body = e.response.text
                print(f"Сервер: {body}")
            logger.error(
                "Watchdog POST /detections failed: filename=%s error=%s response=%s",
                filename,
                e,
                body[:500] if body else None,
            )

    def on_created(self, event):
        if event.is_directory:
            return
        self._process_path(event.src_path)

    def on_modified(self, event):
        if event.is_directory:
            return
        if os.getenv("WATCHDOG_USE_POLLING", "").lower() in ("1", "true", "yes"):
            self._process_path(event.src_path)


def _make_observer():
    use_polling = os.getenv("WATCHDOG_USE_POLLING", "").lower() in ("1", "true", "yes")
    if use_polling:
        from watchdog.observers.polling import PollingObserver

        print("Watchdog: polling (WATCHDOG_USE_POLLING) — для Docker + локальная папка")
        return PollingObserver()
    return Observer()


def main():
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

    event_handler = ScreenshotHandler()
    observer = _make_observer()
    observer.schedule(event_handler, str(SCREENSHOTS_DIR), recursive=False)
    observer.start()

    print(f"Watchdog: {SCREENSHOTS_DIR}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nСтоп")
        observer.stop()
        observer.join()


if __name__ == "__main__":
    main()
