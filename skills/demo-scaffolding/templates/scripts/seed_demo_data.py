#!/usr/bin/env python3
"""
Seed Demo Data Script

Creates sample demo data for the {{PRODUCT}} Assistant Skills demo.

Usage:
    python seed_demo_data.py

Environment Variables:
    {{API_URL_VAR}}: {{PRODUCT}} API URL
    {{API_TOKEN_VAR}}: API token
"""

import sys

from {{PRODUCT_LOWER}}_base import {{PRODUCT_UPPER}}Client, require_config

# Demo content configuration - customize for your product
DEMO_ITEMS = [
    {
        "name": "Getting Started",
        "description": "Introduction to {{PRODUCT}} features",
        "tags": ["demo", "docs"]
    },
    {
        "name": "API Reference",
        "description": "Technical API documentation",
        "tags": ["demo", "api", "technical"]
    },
    {
        "name": "Best Practices",
        "description": "Recommended patterns and workflows",
        "tags": ["demo", "guide"]
    }
]


def create_demo_content(client: {{PRODUCT_UPPER}}Client):
    """Create all demo content."""
    print("\nCreating demo content...")

    for item in DEMO_ITEMS:
        print(f"  Creating: {item['name']}")
        # TODO: Implement API call to create item
        # response = client.post("/api/items", json=item)
        # if response.status_code == 200:
        #     print(f"    Created: {item['name']}")
        # else:
        #     print(f"    Failed: {response.status_code}")


def main():
    """Main entry point."""
    print("{{PRODUCT}} Demo Data Seeder")
    print("=" * 40)

    # Validate and get configuration
    config = require_config()
    client = {{PRODUCT_UPPER}}Client(config)

    print(f"API URL: {config.api_url}")

    # Create demo content
    create_demo_content(client)

    print("\nDemo data seeding complete!")


if __name__ == "__main__":
    main()
