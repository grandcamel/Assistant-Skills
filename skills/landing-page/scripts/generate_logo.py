#!/usr/bin/env python3
"""
Generate a logo SVG for an Assistant Skills project.

Uses the terminal prompt design pattern with customizable colors
and product name.
"""

import argparse
from pathlib import Path


def calculate_text_metrics(product_name: str) -> dict[str, int]:
    """Calculate font size and positions based on text length."""
    length = len(product_name)

    # Base metrics for 4-char name like "jira"
    if length <= 4:
        return {"font_size": 80, "text_x": 230, "cursor_x": 390}
    elif length <= 6:
        return {"font_size": 70, "text_x": 220, "cursor_x": 400}
    elif length <= 8:
        return {"font_size": 60, "text_x": 215, "cursor_x": 400}
    elif length <= 10:
        return {"font_size": 50, "text_x": 210, "cursor_x": 395}
    else:
        return {"font_size": 42, "text_x": 205, "cursor_x": 390}


def generate_logo(
    product_name: str,
    primary_color: str = "#0052CC",
    accent_color: str = "#4a00e0",
    cursor_color: str = "#00C7E6",
    bg_start: str = "#1a1a2e",
    bg_end: str = "#16213e",
    animated: bool = True,
) -> str:
    """Generate logo SVG content."""
    metrics = calculate_text_metrics(product_name.lower())

    animation = ""
    if animated:
        animation = """
    <!-- Blinking animation -->
    <animate
      attributeName="opacity"
      values="1;0;1"
      dur="1.2s"
      repeatCount="indefinite"
    />"""

    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">
  <defs>
    <linearGradient id="bgGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{bg_start};stop-opacity:1" />
      <stop offset="100%" style="stop-color:{bg_end};stop-opacity:1" />
    </linearGradient>
    <linearGradient id="promptGradient" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:{primary_color};stop-opacity:1" />
      <stop offset="100%" style="stop-color:{accent_color};stop-opacity:1" />
    </linearGradient>
    <linearGradient id="cursorGradient" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:{cursor_color};stop-opacity:1" />
      <stop offset="100%" style="stop-color:{primary_color};stop-opacity:1" />
    </linearGradient>
    <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="4" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="4" stdDeviation="8" flood-color="#000000" flood-opacity="0.3"/>
    </filter>
  </defs>

  <circle cx="256" cy="256" r="240" fill="url(#bgGradient)" filter="url(#shadow)"/>
  <circle cx="256" cy="256" r="240" fill="none" stroke="url(#promptGradient)" stroke-width="3" opacity="0.6"/>
  <circle cx="256" cy="256" r="200" fill="none" stroke="#ffffff" stroke-width="1" opacity="0.1"/>

  <path
    d="M 130 200 L 200 256 L 130 312"
    fill="none"
    stroke="url(#promptGradient)"
    stroke-width="28"
    stroke-linecap="round"
    stroke-linejoin="round"
  />

  <text
    x="{metrics['text_x']}"
    y="275"
    font-family="'SF Mono', 'Monaco', 'Consolas', 'Courier New', monospace"
    font-size="{metrics['font_size']}"
    font-weight="600"
    fill="#ffffff"
    letter-spacing="-2"
  >{product_name.lower()}</text>

  <rect
    x="{metrics['cursor_x']}"
    y="275"
    width="40"
    height="8"
    rx="2"
    fill="url(#cursorGradient)"
    filter="url(#glow)"
  >{animation}
  </rect>

  <g opacity="0.3">
    <circle cx="120" cy="380" r="4" fill="{cursor_color}"/>
    <circle cx="140" cy="380" r="4" fill="{accent_color}"/>
    <circle cx="160" cy="380" r="4" fill="{primary_color}"/>
  </g>
</svg>'''

    return svg


# Predefined color palettes
PALETTES = {
    "atlassian": {
        "primary": "#0052CC",
        "accent": "#4a00e0",
        "cursor": "#00C7E6",
    },
    "jira": {
        "primary": "#0052CC",
        "accent": "#4a00e0",
        "cursor": "#00C7E6",
    },
    "confluence": {
        "primary": "#0052CC",
        "accent": "#36B37E",
        "cursor": "#00C7E6",
    },
    "splunk": {
        "primary": "#FF6900",
        "accent": "#65A637",
        "cursor": "#00C7E6",
    },
    "github": {
        "primary": "#238636",
        "accent": "#1f6feb",
        "cursor": "#00C7E6",
    },
    "gitlab": {
        "primary": "#FC6D26",
        "accent": "#6E49CB",
        "cursor": "#00C7E6",
    },
    "datadog": {
        "primary": "#632CA6",
        "accent": "#FF6B6B",
        "cursor": "#00C7E6",
    },
}


def main():
    parser = argparse.ArgumentParser(
        description="Generate a logo SVG for an Assistant Skills project",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Generate Confluence logo with default Atlassian colors
    python generate_logo.py confluence --palette atlassian

    # Generate Splunk logo with Splunk colors
    python generate_logo.py splunk --palette splunk

    # Custom colors
    python generate_logo.py myproduct --primary "#FF6900" --accent "#65A637"

    # Static logo (no animation)
    python generate_logo.py jira --static

Available palettes: atlassian, jira, confluence, splunk, github, gitlab, datadog
        """,
    )
    parser.add_argument("product_name", help="Product name to display (e.g., jira, confluence)")
    parser.add_argument(
        "-o", "--output", help="Output file path (default: stdout)"
    )
    parser.add_argument(
        "--palette",
        choices=list(PALETTES.keys()),
        help="Use predefined color palette",
    )
    parser.add_argument("--primary", help="Primary color (hex, e.g., #0052CC)")
    parser.add_argument("--accent", help="Accent color (hex, e.g., #4a00e0)")
    parser.add_argument("--cursor", help="Cursor color (hex, e.g., #00C7E6)")
    parser.add_argument(
        "--static",
        action="store_true",
        help="Generate static logo without animation",
    )

    args = parser.parse_args()

    # Start with defaults
    colors = {
        "primary_color": "#0052CC",
        "accent_color": "#4a00e0",
        "cursor_color": "#00C7E6",
    }

    # Apply palette if specified
    if args.palette:
        palette = PALETTES[args.palette]
        colors["primary_color"] = palette["primary"]
        colors["accent_color"] = palette["accent"]
        colors["cursor_color"] = palette["cursor"]

    # Override with specific colors
    if args.primary:
        colors["primary_color"] = args.primary
    if args.accent:
        colors["accent_color"] = args.accent
    if args.cursor:
        colors["cursor_color"] = args.cursor

    svg = generate_logo(
        args.product_name,
        animated=not args.static,
        **colors,
    )

    if args.output:
        output_path = Path(args.output)
        output_path.write_text(svg)
        print(f"Logo saved to: {output_path}")
    else:
        print(svg)


if __name__ == "__main__":
    main()
