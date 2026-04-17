.PHONY: dev watchdog init-db test logs clean

dev:
	@echo "🚀 Backend API + WS (8080)"
	uvicorn src.traffic_dtp.api.main:app --host 0.0.0.0 --port 8080 --reload

watchdog:
	@echo "👀 YOLO Screenshot Processor"
	python src/traffic_dtp/services/accident_processor.py

init-db:
	@echo "🗄️ Initialize database"
	python -c "from src.traffic_dtp.db.session import init_db; init_db()"

test:
	@echo "🧪 Test /detections API"
	curl -X POST "http://localhost:8080/api/v1/detections" ^
	 -H "Content-Type: application/json" ^
	 -d "{\"screenshotid\":999,\"confidence\":0.95,\"bbox\":[100,200,300,400],\"geo_lat\":55.7558,\"geo_lon\":37.6176}"

logs:
	@echo "📊 Tail watcher.log"
	tail -f ../data/watcher.log

clean:
	@echo "🧹 Clean Python cache"
	rm -rf __pycache__ *.pyc`