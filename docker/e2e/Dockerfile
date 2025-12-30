# E2E Testing Container for Claude Code Plugins
# Includes Claude Code CLI, Python, and test infrastructure

FROM node:20-slim

# Install Python and dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create symlinks for python
RUN ln -sf /usr/bin/python3 /usr/bin/python

# Install Claude Code CLI
RUN npm install -g @anthropic-ai/claude-code

# Set up working directory
WORKDIR /workspace

# Create virtual environment for Python dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python test dependencies
COPY requirements-e2e.txt /tmp/requirements-e2e.txt
RUN pip install --no-cache-dir -r /tmp/requirements-e2e.txt

# Create non-root user for security (--dangerously-skip-permissions won't work as root)
RUN useradd -m -s /bin/bash testuser && \
    mkdir -p /home/testuser/.claude/debug /home/testuser/.claude/projects /home/testuser/.claude/settings && \
    chown -R testuser:testuser /home/testuser/.claude && \
    chmod -R 755 /home/testuser/.claude

# Copy the plugin source and set ownership
COPY --chown=testuser:testuser . /workspace/plugin-source

# Create entrypoint script inline (docker/ is in .dockerignore)
RUN printf '%s\n' \
    '#!/bin/bash' \
    'set -e' \
    'mkdir -p $HOME/.claude/debug $HOME/.claude/projects $HOME/.claude/settings' \
    'chmod -R 755 $HOME/.claude 2>/dev/null || true' \
    'if [ -f /tmp/claude-credentials/credentials.json ]; then' \
    '    cp /tmp/claude-credentials/credentials.json $HOME/.claude/credentials.json' \
    '    chmod 600 $HOME/.claude/credentials.json' \
    'fi' \
    'if [ -n "$ANTHROPIC_API_KEY" ]; then' \
    '    echo "Using ANTHROPIC_API_KEY for authentication"' \
    'elif [ -f $HOME/.claude/credentials.json ]; then' \
    '    echo "Using OAuth credentials for authentication"' \
    'else' \
    '    echo "WARNING: No authentication configured"' \
    'fi' \
    'exec "$@"' \
    > /entrypoint.sh && chmod +x /entrypoint.sh

# Switch to non-root user
USER testuser
ENV HOME=/home/testuser

# Environment variables for Claude Code
# ANTHROPIC_API_KEY must be provided at runtime
ENV CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
ENV CLAUDE_CODE_SKIP_OOBE=1
ENV CI=true

# Use entrypoint to setup credentials before running tests
ENTRYPOINT ["/entrypoint.sh"]

# Default command runs the E2E test suite
CMD ["python", "-m", "pytest", "tests/e2e/", "-v", "--tb=short"]
