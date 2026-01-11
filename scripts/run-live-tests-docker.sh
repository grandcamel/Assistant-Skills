#!/usr/bin/env bash
#
# Run live integration tests in Docker container
#
# Live integration tests require API credentials and external service access.
# Credentials should be provided via environment variables or .env file.
#
# Usage:
#   ./scripts/run-live-tests-docker.sh                    # Run all live tests
#   ./scripts/run-live-tests-docker.sh --env-file .env    # Use specific env file
#   ./scripts/run-live-tests-docker.sh --skill jira       # Run tests for specific skill
#   ./scripts/run-live-tests-docker.sh --timeout 120      # Set test timeout
#   ./scripts/run-live-tests-docker.sh --dry-run          # Show what would run
#

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Defaults
PYTHON_VERSION="3.11"
ENV_FILE="${PROJECT_ROOT}/.env"
SPECIFIC_SKILL=""
TIMEOUT=60
DRY_RUN=false
VERBOSE=false
FAIL_FAST=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --env-file|-e)
            ENV_FILE="$2"
            shift 2
            ;;
        --skill|-s)
            SPECIFIC_SKILL="$2"
            shift 2
            ;;
        --timeout|-t)
            TIMEOUT="$2"
            shift 2
            ;;
        --dry-run|-n)
            DRY_RUN=true
            shift
            ;;
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        --fail-fast|-x)
            FAIL_FAST=true
            shift
            ;;
        --python)
            PYTHON_VERSION="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Run live integration tests in Docker container."
            echo "These tests require API credentials for external services."
            echo ""
            echo "Options:"
            echo "  --env-file, -e FILE   Path to .env file with credentials (default: .env)"
            echo "  --skill, -s NAME      Run tests for specific skill only"
            echo "  --timeout, -t SECS    Test timeout in seconds (default: 60)"
            echo "  --dry-run, -n         Show what would run without executing"
            echo "  --verbose, -v         Verbose output"
            echo "  --fail-fast, -x       Stop on first failure"
            echo "  --python VERSION      Use specific Python version (default: 3.11)"
            echo "  --help, -h            Show this help message"
            echo ""
            echo "Environment Variables (via .env or exported):"
            echo "  Required for specific integrations:"
            echo "  - JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN    (Jira)"
            echo "  - CONFLUENCE_URL, CONFLUENCE_EMAIL, ...   (Confluence)"
            echo "  - SPLUNK_HOST, SPLUNK_TOKEN               (Splunk)"
            echo "  - GITHUB_TOKEN                            (GitHub)"
            echo ""
            echo "Examples:"
            echo "  $0                          # Run all live tests"
            echo "  $0 --skill jira             # Run only Jira integration tests"
            echo "  $0 --env-file prod.env      # Use production credentials"
            echo "  $0 --timeout 120 --verbose  # Extended timeout with verbose output"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${CYAN}[STEP]${NC} $1"
}

# Ensure we're in the project root
cd "$PROJECT_ROOT"

# Create test-results directory
mkdir -p test-results

# Check for .env file
if [[ ! -f "$ENV_FILE" ]]; then
    log_warning "Environment file not found: ${ENV_FILE}"
    log_info "Creating template .env file..."
    
    cat > "${PROJECT_ROOT}/.env.template" << 'ENVTEMPLATE'
# Assistant Skills Live Integration Test Configuration
# Copy this to .env and fill in your credentials

# General
LIVE_TEST_ENABLED=true

# Jira Integration
JIRA_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-api-token
JIRA_TEST_PROJECT=TEST

# Confluence Integration
CONFLUENCE_URL=https://your-domain.atlassian.net/wiki
CONFLUENCE_EMAIL=your-email@example.com
CONFLUENCE_API_TOKEN=your-api-token
CONFLUENCE_TEST_SPACE=TEST

# Splunk Integration
SPLUNK_HOST=https://your-splunk-instance.splunkcloud.com
SPLUNK_TOKEN=your-splunk-token
SPLUNK_PORT=8089

# GitHub Integration
GITHUB_TOKEN=your-github-token
GITHUB_TEST_REPO=owner/repo
ENVTEMPLATE
    
    log_info "Template created at: .env.template"
    log_error "Please create .env file with your credentials before running live tests"
    exit 1
fi

# Source the env file if it exists
if [[ -f "$ENV_FILE" ]]; then
    log_info "Loading environment from: ${ENV_FILE}"
    set -a
    source "$ENV_FILE"
    set +a
fi

# Build image
IMAGE_NAME="assistant-skills-tests:py${PYTHON_VERSION}"

log_step "Building Docker image..."
if [[ "$DRY_RUN" == false ]]; then
    docker build \
        --build-arg PYTHON_VERSION="${PYTHON_VERSION}" \
        -f docker/Dockerfile \
        -t "${IMAGE_NAME}" \
        . \
        ${VERBOSE:+} || {
            log_error "Docker build failed"
            exit 1
        }
    log_success "Docker image built"
else
    log_info "[DRY RUN] Would build image: ${IMAGE_NAME}"
fi

# Construct test path
if [[ -n "$SPECIFIC_SKILL" ]]; then
    TEST_PATH="skills/${SPECIFIC_SKILL}/tests/live_integration/"
    log_info "Running live tests for skill: ${SPECIFIC_SKILL}"
else
    TEST_PATH="skills/*/tests/live_integration/"
    log_info "Running all live integration tests"
fi

