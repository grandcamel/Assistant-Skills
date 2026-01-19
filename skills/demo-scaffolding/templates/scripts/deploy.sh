#!/bin/bash
# =============================================================================
# {{PRODUCT}} Demo Deployment Script
# =============================================================================
# Deploys the demo system to a DigitalOcean droplet.
#
# Usage:
#   ./deploy.sh                   # Deploy to production
#   ./deploy.sh --setup           # Initial setup (install Docker, etc.)
#   ./deploy.sh --ssl             # Set up SSL with Let's Encrypt
#   ./deploy.sh --update          # Update to latest version
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
echo_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
echo_error() { echo -e "${RED}[ERROR]${NC} $1"; }
echo_step() { echo -e "${CYAN}==>${NC} $1"; }

# =============================================================================
# Initial Setup
# =============================================================================

setup() {
    echo_step "Setting up server..."

    # Update system
    apt-get update && apt-get upgrade -y

    # Install Docker
    if ! command -v docker &> /dev/null; then
        echo_info "Installing Docker..."
        curl -fsSL https://get.docker.com | sh
        systemctl enable docker
        systemctl start docker
    else
        echo_info "Docker already installed"
    fi

    # Install Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        echo_info "Installing Docker Compose..."
        apt-get install -y docker-compose-plugin
    else
        echo_info "Docker Compose already installed"
    fi

    # Install certbot for SSL
    echo_info "Installing certbot..."
    apt-get install -y certbot python3-certbot-nginx

    # Create project directory
    mkdir -p /opt/{{DEMO_NAME}}
    mkdir -p /opt/{{DEMO_NAME}}/secrets

    echo_info "Setup complete!"
    echo ""
    echo "Next steps:"
    echo "  1. Copy your project files to /opt/{{DEMO_NAME}}"
    echo "  2. Configure secrets in /opt/{{DEMO_NAME}}/secrets/"
    echo "  3. Run: ./deploy.sh"
}

# =============================================================================
# SSL Setup
# =============================================================================

setup_ssl() {
    echo_step "Setting up SSL with Let's Encrypt..."

    # Load domain from env
    if [ -f "$PROJECT_ROOT/secrets/.env" ]; then
        source "$PROJECT_ROOT/secrets/.env"
    fi

    if [ -z "$DOMAIN" ]; then
        echo_error "DOMAIN not set in secrets/.env"
        exit 1
    fi

    # Get certificate
    certbot certonly --standalone -d "$DOMAIN" --non-interactive --agree-tos --email "admin@$DOMAIN"

    # Update nginx config
    echo_info "Update nginx/demo.conf to enable HTTPS server block"

    echo_info "SSL setup complete!"
}

# =============================================================================
# Deploy
# =============================================================================

deploy() {
    echo_step "Deploying {{PRODUCT}} Demo..."

    cd "$PROJECT_ROOT"

    # Verify secrets exist
    if [ ! -f "secrets/.env" ]; then
        echo_error "secrets/.env not found"
        echo "Copy secrets/example.env to secrets/.env and configure"
        exit 1
    fi

    # Load environment
    source secrets/.env

    # Verify Claude authentication
    if [ -z "${CLAUDE_CODE_OAUTH_TOKEN:-}" ] && [ -z "${ANTHROPIC_API_KEY:-}" ]; then
        echo_error "No Claude authentication configured"
        echo "Set CLAUDE_CODE_OAUTH_TOKEN or ANTHROPIC_API_KEY in secrets/.env"
        echo "  CLAUDE_CODE_OAUTH_TOKEN=...  # From 'claude setup-token'"
        echo "  ANTHROPIC_API_KEY=...        # API key"
        exit 1
    fi

    # Pull latest images
    echo_info "Pulling base images..."
    docker pull grandcamel/claude-devcontainer:enhanced
    docker pull redis:alpine
    docker pull nginx:alpine

    # Build custom images
    echo_info "Building custom images..."
    docker-compose build

    # Build demo container
    echo_info "Building demo container..."
    docker build -t {{CONTAINER_IMAGE}} ./demo-container

    # Stop existing services
    echo_info "Stopping existing services..."
    docker-compose down || true

    # Start services
    echo_info "Starting services..."
    docker-compose up -d

    # Wait for startup
    echo_info "Waiting for services to start..."
    sleep 10

    # Health check
    echo_info "Running health checks..."
    if curl -sf http://localhost/health > /dev/null; then
        echo_info "Landing page: OK"
    else
        echo_warn "Landing page: FAILED"
    fi

    if curl -sf http://localhost/api/health > /dev/null; then
        echo_info "Queue manager: OK"
    else
        echo_warn "Queue manager: FAILED"
    fi

    echo ""
    echo -e "${GREEN}+--------------------------------------------------------------+${NC}"
    echo -e "${GREEN}|${NC}  ${CYAN}Deployment Complete!${NC}                                       ${GREEN}|${NC}"
    echo -e "${GREEN}+--------------------------------------------------------------+${NC}"
    echo ""
    echo "  Access the demo at: http://$(hostname -I | awk '{print $1}')"
    echo ""
    echo "  View logs: docker-compose logs -f"
    echo ""
}

# =============================================================================
# Update
# =============================================================================

update() {
    echo_step "Updating {{PRODUCT}} Demo..."

    cd "$PROJECT_ROOT"

    # Pull latest code
    if [ -d ".git" ]; then
        git pull origin main
    fi

    # Rebuild and restart
    deploy
}

# =============================================================================
# Main
# =============================================================================

case "${1:-}" in
    --setup)
        setup
        ;;
    --ssl)
        setup_ssl
        ;;
    --update)
        update
        ;;
    *)
        deploy
        ;;
esac
