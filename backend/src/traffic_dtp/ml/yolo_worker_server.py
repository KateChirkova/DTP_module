# отдельный процесс: YOLO грузится один раз, POST /predict по пути к файлу
from __future__ import annotations

import json
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

_SRC = Path(__file__).resolve().parents[2]
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from traffic_dtp.services.yolo_predict import predict_accident  # noqa: E402


class _Handler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        if self.path.rstrip("/") != "/predict":
            self.send_response(404)
            self.end_headers()
            return
        try:
            n = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(n) if n else b"{}"
            data = json.loads(raw.decode("utf-8"))
            image_path = data.get("path")
            if not image_path:
                raise ValueError("JSON body must contain string field 'path'")
            out = predict_accident(str(image_path))
            body = json.dumps(out, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except Exception as e:
            err = json.dumps({"error": str(e), "detections": []}, ensure_ascii=False).encode("utf-8")
            self.send_response(500)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(err)))
            self.end_headers()
            self.wfile.write(err)

    def log_message(self, fmt: str, *args) -> None:
        print(f"[yolo-worker] {fmt % args}")


def main() -> None:
    print("[yolo-worker] загрузка модели…")
    from traffic_dtp.services.yolo_predict import get_model

    get_model()
    print("[yolo-worker] модель готова")

    port = int(os.environ.get("YOLO_WORKER_PORT", "18081"))
    bind = os.environ.get("YOLO_WORKER_BIND", "127.0.0.1")
    server = HTTPServer((bind, port), _Handler)
    print(f"[yolo-worker] http://{bind}:{port}/predict (POST JSON {{\"path\": \"...\"}})")
    server.serve_forever()


if __name__ == "__main__":
    main()
