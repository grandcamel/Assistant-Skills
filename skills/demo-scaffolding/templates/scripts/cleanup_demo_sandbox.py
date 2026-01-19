#!/usr/bin/env python3
"""
Cleanup Demo Sandbox Script

Removes user-created content while preserving seed data.
Items with the 'demo' tag are preserved.

Usage:
    python cleanup_demo_sandbox.py

Environment Variables:
    {{API_URL_VAR}}: {{PRODUCT}} API URL
    {{API_TOKEN_VAR}}: API token
    DEMO_PRESERVE_TAG: Tag for preserved content (default: demo)
"""

import os
import sys

from {{PRODUCT_LOWER}}_base import {{PRODUCT_UPPER}}Client, require_config

# Additional configuration
PRESERVE_TAG = os.environ.get("DEMO_PRESERVE_TAG", "demo")


def cleanup_sandbox():
    """Clean up the demo sandbox."""
    print("{{PRODUCT}} Demo Sandbox Cleanup")
    print("=" * 40)

    # Validate and get configuration
    config = require_config()
    client = {{PRODUCT_UPPER}}Client(config)

    print(f"API URL: {config.api_url}")
    print(f"Preserving items with tag: {PRESERVE_TAG}")

    # TODO: Implement cleanup logic
    # 1. Get all items
    # 2. Filter out items with PRESERVE_TAG
    # 3. Delete remaining items

    print("\nCleanup complete!")


def main():
    """Main entry point."""
    try:
        cleanup_sandbox()
    except Exception as e:
        print(f"Error during cleanup: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