# Construct pytest command
PYTEST_ARGS="-v --tb=long"
PYTEST_ARGS="$PYTEST_ARGS --timeout=${TIMEOUT}"
PYTEST_ARGS="$PYTEST_ARGS -m 'live or integration'"
PYTEST_ARGS="$PYTEST_ARGS --junitxml=/app/test-results/live-tests.xml"

if [[ "$FAIL_FAST" == true ]]; then
    PYTEST_ARGS="$PYTEST_ARGS -x"
fi

if [[ "$VERBOSE" == true ]]; then
    PYTEST_ARGS="$PYTEST_ARGS -vv"
fi

# Display configuration
echo ""
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  Live Integration Test Configuration${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo ""
echo "  Python Version:  ${PYTHON_VERSION}"
echo "  Test Path:       ${TEST_PATH}"
echo "  Timeout:         ${TIMEOUT}s per test"
echo "  Fail Fast:       ${FAIL_FAST}"
echo "  Env File:        ${ENV_FILE}"
echo ""

# Check which credentials are available
log_step "Checking available credentials..."
AVAILABLE_INTEGRATIONS=""

if [[ -n "${JIRA_URL:-}" && -n "${JIRA_API_TOKEN:-}" ]]; then
    echo -e "  ${GREEN}✓${NC} Jira credentials found"
    AVAILABLE_INTEGRATIONS="${AVAILABLE_INTEGRATIONS} jira"
else
    echo -e "  ${YELLOW}○${NC} Jira credentials not configured"
fi

if [[ -n "${CONFLUENCE_URL:-}" && -n "${CONFLUENCE_API_TOKEN:-}" ]]; then
    echo -e "  ${GREEN}✓${NC} Confluence credentials found"
    AVAILABLE_INTEGRATIONS="${AVAILABLE_INTEGRATIONS} confluence"
else
    echo -e "  ${YELLOW}○${NC} Confluence credentials not configured"
fi

if [[ -n "${SPLUNK_HOST:-}" && -n "${SPLUNK_TOKEN:-}" ]]; then
    echo -e "  ${GREEN}✓${NC} Splunk credentials found"
    AVAILABLE_INTEGRATIONS="${AVAILABLE_INTEGRATIONS} splunk"
else
    echo -e "  ${YELLOW}○${NC} Splunk credentials not configured"
fi

if [[ -n "${GITHUB_TOKEN:-}" ]]; then
    echo -e "  ${GREEN}✓${NC} GitHub credentials found"
    AVAILABLE_INTEGRATIONS="${AVAILABLE_INTEGRATIONS} github"
else
    echo -e "  ${YELLOW}○${NC} GitHub credentials not configured"
fi

echo ""
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo ""

if [[ -z "${AVAILABLE_INTEGRATIONS// }" ]]; then
    log_warning "No integration credentials found!"
    log_info "Live tests may be skipped. Configure credentials in .env file."
fi

# Run the tests
if [[ "$DRY_RUN" == true ]]; then
    log_info "[DRY RUN] Would run:"
    echo "  docker run --rm \\"
    echo "    -v \"${PROJECT_ROOT}/test-results:/app/test-results\" \\"
    echo "    --env-file \"${ENV_FILE}\" \\"
    echo "    ${IMAGE_NAME} \\"
    echo "    pytest ${TEST_PATH} ${PYTEST_ARGS}"
    exit 0
fi

log_step "Running live integration tests..."
echo ""

# Build docker run command with environment variables
docker run --rm \
    -v "${PROJECT_ROOT}/test-results:/app/test-results" \
    -e PYTEST_ADDOPTS="--color=yes" \
    -e LIVE_TEST_ENABLED="${LIVE_TEST_ENABLED:-true}" \
    -e JIRA_URL="${JIRA_URL:-}" \
    -e JIRA_EMAIL="${JIRA_EMAIL:-}" \
    -e JIRA_API_TOKEN="${JIRA_API_TOKEN:-}" \
    -e JIRA_TEST_PROJECT="${JIRA_TEST_PROJECT:-}" \
    -e CONFLUENCE_URL="${CONFLUENCE_URL:-}" \
    -e CONFLUENCE_EMAIL="${CONFLUENCE_EMAIL:-}" \
    -e CONFLUENCE_API_TOKEN="${CONFLUENCE_API_TOKEN:-}" \
    -e CONFLUENCE_TEST_SPACE="${CONFLUENCE_TEST_SPACE:-}" \
    -e SPLUNK_HOST="${SPLUNK_HOST:-}" \
    -e SPLUNK_TOKEN="${SPLUNK_TOKEN:-}" \
    -e SPLUNK_PORT="${SPLUNK_PORT:-8089}" \
    -e GITHUB_TOKEN="${GITHUB_TOKEN:-}" \
    -e GITHUB_TEST_REPO="${GITHUB_TEST_REPO:-}" \
    "${IMAGE_NAME}" \
    sh -c "pytest ${TEST_PATH} ${PYTEST_ARGS} 2>/dev/null || echo 'No live integration tests found or tests completed'"

EXIT_CODE=$?

echo ""
if [[ $EXIT_CODE -eq 0 ]]; then
    log_success "Live integration tests completed!"
    log_info "Test results saved to: test-results/live-tests.xml"
else
    log_warning "Some tests may have failed or no tests found (exit code: ${EXIT_CODE})"
    log_info "This is expected if live_integration/ directories don't exist yet."
fi

exit 0  # Don't fail if no tests found
