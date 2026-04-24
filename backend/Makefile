.PHONY: dev watch init-db test test-api docker-up status clean backup

dev:
	@echo "Backend FastAPI + WS (8080)"
	uvicorn src.traffic_dtp.api.main:app --host 0.0.0.0 --port 8080 --reload

watch:
	@echo "Watchdog: data/screenshots/ → YOLO → API"
	pip install watchdog requests python-dotenv || true
	python -m src.traffic_dtp.services.watchdog

# База данных
init-db:
	@echo "Create tables"
	python -m src.traffic_dtp.db.init_db

status:
	@echo "=== Traffic DTP Status ==="
	@sqlite3 data/database.sqlite "SELECT COUNT(*) FROM accidents WHERE is_active=1" | tr -d '\n' && echo " active accidents"
	@sqlite3 data/database.sqlite "SELECT COUNT(*) FROM notifications WHERE status='unread'" | tr -d '\n' && echo " unread notifications"
	@ls data/screenshots/ 2>/dev/null | wc -l | tr -d '\n' && echo " screenshots"
	@curl -s "localhost:8080/health" | jq '.database.accidents.count' 2>/dev/null || echo "API down"

# Тесты
test:
	@echo "Unit tests"
	pytest tests/ -v

test-api:
	@echo "API test"
	curl -s -X POST "http://localhost:8080/api/v1/detections" \
	 -H "Content-Type: application/json" \
	 -d "{\"screenshot_path\": \"data/screenshots/test.jpg\"}" | jq

test-full:
	@echo "Full stack test"
	make dev & sleep 3 && make test-api

# Docker
docker-up:
	docker-compose up -d

docker-logs:
	docker-compose logs -f

# Yтилиты
clean:
	rm -rf __pycache__ src/__pycache__ *.pyc data/*.log

backup:
	cp data/database.sqlite data/database.sqlite.bak

logs:
	tail -f nohup.out || echo "No logs file"