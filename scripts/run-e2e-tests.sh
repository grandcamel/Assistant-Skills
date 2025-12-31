#!/bin/bash
#
# Run E2E tests for the Assistant-Skills plugin
#
# Usage:
#   ./scripts/run-e2e-tests.sh              # Run in Docker
#   ./scripts/run-e2e-tests.sh --local      # Run locally (no Docker)
#   ./scripts/run-e2e-tests.sh --shell      # Open interactive shell in Docker
#
# Environment variables:
#   ANTHROPIC_API_KEY     - API key for Claude (required)
#   E2E_TEST_TIMEOUT      - Timeout per test in seconds (default: 120)
#   E2E_TEST_MODEL        - Claude model to use (default: claude-sonnet-4-20250514)
#   E2E_MAX_TURNS         - Max conversation turns per test (default: 5)
#   E2E_VERBOSE           - Enable verbose output (default: false)
#
# Alternative authentication:
#   - Mount ~/.claude directory for OAuth credentials
#   - Use Claude Code's built-in authentication
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
USE_DOCKER=true
OPEN_SHELL=false
VERBOSE=${E2E_VERBOSE:-false}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --local)
            USE_DOCKER=false
            shift
            ;;
        --shell)
            OPEN_SHELL=true
            shift
            ;;
        --verbose|-v)
            VERBOSE=true
            export E2E_VERBOSE=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --local     Run tests locally (without Docker)"
            echo "  --shell     Open interactive shell in Docker container"
            echo "  --verbose   Enable verbose output"
            echo "  --help      Show this help message"
            echo ""
            echo "Environment variables:"
            echo "  ANTHROPIC_API_KEY     API key for Claude (required)"
            echo "  E2E_TEST_TIMEOUT      Timeout per test in seconds (default: 120)"
            echo "  E2E_TEST_MODEL        Claude model (default: claude-sonnet-4-20250514)"
            echo "  E2E_MAX_TURNS         Max conversation turns per test (default: 5)"
            echo "  E2E_VERBOSE           Enable verbose output (default: false)"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Check authentication
check_auth() {
    # For local runs, prefer OAuth credentials
    if [[ "$USE_DOCKER" == "false" ]]; then
        # Check for OAuth credentials in ~/.claude.json (primary location)
        if [[ -f "$HOME/.claude.json" ]]; then
            echo -e "${GREEN}✓ Using Claude OAuth credentials (~/.claude.json)${NC}"
            # Unset API key to force OAuth usage
            unset ANTHROPIC_API_KEY
            return 0
        fi

        # Also check legacy location ~/.claude/credentials.json
        if [[ -f "$HOME/.claude/credentials.json" ]]; then
            echo -e "${GREEN}✓ Using Claude OAuth credentials (~/.claude/credentials.json)${NC}"
            # Unset API key to force OAuth usage
            unset ANTHROPIC_API_KEY
            return 0
        fi
    fi

    # For Docker or when no OAuth, use API key
    if [[ -n "$ANTHROPIC_API_KEY" ]]; then
        echo -e "${GREEN}✓ ANTHROPIC_API_KEY is set${NC}"
        return 0
    fi

    # Final check for OAuth (Docker case where OAuth might be mounted)
    if [[ -f "$HOME/.claude.json" ]] || [[ -f "$HOME/.claude/credentials.json" ]]; then
        echo -e "${GREEN}✓ Claude OAuth credentials found${NC}"
        return 0
    fi

    echo -e "${RED}✗ No authentication configured${NC}"
    echo ""
    echo "Please set one of the following:"
    echo "  1. Claude Code OAuth credentials (~/.claude.json) - preferred for local"
    echo "  2. ANTHROPIC_API_KEY environment variable - required for Docker"
    echo ""
    echo "To authenticate with OAuth: claude auth login"
    echo "To get an API key: https://console.anthropic.com/"
    return 1
}

# Run tests in Docker
run_docker_tests() {
    echo -e "${YELLOW}Running E2E tests in Docker...${NC}"
    echo ""

    cd "$PROJECT_ROOT"

    # Create test results directory
    mkdir -p test-results/e2e

    # Build and run
    docker compose -f docker/e2e/docker-compose.yml build e2e-tests
    docker compose -f docker/e2e/docker-compose.yml run --rm e2e-tests

    echo ""
    echo -e "${GREEN}Results saved to: test-results/e2e/${NC}"
}

# Open shell in Docker
open_docker_shell() {
    echo -e "${YELLOW}Opening interactive shell in Docker...${NC}"
    echo ""

    cd "$PROJECT_ROOT"

    docker compose -f docker/e2e/docker-compose.yml build e2e-shell
    docker compose -f docker/e2e/docker-compose.yml run --rm e2e-shell
}

# Run tests locally
run_local_tests() {
    echo -e "${YELLOW}Running E2E tests locally...${NC}"
    echo ""

    cd "$PROJECT_ROOT"

    # Check Claude Code CLI
    if ! command -v claude &> /dev/null; then
        echo -e "${RED}Claude Code CLI not found${NC}"
        echo "Install with: npm install -g @anthropic-ai/claude-code"
        exit 1
    fi

    # Install dependencies
    pip install -q -r requirements-e2e.txt

    # Run pytest
    if [[ "$VERBOSE" == "true" ]]; then
        python -m pytest tests/e2e/ -v --e2e-verbose --tb=short
    else
        python -m pytest tests/e2e/ -v --tb=short
    fi
}

# Run standalone runner (without pytest)
run_standalone() {
    echo -e "${YELLOW}Running E2E tests with standalone runner...${NC}"
    echo ""

    cd "$PROJECT_ROOT"

    if [[ "$VERBOSE" == "true" ]]; then
        python tests/e2e/runner.py --verbose
    else
        python tests/e2e/runner.py
    fi
}

# Main
main() {
    echo "========================================"
    echo "Assistant-Skills E2E Test Runner"
    echo "========================================"
    echo ""

    # Check authentication
    if ! check_auth; then
        exit 1
    fi
    echo ""

    if [[ "$OPEN_SHELL" == "true" ]]; then
        open_docker_shell
    elif [[ "$USE_DOCKER" == "true" ]]; then
        run_docker_tests
    else
        run_local_tests
    fi
}

main
