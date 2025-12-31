#!/bin/bash
# Assistant Skills Docker Entrypoint
# Handles plugin installation, marketplace refresh, and Claude startup

set -e

CLAUDE_DIR="$HOME/.claude"
CONFIG_DIR="$HOME/.assistant-skills"
VENV_DIR="$HOME/.assistant-skills-venv"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Ensure directories exist
mkdir -p "$CLAUDE_DIR/plugins" "$CONFIG_DIR"

# Install a plugin from GitHub repo or URL
install_plugin() {
    local spec="$1"
    local plugin_dir=""
    local repo_name=""

    # Determine if it's a full URL or owner/repo format
    if [[ "$spec" == http* ]]; then
        # Full URL - extract repo name from URL
        repo_name=$(basename "$spec" .git)
        plugin_dir="$CLAUDE_DIR/plugins/$repo_name"
    elif [[ "$spec" == */* ]]; then
        # owner/repo format
        repo_name=$(basename "$spec")
        plugin_dir="$CLAUDE_DIR/plugins/$repo_name"
        spec="https://github.com/$spec.git"
    else
        log_error "Invalid plugin spec: $spec (use owner/repo or full URL)"
        return 1
    fi

    if [ -d "$plugin_dir" ]; then
        if [ "$CLAUDE_REFRESH_PLUGINS" = "true" ]; then
            log_info "Updating plugin: $repo_name"
            cd "$plugin_dir" && git pull --quiet
            log_success "Updated: $repo_name"
        else
            log_info "Plugin already installed: $repo_name (skipping)"
        fi
    else
        log_info "Installing plugin: $repo_name"
        git clone --quiet "$spec" "$plugin_dir"
        log_success "Installed: $repo_name"
    fi

    # Install requirements if present
    if [ -f "$plugin_dir/requirements.txt" ]; then
        log_info "Installing Python dependencies for $repo_name"
        pip install -q -r "$plugin_dir/requirements.txt"
    fi

    # Check for plugin.json assistant_skills requirements
    if [ -f "$plugin_dir/plugin.json" ] || [ -f "$plugin_dir/.claude-plugin/plugin.json" ]; then
        local plugin_json=""
        if [ -f "$plugin_dir/.claude-plugin/plugin.json" ]; then
            plugin_json="$plugin_dir/.claude-plugin/plugin.json"
        else
            plugin_json="$plugin_dir/plugin.json"
        fi

        local req_path=$(jq -r '.assistant_skills.requirements // empty' "$plugin_json" 2>/dev/null)
        if [ -n "$req_path" ] && [ -f "$plugin_dir/$req_path" ]; then
            log_info "Installing assistant_skills dependencies for $repo_name"
            pip install -q -r "$plugin_dir/$req_path"
        fi
    fi
}

# Install a marketplace and its plugins
install_marketplace() {
    local spec="$1"
    local marketplace_dir=""
    local repo_name=""

    # Determine if it's a full URL or owner/repo format
    if [[ "$spec" == http* ]]; then
        repo_name=$(basename "$spec" .git)
        marketplace_dir="$CLAUDE_DIR/plugins/$repo_name"
    elif [[ "$spec" == */* ]]; then
        repo_name=$(basename "$spec")
        marketplace_dir="$CLAUDE_DIR/plugins/$repo_name"
        spec="https://github.com/$spec.git"
    else
        log_error "Invalid marketplace spec: $spec"
        return 1
    fi

    # Install the marketplace itself as a plugin first
    install_plugin "$spec"

    # Look for marketplace.json
    local marketplace_json=""
    if [ -f "$marketplace_dir/.claude-plugin/marketplace.json" ]; then
        marketplace_json="$marketplace_dir/.claude-plugin/marketplace.json"
    elif [ -f "$marketplace_dir/marketplace.json" ]; then
        marketplace_json="$marketplace_dir/marketplace.json"
    fi

    if [ -n "$marketplace_json" ] && [ -f "$marketplace_json" ]; then
        log_info "Processing marketplace: $repo_name"

        # Extract and install featured/listed plugins
        local plugins=$(jq -r '.plugins[]?.repo // empty' "$marketplace_json" 2>/dev/null)
        for plugin in $plugins; do
            if [ -n "$plugin" ]; then
                install_plugin "$plugin"
            fi
        done
    fi
}

# Check authentication
check_auth() {
    if [ -n "$ANTHROPIC_API_KEY" ]; then
        log_success "Using API key authentication"
        return 0
    fi

    # Check for OAuth token in ~/.claude
    if [ -f "$CLAUDE_DIR/.credentials.json" ]; then
        log_success "Using OAuth authentication (existing credentials)"
        return 0
    fi

    log_warn "No authentication configured"
    log_info "Set ANTHROPIC_API_KEY or mount ~/.claude with OAuth credentials"
    return 0  # Don't fail - Claude will prompt for auth
}

# Main setup
main() {
    echo ""
    echo "========================================"
    echo "  Assistant Skills Docker Environment"
    echo "========================================"
    echo ""

    # Check authentication
    check_auth

    # Install marketplaces (which include their plugins)
    if [ -n "$CLAUDE_MARKETPLACES" ]; then
        log_info "Installing marketplaces..."
        IFS=',' read -ra MARKETPLACES <<< "$CLAUDE_MARKETPLACES"
        for marketplace in "${MARKETPLACES[@]}"; do
            marketplace=$(echo "$marketplace" | xargs)  # Trim whitespace
            if [ -n "$marketplace" ]; then
                install_marketplace "$marketplace"
            fi
        done
    fi

    # Install additional plugins
    if [ -n "$CLAUDE_PLUGINS" ]; then
        log_info "Installing plugins..."
        IFS=',' read -ra PLUGINS <<< "$CLAUDE_PLUGINS"
        for plugin in "${PLUGINS[@]}"; do
            plugin=$(echo "$plugin" | xargs)  # Trim whitespace
            if [ -n "$plugin" ]; then
                install_plugin "$plugin"
            fi
        done
    fi

    # Default: install Assistant-Skills marketplace
    if [ -z "$CLAUDE_MARKETPLACES" ] && [ -z "$CLAUDE_PLUGINS" ]; then
        log_info "Installing default Assistant-Skills marketplace..."
        install_marketplace "grandcamel/Assistant-Skills"
    fi

    echo ""
    log_success "Setup complete!"
    echo ""

    # Execute the command
    # If first arg starts with - or is empty, prepend 'claude'
    if [ $# -eq 0 ] || [ "${1#-}" != "$1" ]; then
        exec claude "$@"
    else
        exec "$@"
    fi
}

main "$@"
