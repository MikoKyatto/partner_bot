# Makefile for Lethai Concierge Referral Bot

.PHONY: help install test run docker-build docker-run docker-stop clean lint format

# Default target
help:
	@echo "Lethai Concierge Referral Bot - Available commands:"
	@echo ""
	@echo "Development:"
	@echo "  install     Install dependencies"
	@echo "  test        Run tests"
	@echo "  run         Run bot locally"
	@echo "  lint        Run linting"
	@echo "  format      Format code"
	@echo ""
	@echo "Docker:"
	@echo "  docker-build    Build Docker image"
	@echo "  docker-run      Run with Docker Compose"
	@echo "  docker-stop     Stop Docker containers"
	@echo "  docker-logs     View Docker logs"
	@echo ""
	@echo "Utilities:"
	@echo "  clean       Clean up generated files"
	@echo "  setup       Initial setup"

# Development commands
install:
	pip install -r requirements.txt
	pip install -e .

test:
	pytest -v --tb=short

test-coverage:
	pytest --cov=. --cov-report=html --cov-report=term

run:
	python main.py

lint:
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

format:
	black . --line-length 127
	isort .

# Docker commands
docker-build:
	docker-compose build

docker-run:
	docker-compose up -d

docker-stop:
	docker-compose down

docker-logs:
	docker-compose logs -f lethai-bot

docker-restart:
	docker-compose restart lethai-bot

# Setup commands
setup: install
	@echo "Setting up Lethai Referral Bot..."
	@if [ ! -f .env ]; then \
		cp env.example .env; \
		echo "Created .env file from template. Please edit it with your configuration."; \
	fi
	@if [ ! -f credentials.json ]; then \
		echo "Please add your Google service account credentials.json file."; \
	fi
	@echo "Setup complete!"

# Cleanup commands
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type f -name "qr_*.jpg" -delete
	find . -type f -name "*.log" -delete
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage

clean-docker:
	docker-compose down -v
	docker system prune -f

# Database commands
init-db:
	python -c "from utils.database import init_database; init_database()"

# Production commands
deploy:
	docker-compose -f docker-compose.yml up -d --build

status:
	docker-compose ps

# Development server with auto-reload
dev:
	python -m aiogram.cli run_polling main:bot

# Check system requirements
check:
	@echo "Checking system requirements..."
	@python --version
	@docker --version
	@docker-compose --version
	@echo "All requirements met!"

# Backup database
backup:
	@if [ -f users.db ]; then \
		cp users.db "backup_$(shell date +%Y%m%d_%H%M%S).db"; \
		echo "Database backed up successfully"; \
	else \
		echo "No database file found"; \
	fi

# Restore database
restore:
	@if [ -f "$(BACKUP_FILE)" ]; then \
		cp "$(BACKUP_FILE)" users.db; \
		echo "Database restored from $(BACKUP_FILE)"; \
	else \
		echo "Please specify BACKUP_FILE=filename.db"; \
	fi



