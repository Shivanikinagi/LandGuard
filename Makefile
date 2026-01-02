# Pied Piper 2.0 - Makefile
# Convenience commands for development and deployment

.PHONY: help install setup clean test start stop docker-up docker-down deploy-blockchain

# Default target
help:
	@echo "🚀 Pied Piper 2.0 - Available Commands"
	@echo "======================================"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make install          - Install all dependencies"
	@echo "  make setup            - Run automated setup script"
	@echo "  make clean            - Clean build artifacts and cache"
	@echo ""
	@echo "Development:"
	@echo "  make start            - Start all services"
	@echo "  make stop             - Stop all services"
	@echo "  make test             - Run tests"
	@echo "  make test-pcc         - Run PCC tests only"
	@echo "  make test-landguard   - Run LandGuard tests only"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-up        - Start Docker containers"
	@echo "  make docker-down      - Stop Docker containers"
	@echo "  make docker-logs      - View Docker logs"
	@echo "  make docker-build     - Build Docker images"
	@echo ""
	@echo "Blockchain:"
	@echo "  make deploy-blockchain - Deploy smart contracts"
	@echo "  make check-balance     - Check wallet balance"
	@echo ""
	@echo "Production:"
	@echo "  make install-prod     - Install production dependencies"
	@echo "  make deploy-server    - Deploy to production server"
	@echo ""

# Installation
install:
	@echo "📦 Installing PCC dependencies..."
	cd pcc && python -m venv venv && . venv/bin/activate && pip install -r requirements.txt
	@echo "📦 Installing LandGuard dependencies..."
	cd landguard && python -m venv venv && . venv/bin/activate && pip install -r requirements.txt
	@echo "📦 Installing Blockchain dependencies..."
	cd landguard/Blockchain && npm install
	@echo "✅ Installation complete!"

install-prod:
	@echo "📦 Installing production dependencies..."
	cd pcc && python -m venv venv && . venv/bin/activate && pip install -r requirements.production.txt
	cd landguard && python -m venv venv && . venv/bin/activate && pip install -r requirements.production.txt
	@echo "✅ Production installation complete!"

setup:
	@echo "🔧 Running automated setup..."
	chmod +x setup.sh
	./setup.sh

# Development
start:
	@echo "🚀 Starting services..."
	chmod +x start.sh
	./start.sh

stop:
	@echo "🛑 Stopping services..."
	chmod +x stop.sh
	./stop.sh

test:
	@echo "🧪 Running all tests..."
	cd pcc && . venv/bin/activate && pytest
	cd landguard && . venv/bin/activate && pytest
	cd landguard/Blockchain && npm test

test-pcc:
	@echo "🧪 Running PCC tests..."
	cd pcc && . venv/bin/activate && pytest

test-landguard:
	@echo "🧪 Running LandGuard tests..."
	cd landguard && . venv/bin/activate && pytest

# Docker
docker-up:
	@echo "🐳 Starting Docker containers..."
	docker-compose up -d
	@echo "✅ Containers started!"
	@echo "PCC: http://localhost:8000"
	@echo "LandGuard: http://localhost:8001"

docker-down:
	@echo "🐳 Stopping Docker containers..."
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-build:
	@echo "🐳 Building Docker images..."
	docker-compose build

docker-restart:
	make docker-down
	make docker-up

# Blockchain
deploy-blockchain:
	@echo "⛓️  Deploying smart contracts..."
	cd landguard/Blockchain && npm run deploy:amoy

check-balance:
	@echo "💰 Checking wallet balance..."
	cd landguard/Blockchain && npm run balance

# Cleaning
clean:
	@echo "🧹 Cleaning build artifacts..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pid" -delete
	rm -rf build dist
	@echo "✅ Cleanup complete!"

# Production deployment
deploy-server:
	@echo "🚀 Deploying to production server..."
	@echo "⚠️  Make sure you've configured your server details!"
	rsync -avz --exclude 'venv' --exclude 'node_modules' --exclude '.git' . user@server:/path/to/deployment/
	@echo "✅ Files synced! Now SSH to server and run setup."

# Database
db-migrate:
	@echo "🗄️  Running database migrations..."
	cd landguard && . venv/bin/activate && alembic upgrade head

db-reset:
	@echo "⚠️  Resetting database..."
	cd landguard && . venv/bin/activate && alembic downgrade base && alembic upgrade head

# Health checks
health:
	@echo "🏥 Checking service health..."
	@curl -s http://localhost:8000/health || echo "❌ PCC not responding"
	@curl -s http://localhost:8001/health || echo "❌ LandGuard not responding"

# Logs
logs:
	@echo "📋 Viewing logs..."
	tail -f logs/*.log

# Update
update:
	@echo "🔄 Updating dependencies..."
	cd pcc && . venv/bin/activate && pip install -U -r requirements.txt
	cd landguard && . venv/bin/activate && pip install -U -r requirements.txt
	cd landguard/Blockchain && npm update
	@echo "✅ Update complete!"
