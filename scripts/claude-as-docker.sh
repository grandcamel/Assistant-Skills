#!/bin/bash
# claude-as-docker - Run Claude Code with Assistant Skills in Docker
#
# Usage:
#   claude-as-docker                    # Run with defaults
#   claude-as-docker -p "your prompt"   # Run with prompt
#   claude-as-docker --help             # Show help
#
# Environment Variables:
#   ANTHROPIC_API_KEY     - API key for authentication
#   CLAUDE_PLUGINS        - Comma-separated list of plugins to install
#   CLAUDE_MARKETPLACES   - Comma-separated list of marketplaces to install
#   CLAUDE_REFRESH_PLUGINS - Set to "false" to skip plugin updates
#
# Examples:
#   # Basic usage with API key
#   ANTHROPIC_API_KEY=sk-... claude-as-docker
#
#   # Install additional plugins
#   CLAUDE_PLUGINS="owner/plugin1,owner/plugin2" claude-as-docker
#
#   # Use with OAuth (mount existing credentials)
#   claude-as-docker --oauth

set -e

# Configuration
IMAGE_NAME="${CLAUDE_AS_IMAGE:-ghcr.io/grandcamel/assistant-skills:latest}"
CLAUDE_HOME="${CLAUDE_HOME:-$HOME/.claude}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

show_help() {
    cat << 'EOF'
claude-as-docker - Run Claude Code with Assistant Skills in Docker

USAGE:
    claude-as-docker [OPTIONS] [-- CLAUDE_ARGS...]

OPTIONS:
    -h, --help          Show this help message
    --pull              Pull the latest image before running
    --oauth             Use OAuth authentication (mounts ~/.claude)
    --no-refresh        Skip plugin updates on startup
    --image IMAGE       Use a custom Docker image
    --shell             Start a bash shell instead of Claude

ENVIRONMENT VARIABLES:
    ANTHROPIC_API_KEY       API key for Claude authentication
    CLAUDE_PLUGINS          Comma-separated plugin repos (owner/repo or URLs)
    CLAUDE_MARKETPLACES     Comma-separated marketplace repos
    CLAUDE_REFRESH_PLUGINS  Set to "false" to skip updates (default: true)
    CLAUDE_AS_IMAGE         Override the Docker image

EXAMPLES:
    # Run with API key
    export ANTHROPIC_API_KEY=sk-ant-...
    claude-as-docker

    # Run with a prompt
    claude-as-docker -- -p "Help me with Python"

    # Install additional plugins
    CLAUDE_PLUGINS="owner/my-plugin" claude-as-docker

    # Use OAuth authentication
    claude-as-docker --oauth

    # Install from multiple marketplaces
    CLAUDE_MARKETPLACES="grandcamel/Assistant-Skills,other/marketplace" claude-as-docker

EOF
}

# Parse arguments
PULL_LATEST=false
USE_OAUTH=false
REFRESH_PLUGINS=true
CUSTOM_IMAGE=""
START_SHELL=false
CLAUDE_ARGS=()

while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--help)
            show_help
            exit 0
            ;;
        --pull)
            PULL_LATEST=true
            shift
            ;;
        --oauth)
            USE_OAUTH=true
            shift
            ;;
        --no-refresh)
            REFRESH_PLUGINS=false
            shift
            ;;
        --image)
            CUSTOM_IMAGE="$2"
            shift 2
            ;;
        --shell)
            START_SHELL=true
            shift
            ;;
        --)
            shift
            CLAUDE_ARGS=("$@")
            break
            ;;
        *)
            CLAUDE_ARGS+=("$1")
            shift
            ;;
    esac
done

# Use custom image if provided
if [ -n "$CUSTOM_IMAGE" ]; then
    IMAGE_NAME="$CUSTOM_IMAGE"
fi

# Pull latest if requested
if [ "$PULL_LATEST" = true ]; then
    echo -e "${BLUE}[INFO]${NC} Pulling latest image..."
    docker pull "$IMAGE_NAME"
fi

# Build docker run command
DOCKER_ARGS=(
    "run"
    "-it"
    "--rm"
    "-v" "$(pwd):/workspace"
    "-v" "$CLAUDE_HOME:/home/claude/.claude"
    "-w" "/workspace"
)

# Add API key if set
if [ -n "$ANTHROPIC_API_KEY" ]; then
    DOCKER_ARGS+=("-e" "ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY")
fi

# Add plugin configuration
if [ -n "$CLAUDE_PLUGINS" ]; then
    DOCKER_ARGS+=("-e" "CLAUDE_PLUGINS=$CLAUDE_PLUGINS")
fi

if [ -n "$CLAUDE_MARKETPLACES" ]; then
    DOCKER_ARGS+=("-e" "CLAUDE_MARKETPLACES=$CLAUDE_MARKETPLACES")
fi

# Set refresh preference
if [ "$REFRESH_PLUGINS" = false ] || [ "$CLAUDE_REFRESH_PLUGINS" = "false" ]; then
    DOCKER_ARGS+=("-e" "CLAUDE_REFRESH_PLUGINS=false")
fi

# Add the image
DOCKER_ARGS+=("$IMAGE_NAME")

# Add command
if [ "$START_SHELL" = true ]; then
    DOCKER_ARGS+=("bash")
else
    DOCKER_ARGS+=("claude" "${CLAUDE_ARGS[@]}")
fi

# Run Docker
exec docker "${DOCKER_ARGS[@]}"
