"""Fixtures for live integration tests."""

import os
import pytest
from pathlib import Path


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "live: mark test as live integration test")
    config.addinivalue_line("markers", "integration: mark test as integration test")


@pytest.fixture(scope="session")
def live_test_enabled():
    """Check if live tests are enabled."""
    return os.getenv("LIVE_TEST_ENABLED", "false").lower() == "true"


@pytest.fixture(scope="session")
def project_root():
    """Get the project root directory."""
    # In Docker, the project is mounted at /app
    # Locally, we need to find the root by looking for .claude-plugin
    docker_root = Path("/app")
    if docker_root.exists() and (docker_root / ".claude-plugin").exists():
        return docker_root
    
    # Fall back to finding root from test file location
    current = Path(__file__).resolve()
    while current != current.parent:
        if (current / ".claude-plugin").exists():
            return current
        current = current.parent
    
    # Last resort - assume we're 6 levels deep from root
    return Path(__file__).parent.parent.parent.parent.parent.parent


@pytest.fixture(scope="session")
def reference_projects():
    """Get paths to reference projects if they exist."""
    home = Path.home()
    projects = {
        "jira": home / "IdeaProjects" / "Jira-Assistant-Skills",
        "confluence": home / "IdeaProjects" / "Confluence-Assistant-Skills", 
        "splunk": home / "IdeaProjects" / "Splunk-Assistant-Skills",
    }
    return {name: path for name, path in projects.items() if path.exists()}
