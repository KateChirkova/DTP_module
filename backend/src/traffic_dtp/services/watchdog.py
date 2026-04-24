import time
from pathlib import Path
import os
import requests
from dotenv import load_dotenv
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

load_dotenv()

PROJECT_ROOT = Path(os.getenv("PROJECT_ROOT", "."))
SCREENSHOTS_PATH = os.getenv("SCREENSHOTS_PATH", "data/screenshots")
SCREENSHOTS_DIR = PROJECT_ROOT / SCREENSHOTS_PATH
API_URL = os.getenv("NEXT_PUBLIC_API_BASE", "http://127.0.0.1:8080") + "/api/v1/detections"

print(f"PROJECT_ROOT: {PROJECT_ROOT}")
print(f"SCREENSHOTS_DIR: {SCREENSHOTS_DIR}")
print(f"API_URL: {API_URL}")

if not PROJECT_ROOT.exists():
    raise ValueError(f"PROJECT_ROOT не существует: {PROJECT_ROOT}")


class ScreenshotHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and event.src_path.lower().endswith(('.jpg', '.jpeg', '.png')):
            filename = Path(event.src_path).name
            print(f"Новый скриншот: {filename}") # При запросе писать только имя файла

            time.sleep(2)

            try:
                payload = {"screenshot_path": filename}

                print(f"🚀 Отправляем: {payload}")
                response = requests.post(API_URL, json=payload, timeout=30)
                response.raise_for_status()

                result = response.json()
                print(f"YOLO: {result.get('detections_found', 0)} ДТП")

            except requests.exceptions.RequestException as e:
                print(f"API Ошибка: {e}")
                if hasattr(e.response, 'text'):
                    print(f"Сервер: {e.response.text}")


def main():
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

    event_handler = ScreenshotHandler()
    observer = Observer()
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