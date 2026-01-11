#!/usr/bin/env bash
#
# Unified test runner for Assistant Skills
#
# Usage:
#   ./scripts/test.sh                    # Run unit tests locally
#   ./scripts/test.sh docker             # Run unit tests in Docker
#   ./scripts/test.sh docker --coverage  # Run with coverage in Docker
#   ./scripts/test.sh live               # Run live integration tests
#   ./scripts/test.sh all                # Run all tests
#   ./scripts/test.sh matrix             # Run tests across Python versions
#

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Functions
print_header() {
    echo ""
    echo -e "${CYAN}╔═══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║  Assistant Skills Test Runner                                 ║${NC}"
    echo -e "${CYAN}╚═══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_usage() {
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  local, unit     Run unit tests locally (default)"
    echo "  docker, d       Run unit tests in Docker container"
    echo "  live, l         Run live integration tests in Docker"
    echo "  all, a          Run all tests (unit + live)"
    echo "  matrix, m       Run tests across multiple Python versions"
    echo "  compose, c      Run tests using docker-compose"
    echo "  help, h         Show this help message"
    echo ""
    echo "Options (passed to underlying scripts):"
    echo "  --coverage, -c  Generate coverage report"
    echo "  --parallel, -p  Run tests in parallel"
    echo "  --quick, -q     Run smoke tests only"
    echo "  --verbose, -v   Verbose output"
    echo "  --python VER    Use specific Python version"
    echo ""
    echo "Examples:"
    echo "  $0                         # Run unit tests locally"
    echo "  $0 docker --coverage       # Run in Docker with coverage"
    echo "  $0 live --skill jira       # Run Jira integration tests"
    echo "  $0 matrix                  # Test on Python 3.8-3.12"
    echo "  $0 compose unit-tests      # Use docker-compose"
}

run_local_tests() {
    echo -e "${BLUE}[INFO]${NC} Running unit tests locally..."
    cd "$PROJECT_ROOT"

    pytest skills/assistant-builder/tests/ -v --tb=short "$@"
}

run_docker_tests() {
    echo -e "${BLUE}[INFO]${NC} Running unit tests in Docker..."
    "${SCRIPT_DIR}/run-tests-docker.sh" "$@"
}

run_live_tests() {
    echo -e "${BLUE}[INFO]${NC} Running live integration tests..."
    "${SCRIPT_DIR}/run-live-tests-docker.sh" "$@"
}

run_all_tests() {
    echo -e "${BLUE}[INFO]${NC} Running all tests..."
    
    echo ""
    echo -e "${CYAN}━━━ Unit Tests ━━━${NC}"
    "${SCRIPT_DIR}/run-tests-docker.sh" "$@" || true
    
    echo ""
    echo -e "${CYAN}━━━ Live Integration Tests ━━━${NC}"
    "${SCRIPT_DIR}/run-live-tests-docker.sh" "$@" || true
    
    echo ""
    echo -e "${GREEN}[DONE]${NC} All test suites completed"
}

run_matrix_tests() {
    echo -e "${BLUE}[INFO]${NC} Running tests across Python versions..."
    
    local PYTHON_VERSIONS=("3.8" "3.9" "3.10" "3.11" "3.12")
    local FAILED_VERSIONS=""
    
    for PY_VER in "${PYTHON_VERSIONS[@]}"; do
        echo ""
        echo -e "${CYAN}━━━ Python ${PY_VER} ━━━${NC}"
        
        if "${SCRIPT_DIR}/run-tests-docker.sh" --python "$PY_VER" "$@"; then
            echo -e "${GREEN}[PASS]${NC} Python ${PY_VER}"
        else
            echo -e "${RED}[FAIL]${NC} Python ${PY_VER}"
            FAILED_VERSIONS="${FAILED_VERSIONS} ${PY_VER}"
        fi
    done
    
    echo ""
    echo -e "${CYAN}━━━ Matrix Results ━━━${NC}"
    if [[ -z "$FAILED_VERSIONS" ]]; then
        echo -e "${GREEN}[SUCCESS]${NC} All Python versions passed!"
    else
        echo -e "${RED}[FAILURE]${NC} Failed versions:${FAILED_VERSIONS}"
        exit 1
    fi
}

run_compose_tests() {
    local SERVICE="${1:-unit-tests}"
    shift || true
    
    echo -e "${BLUE}[INFO]${NC} Running tests via docker-compose..."
    cd "$PROJECT_ROOT"
    
    docker-compose -f docker/docker-compose.yml run --rm "$SERVICE" "$@"
}

# Main
print_header

cd "$PROJECT_ROOT"

COMMAND="${1:-local}"
shift || true

case "$COMMAND" in
    local|unit)
        run_local_tests "$@"
        ;;
    docker|d)
        run_docker_tests "$@"
        ;;
    live|l)
        run_live_tests "$@"
        ;;
    all|a)
        run_all_tests "$@"
        ;;
    matrix|m)
        run_matrix_tests "$@"
        ;;
    compose|c)
        run_compose_tests "$@"
        ;;
    help|h|--help|-h)
        print_usage
        ;;
    *)
        echo -e "${RED}Unknown command: $COMMAND${NC}"
        echo ""
        print_usage
        exit 1
        ;;
esac
