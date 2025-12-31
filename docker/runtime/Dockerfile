# Assistant Skills Runtime Environment
# Claude Code CLI with Python support for running Assistant Skills plugins
#
# Usage:
#   docker run -it \
#     -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
#     -v $(pwd):/workspace \
#     -v ~/.claude:/home/claude/.claude \
#     ghcr.io/grandcamel/assistant-skills:latest

ARG NODE_VERSION=20
ARG PYTHON_VERSION=3.11

FROM node:${NODE_VERSION}-slim AS base

LABEL maintainer="Jason Krueger <grandcamel@github.com>"
LABEL description="Claude Code CLI with Assistant Skills Python environment"
LABEL org.opencontainers.image.source="https://github.com/grandcamel/Assistant-Skills"

# Install Python and system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    git \
    curl \
    jq \
    && rm -rf /var/lib/apt/lists/* \
    && ln -sf /usr/bin/python3 /usr/bin/python

# Create non-root user for security
RUN groupadd -g 1000 claude && \
    useradd -m -u 1000 -g claude claude

# Install Claude Code CLI globally
RUN npm install -g @anthropic-ai/claude-code

# Create directories
RUN mkdir -p /home/claude/.claude /home/claude/.assistant-skills-venv /workspace && \
    chown -R claude:claude /home/claude /workspace

# Switch to non-root user
USER claude
WORKDIR /home/claude

# Create the shared venv
RUN python -m venv /home/claude/.assistant-skills-venv

# Set environment for venv
ENV VIRTUAL_ENV=/home/claude/.assistant-skills-venv
ENV PATH="/home/claude/.assistant-skills-venv/bin:$PATH"

# Install base Python dependencies
RUN pip install --upgrade pip && \
    pip install assistant-skills-lib requests pyyaml python-dotenv

# Copy entrypoint script (path relative to build context)
COPY --chown=claude:claude docker/runtime/entrypoint.sh /home/claude/entrypoint.sh
RUN chmod +x /home/claude/entrypoint.sh

# Default working directory for user projects
WORKDIR /workspace

# Environment variables for configuration
ENV CLAUDE_PLUGINS=""
ENV CLAUDE_MARKETPLACES=""
ENV CLAUDE_REFRESH_PLUGINS="true"

ENTRYPOINT ["/home/claude/entrypoint.sh"]
CMD ["claude"]
