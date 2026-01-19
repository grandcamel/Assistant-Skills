# {{PRODUCT}} Demo Container
# Based on Claude Code devcontainer with plugin pre-installed

ARG BASE_IMAGE=grandcamel/claude-devcontainer:enhanced
FROM ${BASE_IMAGE}

# Install additional dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ttyd \
    && rm -rf /var/lib/apt/lists/*

# Create demo user
RUN useradd -m -s /bin/bash demo

# Copy entrypoint and scenarios
COPY entrypoint.sh /entrypoint.sh
COPY scenarios/ /opt/scenarios/
COPY motd /etc/motd

RUN chmod +x /entrypoint.sh

# Set working directory
WORKDIR /home/demo

USER demo

ENTRYPOINT ["/entrypoint.sh"]
