#!/bin/bash
# =============================================================================
# {{PRODUCT}} Demo Health Check
# =============================================================================
# Checks the health of all demo system components.
#
# Usage:
#   ./healthcheck.sh
#   ./healthcheck.sh --verbose
# =============================================================================

set -e

VERBOSE=${1:-}

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

check_pass() { echo -e "  ${GREEN}+${NC} $1"; }
check_fail() { echo -e "  ${RED}x${NC} $1"; }
check_warn() { echo -e "  ${YELLOW}!${NC} $1"; }

echo "{{PRODUCT}} Demo Health Check"
echo "============================="
echo ""

ERRORS=0

# Check nginx/landing page
echo "Web Server:"
if curl -sf http://localhost/health > /dev/null 2>&1; then
    check_pass "Landing page responding"
else
    check_fail "Landing page not responding"
    ERRORS=$((ERRORS + 1))
fi

# Check queue manager API
echo ""
echo "Queue Manager:"
if curl -sf http://localhost/api/health > /dev/null 2>&1; then
    check_pass "API responding"

    # Get status
    STATUS=$(curl -sf http://localhost/api/status 2>/dev/null)
    if [ -n "$STATUS" ] && [ "$VERBOSE" = "--verbose" ]; then
        echo "    Status: $STATUS"
    fi
else
    check_fail "API not responding"
    ERRORS=$((ERRORS + 1))
fi

# Check Redis
echo ""
echo "Redis:"
if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
    check_pass "Redis responding"
else
    check_fail "Redis not responding"
    ERRORS=$((ERRORS + 1))
fi

# Check Docker
echo ""
echo "Docker:"
if docker ps > /dev/null 2>&1; then
    check_pass "Docker daemon running"

    # Count running containers
    CONTAINERS=$(docker-compose ps -q 2>/dev/null | wc -l)
    if [ "$CONTAINERS" -ge 3 ]; then
        check_pass "$CONTAINERS containers running"
    else
        check_warn "Only $CONTAINERS containers running (expected 3+)"
    fi
else
    check_fail "Docker daemon not responding"
    ERRORS=$((ERRORS + 1))
fi

# Check demo container image
echo ""
echo "Demo Container:"
if docker image inspect {{CONTAINER_IMAGE}} > /dev/null 2>&1; then
    check_pass "Demo container image exists"
else
    check_warn "Demo container image not built"
fi

# Check API connectivity (if credentials available)
echo ""
echo "{{PRODUCT}} Connectivity:"
if [ -f "secrets/.env" ]; then
    source secrets/.env
    if [ -n "${{API_TOKEN_VAR}}" ]; then
        check_pass "{{PRODUCT}} credentials configured"
    else
        check_warn "{{PRODUCT}} credentials not configured"
    fi
else
    check_warn "secrets/.env not found"
fi

# Summary
echo ""
echo "============================="
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}All checks passed!${NC}"
    exit 0
else
    echo -e "${RED}$ERRORS check(s) failed${NC}"
    exit 1
fi
