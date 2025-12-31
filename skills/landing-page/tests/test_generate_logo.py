"""Tests for generate_logo.py module."""

import pytest
from pathlib import Path

# Import functions from generate_logo
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from generate_logo import (
    calculate_text_metrics,
    generate_logo,
    PALETTES,
)


class TestCalculateTextMetrics:
    """Tests for calculate_text_metrics function."""

    def test_short_name_metrics(self):
        """Test metrics for short name (4 chars or less)."""
        metrics = calculate_text_metrics("jira")
        assert metrics["font_size"] == 80
        assert "text_x" in metrics
        assert "cursor_x" in metrics

    def test_medium_name_metrics(self):
        """Test metrics for medium name (5-6 chars)."""
        metrics = calculate_text_metrics("splunk")
        assert metrics["font_size"] == 70

    def test_long_name_metrics(self):
        """Test metrics for longer name (7-8 chars)."""
        metrics = calculate_text_metrics("datadog8")
        assert metrics["font_size"] == 60

    def test_very_long_name_metrics(self):
        """Test metrics for very long name (9-10 chars)."""
        metrics = calculate_text_metrics("prometheus")
        assert metrics["font_size"] == 50

    def test_extra_long_name_metrics(self):
        """Test metrics for extra long name (11+ chars)."""
        metrics = calculate_text_metrics("elasticsearch")
        assert metrics["font_size"] == 42


class TestGenerateLogo:
    """Tests for generate_logo function."""

    def test_generates_valid_svg(self):
        """Test that output is valid SVG."""
        svg = generate_logo("test")
        assert svg.startswith('<?xml version="1.0"')
        assert "<svg" in svg
        assert "</svg>" in svg

    def test_includes_product_name(self):
        """Test that product name is in SVG."""
        svg = generate_logo("jira")
        assert "jira" in svg.lower()

    def test_includes_primary_color(self):
        """Test that primary color is included."""
        svg = generate_logo("test", primary_color="#FF0000")
        assert "#FF0000" in svg

    def test_includes_accent_color(self):
        """Test that accent color is included."""
        svg = generate_logo("test", accent_color="#00FF00")
        assert "#00FF00" in svg

    def test_includes_cursor_color(self):
        """Test that cursor color is included."""
        svg = generate_logo("test", cursor_color="#0000FF")
        assert "#0000FF" in svg

    def test_animated_includes_animation(self):
        """Test that animated logo includes animation."""
        svg = generate_logo("test", animated=True)
        assert "<animate" in svg
        assert "repeatCount" in svg

    def test_static_excludes_animation(self):
        """Test that static logo excludes animation."""
        svg = generate_logo("test", animated=False)
        assert "<animate" not in svg

    def test_includes_gradients(self):
        """Test that SVG includes gradient definitions."""
        svg = generate_logo("test")
        assert "linearGradient" in svg
        assert "bgGradient" in svg
        assert "promptGradient" in svg

    def test_includes_filters(self):
        """Test that SVG includes filter definitions."""
        svg = generate_logo("test")
        assert 'id="glow"' in svg
        assert 'id="shadow"' in svg

    def test_includes_chevron(self):
        """Test that SVG includes prompt chevron."""
        svg = generate_logo("test")
        assert "<path" in svg
        assert "stroke-linejoin" in svg

    def test_includes_decorative_circles(self):
        """Test that SVG includes decorative elements."""
        svg = generate_logo("test")
        assert svg.count("<circle") >= 3  # Background + decoration circles


class TestPalettes:
    """Tests for color palettes."""

    def test_all_palettes_have_required_colors(self):
        """Test that all palettes have required color keys."""
        for name, palette in PALETTES.items():
            assert "primary" in palette, f"{name} missing primary"
            assert "accent" in palette, f"{name} missing accent"
            assert "cursor" in palette, f"{name} missing cursor"

    def test_atlassian_palette(self):
        """Test Atlassian palette colors."""
        assert PALETTES["atlassian"]["primary"] == "#0052CC"

    def test_jira_palette(self):
        """Test Jira palette colors."""
        assert PALETTES["jira"]["primary"] == "#0052CC"

    def test_confluence_palette(self):
        """Test Confluence palette colors."""
        assert PALETTES["confluence"]["accent"] == "#36B37E"

    def test_splunk_palette(self):
        """Test Splunk palette colors."""
        assert PALETTES["splunk"]["primary"] == "#FF6900"

    def test_github_palette(self):
        """Test GitHub palette colors."""
        assert PALETTES["github"]["primary"] == "#238636"

    def test_gitlab_palette(self):
        """Test GitLab palette colors."""
        assert PALETTES["gitlab"]["primary"] == "#FC6D26"

    def test_datadog_palette(self):
        """Test Datadog palette colors."""
        assert PALETTES["datadog"]["primary"] == "#632CA6"

    def test_colors_are_valid_hex(self):
        """Test that all colors are valid hex format."""
        import re
        hex_pattern = r'^#[0-9A-Fa-f]{6}$'
        for name, palette in PALETTES.items():
            for key, color in palette.items():
                assert re.match(hex_pattern, color), f"{name}.{key} invalid: {color}"


class TestIntegration:
    """Integration tests for logo generation."""

    def test_generates_logo_with_palette(self):
        """Test generating logo using palette."""
        palette = PALETTES["jira"]
        svg = generate_logo(
            "jira",
            primary_color=palette["primary"],
            accent_color=palette["accent"],
            cursor_color=palette["cursor"],
        )
        assert "#0052CC" in svg  # Jira primary color
        assert "jira" in svg

    def test_logo_dimensions(self):
        """Test that logo has correct dimensions."""
        svg = generate_logo("test")
        assert 'viewBox="0 0 512 512"' in svg
        assert 'width="512"' in svg
        assert 'height="512"' in svg

    def test_logo_saves_to_file(self, temp_path):
        """Test saving logo to file."""
        output_path = temp_path / "logo.svg"
        svg = generate_logo("test")
        output_path.write_text(svg)

        assert output_path.exists()
        content = output_path.read_text()
        assert "<svg" in content
