.PHONY: dev dev-down build deploy logs logs-queue logs-nginx health clean clean-all \
	invite invite-list invite-info invite-revoke ssl-setup ssl-renew \
	status-local health-local start-local stop-local restart-local invite-local \
	lint lint-js lint-py lint-fix lint-fix-js lint-fix-py help

# =============================================================================
# Configuration
# =============================================================================

# Load environment from secrets/.env
ifneq (,$(wildcard ./secrets/.env))
    include ./secrets/.env
    export
endif

# macOS Keychain fallback for CLAUDE_CODE_OAUTH_TOKEN
ifeq ($(shell uname -s),Darwin)
    ifndef CLAUDE_CODE_OAUTH_TOKEN
        CLAUDE_CODE_OAUTH_TOKEN := $(shell security find-generic-password -a "$$USER" -s "CLAUDE_CODE_OAUTH_TOKEN" -w 2>/dev/null)
    endif
endif
export CLAUDE_CODE_OAUTH_TOKEN

# Docker Configuration
DEMO_NETWORK ?= {{NETWORK_NAME}}
BASE_IMAGE ?= grandcamel/claude-devcontainer:enhanced

# =============================================================================
# Development
# =============================================================================

dev:
	@echo "Starting development environment..."
	@docker network create $(DEMO_NETWORK) 2>/dev/null || true
	CLAUDE_CODE_OAUTH_TOKEN="$(CLAUDE_CODE_OAUTH_TOKEN)" docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build

dev-down:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml down

# =============================================================================
# Build & Deploy
# =============================================================================

build:
	@echo "Building all containers..."
	docker-compose build
	docker build --build-arg BASE_IMAGE=$(BASE_IMAGE) -t {{CONTAINER_IMAGE}} ./demo-container

deploy:
	@echo "Deploying to production..."
	@docker network create $(DEMO_NETWORK) 2>/dev/null || true
	CLAUDE_CODE_OAUTH_TOKEN="$(CLAUDE_CODE_OAUTH_TOKEN)" docker-compose pull
	CLAUDE_CODE_OAUTH_TOKEN="$(CLAUDE_CODE_OAUTH_TOKEN)" docker-compose build
	docker-compose down
	CLAUDE_CODE_OAUTH_TOKEN="$(CLAUDE_CODE_OAUTH_TOKEN)" docker-compose up -d
	@echo "Waiting for services..."
	@sleep 5
	@$(MAKE) health

# =============================================================================
# Logs
# =============================================================================

logs:
	docker-compose logs -f --tail=100

logs-queue:
	docker-compose logs -f queue-manager

logs-nginx:
	docker-compose logs -f nginx

# =============================================================================
# Health & Status
# =============================================================================

health:
	@echo "Checking system health..."
	@curl -sf http://localhost/health > /dev/null && echo "Landing page: OK" || echo "Landing page: FAILED"
	@curl -sf http://localhost/api/status > /dev/null && echo "Queue manager: OK" || echo "Queue manager: FAILED"
	@docker-compose exec -T redis redis-cli ping > /dev/null && echo "Redis: OK" || echo "Redis: FAILED"

status-local:
	@echo "=== Service Status ==="
	@docker-compose -f docker-compose.yml -f docker-compose.dev.yml ps

health-local:
	@echo "Checking local health..."
	@curl -sf http://localhost:8080/health > /dev/null && echo "Nginx: OK" || echo "Nginx: FAILED"
	@curl -sf http://localhost:8080/api/status > /dev/null && echo "Queue manager: OK" || echo "Queue manager: FAILED"

# =============================================================================
# Invite Management
# =============================================================================

invite:
	@docker-compose exec -T queue-manager node /app/invite-cli.js generate --expires $(or $(EXPIRES),48h) $(if $(TOKEN),--token "$(TOKEN)",) $(if $(LABEL),--label "$(LABEL)",)

invite-local:
	@docker-compose -f docker-compose.yml -f docker-compose.dev.yml exec -T queue-manager node /app/invite-cli.js generate --expires $(or $(EXPIRES),48h) $(if $(LABEL),--label "$(LABEL)",) --base-url http://localhost:8080

invite-list:
	@docker-compose exec -T queue-manager node /app/invite-cli.js list $(if $(STATUS),--status $(STATUS),)

invite-info:
	@docker-compose exec -T queue-manager node /app/invite-cli.js info $(TOKEN)

invite-revoke:
	@docker-compose exec -T queue-manager node /app/invite-cli.js revoke $(TOKEN)

# =============================================================================
# SSL
# =============================================================================

ssl-setup:
	@echo "Setting up SSL with Let's Encrypt..."
	certbot --nginx -d $(DOMAIN)

ssl-renew:
	certbot renew

# =============================================================================
# Linting
# =============================================================================

lint: lint-js lint-py

lint-js:
	@echo "Linting JavaScript..."
	cd queue-manager && npm run lint

lint-py:
	@echo "Linting Python..."
	ruff check scripts/

lint-fix: lint-fix-js lint-fix-py

lint-fix-js:
	cd queue-manager && npm run lint:fix

lint-fix-py:
	ruff check scripts/ --fix

# =============================================================================
# Cleanup
# =============================================================================

clean:
	docker-compose down -v

clean-all:
	docker-compose down -v --rmi all
	rm -rf session-env/*
	rm -rf /tmp/claude-checkpoints/

# =============================================================================
# Help
# =============================================================================

help:
	@echo "{{PRODUCT}} Demo - Available Commands"
	@echo ""
	@echo "Development:"
	@echo "  make dev            - Start development environment"
	@echo "  make dev-down       - Stop development environment"
	@echo "  make logs           - View all logs"
	@echo "  make logs-queue     - View queue-manager logs"
	@echo ""
	@echo "Build & Deploy:"
	@echo "  make build          - Build all containers"
	@echo "  make deploy         - Deploy to production"
	@echo ""
	@echo "Invites:"
	@echo "  make invite-local   - Generate local invite URL"
	@echo "  make invite         - Generate production invite"
	@echo "  make invite-list    - List all invites"
	@echo "  make invite-revoke TOKEN=xxx - Revoke an invite"
	@echo ""
	@echo "Maintenance:"
	@echo "  make health         - Check service health"
	@echo "  make lint           - Run all linters"
	@echo "  make clean          - Remove containers and volumes"
	@echo ""
