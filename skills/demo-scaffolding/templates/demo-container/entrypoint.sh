#!/bin/bash
# {{PRODUCT}} Demo Container Entrypoint

set -e

# Display welcome message
cat /etc/motd

echo ""
echo "{{PRODUCT}} Assistant Skills Demo"
echo "================================="
echo ""

# Start Claude Code
exec claude --dangerously-skip-permissions
