#!/bin/sh
set -e
export PYTHONPATH=/app/backend
cd /app/backend
python init_db.py
exec uvicorn src.traffic_dtp.api.main:app --host 0.0.0.0 --port 8080
