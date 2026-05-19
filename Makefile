# Запуск из корня репозитория DTP_Akaito (нужен GNU Make: Git Bash, WSL, или make из Chocolatey).
.PHONY: help test test-all test-backend test-frontend test-e2e docker-up docker-build docker-down docker-logs

PYTHON ?= python
NPM ?= npm

help:
	@echo "Targets:"
	@echo "  make test          — backend (pytest) + frontend (vitest)"
	@echo "  make test-all     — то же"
	@echo "  make test-backend — только tests/backend (pytest)"
	@echo "  make test-frontend — frontend unit/integration (vitest)"
	@echo "  make test-e2e     — frontend E2E + visual (playwright, поднимает API и dev-сервер)"
	@echo "  make docker-build — docker compose build"
	@echo "  make docker-up    — docker compose up -d --build"
	@echo "  make docker-down  — docker compose down"
	@echo "  make docker-logs  — docker compose logs -f"

test: test-all

test-all: test-backend test-frontend

test-backend:
	$(PYTHON) -m pytest tests/backend -q

test-frontend:
	cd frontend && $(NPM) test

test-e2e:
	cd frontend && $(NPM) run test:e2e

docker-build:
	docker compose build

docker-up:
	docker compose up -d --build

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f
