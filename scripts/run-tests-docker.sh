#!/usr/bin/env bash
#
# Run unit tests in Docker container
#
# Usage:
#   ./scripts/run-tests-docker.sh              # Run all unit tests
#   ./scripts/run-tests-docker.sh --parallel   # Run tests in parallel
#   ./scripts/run-tests-docker.sh --coverage   # Run with coverage report
#   ./scripts/run-tests-docker.sh --quick      # Run smoke tests only
#   ./scripts/run-tests-docker.sh --file test_validate_project.py  # Run specific file
#   ./scripts/run-tests-docker.sh --python 3.9 # Use specific Python version
#

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Defaults
PYTHON_VERSION="3.11"
PARALLEL=false
COVERAGE=false
QUICK=false
SPECIFIC_FILE=""
VERBOSE=false
BUILD_ONLY=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --parallel|-p)
            PARALLEL=true
            shift
            ;;
        --coverage|-c)
            COVERAGE=true
            shift
            ;;
        --quick|-q)
            QUICK=true
            shift
            ;;
        --file|-f)
            SPECIFIC_FILE="$2"
            shift 2
            ;;
        --python)
            PYTHON_VERSION="$2"
            shift 2
            ;;
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        --build-only)
            BUILD_ONLY=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --parallel, -p    Run tests in parallel using pytest-xdist"
            echo "  --coverage, -c    Generate coverage report"
            echo "  --quick, -q       Run smoke tests only"
            echo "  --file, -f FILE   Run specific test file"
            echo "  --python VERSION  Use specific Python version (default: 3.11)"
            echo "  --verbose, -v     Verbose output"
            echo "  --build-only      Only build the Docker image, don't run tests"
            echo "  --help, -h        Show this help message"
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

# Ensure we're in the project root
cd "$PROJECT_ROOT"

# Create test-results directory
mkdir -p test-results

# Build the Docker image
IMAGE_NAME="assistant-skills-tests:py${PYTHON_VERSION}"
log_info "Building Docker image: ${IMAGE_NAME}"

docker build \
    --build-arg PYTHON_VERSION="${PYTHON_VERSION}" \
    -f docker/Dockerfile \
    -t "${IMAGE_NAME}" \
    . \
    ${VERBOSE:+} || {
        log_error "Docker build failed"
        exit 1
    }

log_success "Docker image built successfully"

if [[ "$BUILD_ONLY" == true ]]; then
    log_info "Build-only mode, skipping test execution"
    exit 0
fi

# Construct pytest command
PYTEST_CMD="pytest"
PYTEST_ARGS="-v --tb=short"

if [[ "$QUICK" == true ]]; then
    PYTEST_ARGS="$PYTEST_ARGS skills/assistant-builder/tests/test_validate_project.py -x"
    log_info "Running quick smoke tests"
elif [[ -n "$SPECIFIC_FILE" ]]; then
    PYTEST_ARGS="$PYTEST_ARGS skills/assistant-builder/tests/${SPECIFIC_FILE}"
    log_info "Running specific test file: ${SPECIFIC_FILE}"
else
    PYTEST_ARGS="$PYTEST_ARGS skills/assistant-builder/tests/"
    log_info "Running all unit tests"
fi

if [[ "$PARALLEL" == true ]]; then
    PYTEST_ARGS="$PYTEST_ARGS -n auto"
    log_info "Parallel execution enabled"
fi

if [[ "$COVERAGE" == true ]]; then
    PYTEST_ARGS="$PYTEST_ARGS --cov=skills --cov-report=xml:/app/test-results/coverage.xml --cov-report=term-missing"
    log_info "Coverage reporting enabled"
fi

PYTEST_ARGS="$PYTEST_ARGS --junitxml=/app/test-results/unit-tests.xml"

# Run the tests
log_info "Running tests..."
echo ""

docker run --rm \
    -v "${PROJECT_ROOT}/test-results:/app/test-results" \
    -e PYTHONPATH="/app/skills/shared/scripts/lib:/app/.claude/skills/shared/scripts/lib" \
    -e PYTEST_ADDOPTS="--color=yes" \
    "${IMAGE_NAME}" \
    ${PYTEST_CMD} ${PYTEST_ARGS}

EXIT_CODE=$?

echo ""
if [[ $EXIT_CODE -eq 0 ]]; then
    log_success "All tests passed!"
    log_info "Test results saved to: test-results/unit-tests.xml"
    if [[ "$COVERAGE" == true ]]; then
        log_info "Coverage report saved to: test-results/coverage.xml"
    fi
else
    log_error "Some tests failed (exit code: ${EXIT_CODE})"
fi

exit $EXIT_CODE
