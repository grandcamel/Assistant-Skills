#!/usr/bin/env python3
"""
Demo Scaffolding Script

Creates production-ready demo platforms for Assistant Skills plugins.
Generates complete infrastructure including queue-manager, landing page,
observability stack, and security configurations.

Usage:
    python create_demo.py  # Interactive mode
    python create_demo.py --name github-demo --product GitHub ...
    python create_demo.py --dry-run  # Preview without creating files
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional


@dataclass
class DemoConfig:
    """Configuration for demo generation."""
    name: str  # kebab-case, e.g., "github-demo"
    product: str  # Display name, e.g., "GitHub"
    plugin: Optional[str] = None  # Plugin identifier
    plugin_source: str = "none"  # pypi, github, none
    api_url_var: Optional[str] = None  # e.g., GITHUB_API_URL
    api_token_var: Optional[str] = None  # e.g., GITHUB_TOKEN
    additional_credentials: list = field(default_factory=list)
    scenarios: list = field(default_factory=lambda: ["search", "admin"])
    output_dir: Optional[str] = None
    session_timeout: int = 60
    max_queue_size: int = 10
    enable_ci: bool = False
    enable_precommit: bool = False
    enable_mock_api: bool = True
    enable_skill_testing: bool = True
    enable_autoplay: bool = True

    def __post_init__(self):
        """Set derived values."""
        product_upper = self.product.upper().replace(" ", "_").replace("-", "_")
        if not self.api_url_var:
            self.api_url_var = f"{product_upper}_API_URL"
        if not self.api_token_var:
            self.api_token_var = f"{product_upper}_API_TOKEN"
        if not self.output_dir:
            self.output_dir = f"./{self.name}"

    @property
    def product_lower(self) -> str:
        return self.product.lower().replace(" ", "-")

    @property
    def product_upper(self) -> str:
        return self.product.upper().replace(" ", "_").replace("-", "_")

    @property
    def container_image(self) -> str:
        return f"{self.name}-container:latest"

    @property
    def network_name(self) -> str:
        return f"{self.name}-network"

    @property
    def has_plugin(self) -> bool:
        return self.plugin is not None and self.plugin_source != "none"


def validate_name(name: str) -> bool:
    """Validate demo name is kebab-case and reasonable length."""
    pattern = r'^[a-z][a-z0-9]*(-[a-z0-9]+)*$'
    return bool(re.match(pattern, name)) and 3 <= len(name) <= 50


def validate_scenarios(scenarios: list) -> bool:
    """Validate scenario names are alphanumeric."""
    pattern = r'^[a-z][a-z0-9_]*$'
    return all(re.match(pattern, s) for s in scenarios)


def get_interactive_config() -> DemoConfig:
    """Gather configuration interactively."""
    print("\n" + "=" * 60)
    print("  Demo Scaffolding - Interactive Setup")
    print("=" * 60 + "\n")

    # Demo name
    while True:
        name = input("Demo name (kebab-case, e.g., 'github-demo'): ").strip()
        if validate_name(name):
            break
        print("  Invalid name. Use lowercase letters, numbers, and hyphens.")

    # Product name
    product = input("Product name (e.g., 'GitHub'): ").strip()
    if not product:
        product = name.replace("-demo", "").replace("-", " ").title()

    # Plugin configuration
    print("\nPlugin configuration:")
    print("  1. PyPI package")
    print("  2. GitHub repository")
    print("  3. No plugin (CLI-only demo)")
    plugin_choice = input("Select [1-3, default: 3]: ").strip() or "3"

    plugin = None
    plugin_source = "none"
    if plugin_choice == "1":
        plugin = input("PyPI package name: ").strip()
        plugin_source = "pypi"
    elif plugin_choice == "2":
        plugin = input("GitHub repo (user/repo): ").strip()
        plugin_source = "github"

    # API configuration
    print("\nAPI configuration:")
    product_upper = product.upper().replace(" ", "_").replace("-", "_")
    default_url = f"{product_upper}_API_URL"
    default_token = f"{product_upper}_API_TOKEN"

    api_url_var = input(f"API URL env var [{default_url}]: ").strip() or default_url
    api_token_var = input(f"API token env var [{default_token}]: ").strip() or default_token

    additional = input("Additional credentials (comma-separated, or blank): ").strip()
    additional_credentials = [c.strip() for c in additional.split(",") if c.strip()]

    # Scenarios
    default_scenarios = "search,admin"
    scenarios_input = input(f"Scenarios (comma-separated) [{default_scenarios}]: ").strip()
    scenarios = [s.strip() for s in (scenarios_input or default_scenarios).split(",")]

    if not validate_scenarios(scenarios):
        print("  Warning: Some scenario names may be invalid. Using anyway.")

    # Output directory
    default_output = f"./{name}"
    output_dir = input(f"Output directory [{default_output}]: ").strip() or default_output

    # Features
    print("\nOptional features:")
    enable_ci = input("Generate GitHub Actions CI? [y/N]: ").strip().lower() == "y"
    enable_precommit = input("Generate pre-commit config? [y/N]: ").strip().lower() == "y"

    return DemoConfig(
        name=name,
        product=product,
        plugin=plugin,
        plugin_source=plugin_source,
        api_url_var=api_url_var,
        api_token_var=api_token_var,
        additional_credentials=additional_credentials,
        scenarios=scenarios,
        output_dir=output_dir,
        enable_ci=enable_ci,
        enable_precommit=enable_precommit,
    )


def generate_scenarios_config(config: DemoConfig) -> str:
    """Generate SCENARIO_NAMES configuration for config/index.js."""
    # Default icons for common scenarios
    icons = {
        "search": "🔍",
        "admin": "⚙️",
        "page": "📝",
        "space": "🏠",
        "hierarchy": "🌳",
        "template": "📋",
        "comment": "💬",
        "attachment": "📎",
        "label": "🏷️",
        "permission": "🔒",
        "bulk": "📦",
        "analytics": "📊",
        "issue": "🎫",
        "workflow": "🔄",
        "dashboard": "📈",
        "alert": "🔔",
    }

    lines = []
    for scenario in config.scenarios:
        icon = icons.get(scenario, "📋")
        title = scenario.replace("_", " ").title()
        lines.append(f"    '{scenario}': {{ file: '{scenario}.md', title: '{title}', icon: '{icon}' }},")

    return "\n".join(lines)


def generate_scenario_cards(config: DemoConfig) -> str:
    """Generate scenario cards HTML for landing page."""
    icons = {
        "search": "🔍", "admin": "⚙️", "page": "📝", "space": "🏠",
        "hierarchy": "🌳", "template": "📋", "comment": "💬",
        "attachment": "📎", "label": "🏷️", "permission": "🔒",
        "bulk": "📦", "analytics": "📊", "issue": "🎫",
    }

    cards = []
    for scenario in config.scenarios:
        icon = icons.get(scenario, "📋")
        title = scenario.replace("_", " ").title()
        cards.append(f'''            <div class="scenario-card">
                <div class="card-icon">{icon}</div>
                <h3>{title}</h3>
                <p>Explore {config.product} {title.lower()} operations</p>
                <span class="duration">~5 min</span>
            </div>''')

    return "\n".join(cards)


def generate_scenario_links(config: DemoConfig) -> str:
    """Generate scenario links HTML for terminal dropdown."""
    icons = {
        "search": "🔍", "admin": "⚙️", "page": "📝", "space": "🏠",
        "hierarchy": "🌳", "template": "📋", "comment": "💬",
    }

    links = []
    for scenario in config.scenarios[:5]:  # Limit to 5 in dropdown
        icon = icons.get(scenario, "📋")
        title = scenario.replace("_", " ").title()
        links.append(f'                        <a href="/scenarios/{scenario}" target="_blank">{icon} {title}</a>')

    return "\n".join(links)


def generate_sample_commands(config: DemoConfig) -> str:
    """Generate sample command examples for landing page."""
    commands = [
        f'            <div class="command">\n                <code>claude "Show me available {config.product} skills"</code>\n            </div>',
        f'            <div class="command">\n                <code>claude "Help me with {config.product} {config.scenarios[0] if config.scenarios else "search"}"</code>\n            </div>',
    ]
    return "\n".join(commands)


def render_template(template: str, config: DemoConfig) -> str:
    """Render a template string with config values."""
    # Build replacement dict
    replacements = {
        "{{DEMO_NAME}}": config.name,
        "{{DEMO_TITLE}}": f"{config.product} Live Demo",
        "{{PRODUCT}}": config.product,
        "{{PRODUCT_NAME}}": config.product,
        "{{PRODUCT_LOWER}}": config.product_lower,
        "{{PRODUCT_UPPER}}": config.product_upper,
        "{{PLUGIN}}": config.plugin or "",
        "{{PLUGIN_NAME}}": config.plugin or "",
        "{{PLUGIN_SOURCE}}": config.plugin_source,
        "{{API_URL_VAR}}": config.api_url_var,
        "{{API_TOKEN_VAR}}": config.api_token_var,
        "{{CONTAINER_IMAGE}}": config.container_image,
        "{{NETWORK_NAME}}": config.network_name,
        "{{SESSION_TIMEOUT}}": str(config.session_timeout),
        "{{MAX_QUEUE_SIZE}}": str(config.max_queue_size),
        "{{SCENARIOS_JSON}}": json.dumps(config.scenarios),
        "{{SCENARIOS_COMMA}}": ",".join(config.scenarios),
        "{{SCENARIO_COUNT}}": str(len(config.scenarios)),
        "{{SCENARIOS_CONFIG}}": generate_scenarios_config(config),
        "{{SCENARIO_CARDS}}": generate_scenario_cards(config),
        "{{SCENARIO_LINKS}}": generate_scenario_links(config),
        "{{SAMPLE_COMMANDS}}": generate_sample_commands(config),
        "{{GENERATED_AT}}": datetime.now().isoformat(),
        "{{YEAR}}": str(datetime.now().year),
    }

    result = template
    for key, value in replacements.items():
        result = result.replace(key, value)

    # Handle conditional blocks: {{#IF HAS_PLUGIN}}...{{/IF}}
    if config.has_plugin:
        result = re.sub(r'\{\{#IF HAS_PLUGIN\}\}(.*?)\{\{/IF\}\}', r'\1', result, flags=re.DOTALL)
        result = re.sub(r'\{\{#IF NO_PLUGIN\}\}.*?\{\{/IF\}\}', '', result, flags=re.DOTALL)
    else:
        result = re.sub(r'\{\{#IF HAS_PLUGIN\}\}.*?\{\{/IF\}\}', '', result, flags=re.DOTALL)
        result = re.sub(r'\{\{#IF NO_PLUGIN\}\}(.*?)\{\{/IF\}\}', r'\1', result, flags=re.DOTALL)

    if config.enable_ci:
        result = re.sub(r'\{\{#IF ENABLE_CI\}\}(.*?)\{\{/IF\}\}', r'\1', result, flags=re.DOTALL)
    else:
        result = re.sub(r'\{\{#IF ENABLE_CI\}\}.*?\{\{/IF\}\}', '', result, flags=re.DOTALL)

    return result


def get_template_dir() -> Path:
    """Get the templates directory path."""
    return Path(__file__).parent.parent / "templates"


def create_directory_structure(config: DemoConfig, dry_run: bool = False) -> list:
    """Create the directory structure for the demo."""
    base = Path(config.output_dir)
    directories = [
        base,
        base / "queue-manager",
        base / "queue-manager" / "config",
        base / "queue-manager" / "services",
        base / "queue-manager" / "routes",
        base / "queue-manager" / "handlers",
        base / "queue-manager" / "static",
        base / "queue-manager" / "templates",
        base / "demo-container",
        base / "demo-container" / "scenarios",
        base / "landing-page",
        base / "landing-page" / "assets",
        base / "nginx",
        base / "observability",
        base / "observability" / "dashboards",
        base / "scripts",
        base / "secrets",
        base / ".claude",
        base / ".claude" / "commands",
        base / ".claude" / "agents",
        base / "docs",
    ]

    if config.enable_ci:
        directories.append(base / ".github")
        directories.append(base / ".github" / "workflows")

    created = []
    for d in directories:
        if not dry_run:
            d.mkdir(parents=True, exist_ok=True)
        created.append(str(d))

    return created


def generate_file(path: Path, content: str, config: DemoConfig, dry_run: bool = False) -> bool:
    """Generate a file with rendered content."""
    rendered = render_template(content, config)
    if not dry_run:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rendered)
    return True


def generate_demo(config: DemoConfig, dry_run: bool = False) -> dict:
    """Generate the complete demo structure."""
    results = {
        "directories": [],
        "files": [],
        "errors": [],
    }

    template_dir = get_template_dir()
    base = Path(config.output_dir)

    # Create directory structure
    print("\nCreating directory structure...")
    results["directories"] = create_directory_structure(config, dry_run)
    print(f"  Created {len(results['directories'])} directories")

    # Generate files from templates
    print("\nGenerating files...")

    # Define files to generate (template_name -> output_path)
    files_to_generate = [
        # Root files
        ("docker-compose.yml", base / "docker-compose.yml"),
        ("docker-compose.dev.yml", base / "docker-compose.dev.yml"),
        ("Makefile", base / "Makefile"),
        ("CLAUDE.md", base / "CLAUDE.md"),
        ("README.md", base / "README.md"),
        ("gitignore", base / ".gitignore"),
        ("pyproject.toml", base / "pyproject.toml"),

        # Queue manager
        ("queue-manager/server.js", base / "queue-manager" / "server.js"),
        ("queue-manager/package.json", base / "queue-manager" / "package.json"),
        ("queue-manager/Dockerfile", base / "queue-manager" / "Dockerfile"),
        ("queue-manager/instrumentation.js", base / "queue-manager" / "instrumentation.js"),
        ("queue-manager/invite-cli.js", base / "queue-manager" / "invite-cli.js"),
        ("queue-manager/eslint.config.js", base / "queue-manager" / "eslint.config.js"),
        ("queue-manager/config/index.js", base / "queue-manager" / "config" / "index.js"),
        ("queue-manager/config/metrics.js", base / "queue-manager" / "config" / "metrics.js"),
        ("queue-manager/services/state.js", base / "queue-manager" / "services" / "state.js"),
        ("queue-manager/services/queue.js", base / "queue-manager" / "services" / "queue.js"),
        ("queue-manager/services/session.js", base / "queue-manager" / "services" / "session.js"),
        ("queue-manager/services/invite.js", base / "queue-manager" / "services" / "invite.js"),
        ("queue-manager/routes/health.js", base / "queue-manager" / "routes" / "health.js"),
        ("queue-manager/routes/session.js", base / "queue-manager" / "routes" / "session.js"),
        ("queue-manager/routes/scenarios.js", base / "queue-manager" / "routes" / "scenarios.js"),
        ("queue-manager/handlers/websocket.js", base / "queue-manager" / "handlers" / "websocket.js"),
        ("queue-manager/static/scenario.css", base / "queue-manager" / "static" / "scenario.css"),
        ("queue-manager/templates/scenario.html", base / "queue-manager" / "templates" / "scenario.html"),

        # Demo container
        ("demo-container/Dockerfile", base / "demo-container" / "Dockerfile"),
        ("demo-container/entrypoint.sh", base / "demo-container" / "entrypoint.sh"),
        ("demo-container/motd", base / "demo-container" / "motd"),
        ("demo-container/settings.json", base / "demo-container" / "settings.json"),

        # Landing page
        ("landing-page/index.html", base / "landing-page" / "index.html"),
        ("landing-page/queue-client.js", base / "landing-page" / "queue-client.js"),
        ("landing-page/styles.css", base / "landing-page" / "styles.css"),
        ("landing-page/unauthorized.html", base / "landing-page" / "unauthorized.html"),

        # Nginx
        ("nginx/nginx.conf", base / "nginx" / "nginx.conf"),
        ("nginx/demo.conf", base / "nginx" / "demo.conf"),
        ("nginx/demo.dev.conf", base / "nginx" / "demo.dev.conf"),
        ("nginx/locations.include", base / "nginx" / "locations.include"),

        # Observability
        ("observability/grafana-dashboards.yaml", base / "observability" / "grafana-dashboards.yaml"),
        ("observability/grafana-datasources.yaml", base / "observability" / "grafana-datasources.yaml"),
        ("observability/loki-config.yaml", base / "observability" / "loki-config.yaml"),
        ("observability/tempo-config.yaml", base / "observability" / "tempo-config.yaml"),
        ("observability/prometheus.yaml", base / "observability" / "prometheus.yaml"),
        ("observability/promtail-config.yaml", base / "observability" / "promtail-config.yaml"),
        ("observability/otelcol-config.yaml", base / "observability" / "otelcol-config.yaml"),
        ("observability/dashboards/demo-home.json", base / "observability" / "dashboards" / "demo-home.json"),

        # Scripts
        ("scripts/deploy.sh", base / "scripts" / "deploy.sh"),
        ("scripts/healthcheck.sh", base / "scripts" / "healthcheck.sh"),
        ("scripts/api_base.py", base / "scripts" / f"{config.product_lower}_base.py"),
        ("scripts/seed_demo_data.py", base / "scripts" / "seed_demo_data.py"),
        ("scripts/cleanup_demo_sandbox.py", base / "scripts" / "cleanup_demo_sandbox.py"),

        # Secrets
        ("secrets/example.env", base / "secrets" / "example.env"),

        # Claude commands
        ("claude/commands/start-local.md", base / ".claude" / "commands" / "start-local.md"),
        ("claude/commands/stop-local.md", base / ".claude" / "commands" / "stop-local.md"),
        ("claude/commands/status-local.md", base / ".claude" / "commands" / "status-local.md"),
        ("claude/commands/logs.md", base / ".claude" / "commands" / "logs.md"),
        ("claude/commands/otel-logs.md", base / ".claude" / "commands" / "otel-logs.md"),
        ("claude/commands/invite-local.md", base / ".claude" / "commands" / "invite-local.md"),
        ("claude/commands/reset-sandbox.md", base / ".claude" / "commands" / "reset-sandbox.md"),
    ]

    # Add plugin-specific files
    if config.has_plugin:
        files_to_generate.extend([
            ("demo-container/skill-test.py", base / "demo-container" / "skill-test.py"),
            ("demo-container/autoplay.sh", base / "demo-container" / "autoplay.sh"),
            ("claude/commands/test-skill-dev.md", base / ".claude" / "commands" / "test-skill-dev.md"),
            ("claude/commands/refine-skill.md", base / ".claude" / "commands" / "refine-skill.md"),
            ("claude/agents/skill-fix.md", base / ".claude" / "agents" / "skill-fix.md"),
        ])

    # Add CI files if enabled
    if config.enable_ci:
        files_to_generate.append(
            ("github/workflows/test.yml", base / ".github" / "workflows" / "test.yml")
        )

    # Add pre-commit config if enabled
    if config.enable_precommit:
        files_to_generate.append(
            ("pre-commit-config.yaml", base / ".pre-commit-config.yaml")
        )

    # Process each file
    for template_name, output_path in files_to_generate:
        template_path = template_dir / template_name
        if template_path.exists():
            try:
                content = template_path.read_text()
                generate_file(output_path, content, config, dry_run)
                results["files"].append(str(output_path))
            except Exception as e:
                results["errors"].append(f"Error generating {output_path}: {e}")
        else:
            # Template doesn't exist yet, create placeholder
            results["errors"].append(f"Template not found: {template_name}")

    # Generate scenario files (special handling for SCENARIO_NAME placeholder)
    for scenario in config.scenarios:
        scenario_title = scenario.replace("_", " ").title()
        scenario_replacements = {
            "{{SCENARIO_NAME}}": scenario_title,
            "{{SCENARIO_KEY}}": scenario,
        }

        for template_name, output_name in [
            ("demo-container/scenarios/scenario.prompts", f"{scenario}.prompts"),
            ("demo-container/scenarios/scenario.md", f"{scenario}.md"),
        ]:
            template_path = template_dir / template_name
            output_path = base / "demo-container" / "scenarios" / output_name
            if template_path.exists():
                try:
                    content = template_path.read_text()
                    # First apply scenario-specific replacements
                    for key, value in scenario_replacements.items():
                        content = content.replace(key, value)
                    # Then apply standard config replacements
                    generate_file(output_path, content, config, dry_run)
                    results["files"].append(str(output_path))
                except Exception as e:
                    results["errors"].append(f"Error generating {output_path}: {e}")
            else:
                results["errors"].append(f"Template not found: {template_name}")

    print(f"  Generated {len(results['files'])} files")
    if results["errors"]:
        print(f"  {len(results['errors'])} errors (templates may need to be created)")

    # Save config for regeneration
    config_path = base / "demo.config.json"
    if not dry_run:
        config_dict = {
            "generatedBy": "demo-scaffolding",
            "version": "1.0.0",
            "generatedAt": datetime.now().isoformat(),
            "config": {
                "name": config.name,
                "product": config.product,
                "plugin": config.plugin,
                "pluginSource": config.plugin_source,
                "apiUrlVar": config.api_url_var,
                "apiTokenVar": config.api_token_var,
                "scenarios": config.scenarios,
                "sessionTimeout": config.session_timeout,
                "maxQueueSize": config.max_queue_size,
            }
        }
        config_path.write_text(json.dumps(config_dict, indent=2))
    results["files"].append(str(config_path))

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Create production-ready demo platforms for Assistant Skills plugins.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                    # Interactive mode
  %(prog)s --name github-demo --product GitHub
  %(prog)s --dry-run                          # Preview without creating files

For more information, see the SKILL.md documentation.
        """
    )

    parser.add_argument("--name", help="Demo name (kebab-case)")
    parser.add_argument("--product", help="Product/brand name")
    parser.add_argument("--plugin", help="Plugin identifier")
    parser.add_argument("--plugin-source", choices=["pypi", "github", "none"], default="none")
    parser.add_argument("--api-url-var", help="API URL environment variable name")
    parser.add_argument("--api-token-var", help="API token environment variable name")
    parser.add_argument("--scenarios", help="Comma-separated scenario names")
    parser.add_argument("--output", dest="output_dir", help="Output directory")
    parser.add_argument("--session-timeout", type=int, default=60)
    parser.add_argument("--max-queue", type=int, default=10)
    parser.add_argument("--enable-ci", action="store_true", help="Generate GitHub Actions workflow")
    parser.add_argument("--enable-precommit", action="store_true", help="Generate pre-commit config")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be created")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")

    args = parser.parse_args()

    # Interactive mode if no name provided
    if not args.name:
        config = get_interactive_config()
    else:
        if not validate_name(args.name):
            print(f"Error: Invalid demo name '{args.name}'")
            print("  Name must be kebab-case (lowercase letters, numbers, hyphens)")
            sys.exit(1)

        scenarios = args.scenarios.split(",") if args.scenarios else ["search", "admin"]

        config = DemoConfig(
            name=args.name,
            product=args.product or args.name.replace("-demo", "").replace("-", " ").title(),
            plugin=args.plugin,
            plugin_source=args.plugin_source,
            api_url_var=args.api_url_var,
            api_token_var=args.api_token_var,
            scenarios=scenarios,
            output_dir=args.output_dir,
            session_timeout=args.session_timeout,
            max_queue_size=args.max_queue,
            enable_ci=args.enable_ci,
            enable_precommit=args.enable_precommit,
        )

    # Show configuration summary
    if not args.json:
        print("\n" + "=" * 60)
        print("  Configuration Summary")
        print("=" * 60)
        print(f"  Name:           {config.name}")
        print(f"  Product:        {config.product}")
        print(f"  Plugin:         {config.plugin or 'None'}")
        print(f"  Plugin Source:  {config.plugin_source}")
        print(f"  API URL Var:    {config.api_url_var}")
        print(f"  API Token Var:  {config.api_token_var}")
        print(f"  Scenarios:      {', '.join(config.scenarios)}")
        print(f"  Output:         {config.output_dir}")
        print(f"  Session Timeout: {config.session_timeout} minutes")
        print(f"  Max Queue:      {config.max_queue_size}")
        print(f"  Enable CI:      {config.enable_ci}")
        print(f"  Pre-commit:     {config.enable_precommit}")
        print("=" * 60)

        if args.dry_run:
            print("\n  DRY RUN - No files will be created\n")

    # Generate demo
    results = generate_demo(config, dry_run=args.dry_run)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print("\n" + "=" * 60)
        if args.dry_run:
            print("  Dry Run Complete")
        else:
            print("  Generation Complete!")
        print("=" * 60)
        print(f"\n  Directories: {len(results['directories'])}")
        print(f"  Files:       {len(results['files'])}")

        if results["errors"]:
            print(f"\n  Warnings ({len(results['errors'])}):")
            for err in results["errors"][:5]:
                print(f"    - {err}")
            if len(results["errors"]) > 5:
                print(f"    ... and {len(results['errors']) - 5} more")

        if not args.dry_run:
            print(f"\n  Your demo is ready at: {config.output_dir}/")
            print("\n  Next steps:")
            print(f"    cd {config.output_dir}")
            print("    cp secrets/example.env secrets/.env")
            print("    # Edit secrets/.env with your credentials")
            print("    make dev")
            print("\n  Then visit: http://localhost:8080")


if __name__ == "__main__":
    main()
