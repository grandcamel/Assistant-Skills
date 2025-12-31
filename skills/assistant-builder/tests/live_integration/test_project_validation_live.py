"""Live integration tests for project validation against real projects."""

import os
import sys
import pytest
from pathlib import Path


@pytest.mark.live
@pytest.mark.integration
class TestProjectValidationLive:
    """Live tests that validate against real Assistant Skills projects."""

    def test_validates_self(self, project_root, live_test_enabled):
        """Test that this project validates successfully."""
        if not live_test_enabled:
            pytest.skip("Live tests disabled (set LIVE_TEST_ENABLED=true)")
        
        # Check plugin.json exists
        plugin_json = project_root / ".claude-plugin" / "plugin.json"
        assert plugin_json.exists(), f"plugin.json not found at {plugin_json}"
        
        # Check skills directory exists
        skills_dir = project_root / "skills"
        assert skills_dir.exists(), f"skills/ directory not found at {skills_dir}"
        
        # Check each skill has SKILL.md
        for skill_dir in skills_dir.iterdir():
            if skill_dir.is_dir() and skill_dir.name != "shared":
                skill_md = skill_dir / "SKILL.md"
                assert skill_md.exists(), f"{skill_dir.name} missing SKILL.md"

    def test_validates_reference_projects(self, reference_projects, live_test_enabled):
        """Test validation against reference projects (Jira, Confluence, Splunk)."""
        if not live_test_enabled:
            pytest.skip("Live tests disabled (set LIVE_TEST_ENABLED=true)")

        if not reference_projects:
            pytest.skip("No reference projects found")

        for name, path in reference_projects.items():
            plugin_json = path / ".claude-plugin" / "plugin.json"
            marketplace_json = path / ".claude-plugin" / "marketplace.json"
            has_plugin_config = plugin_json.exists() or marketplace_json.exists()
            assert has_plugin_config, f"{name} missing plugin.json or marketplace.json"

    def test_skill_count_in_reference_projects(self, reference_projects, live_test_enabled):
        """Verify reference projects have expected skill counts."""
        if not live_test_enabled:
            pytest.skip("Live tests disabled (set LIVE_TEST_ENABLED=true)")
        
        if not reference_projects:
            pytest.skip("No reference projects found")
        
        expected_min_skills = {
            "jira": 10,
            "confluence": 10,
            "splunk": 10,
        }
        
        for name, path in reference_projects.items():
            skills_dir = path / "skills"
            if skills_dir.exists():
                skills = [d for d in skills_dir.iterdir() 
                         if d.is_dir() and (d / "SKILL.md").exists()]
                min_expected = expected_min_skills.get(name, 1)
                assert len(skills) >= min_expected, \
                    f"{name} has {len(skills)} skills, expected >= {min_expected}"


@pytest.mark.live
@pytest.mark.integration
class TestTemplateValidationLive:
    """Live tests for template validation."""

    def test_all_templates_exist(self, project_root, live_test_enabled):
        """Verify all expected template directories exist."""
        if not live_test_enabled:
            pytest.skip("Live tests disabled (set LIVE_TEST_ENABLED=true)")
        
        expected_templates = [
            "00-project-lifecycle",
            "01-project-scaffolding", 
            "02-shared-library",
            "03-skill-templates",
            "04-testing",
            "05-documentation",
            "06-git-and-ci",
        ]
        
        # Check in assistant-builder templates
        templates_dir = project_root / "skills" / "assistant-builder" / "templates"
        
        if not templates_dir.exists():
            pytest.skip(f"Templates directory not found: {templates_dir}")
        
        for template in expected_templates:
            template_path = templates_dir / template
            assert template_path.exists(), f"Template directory missing: {template}"
            
            # Each should have at least one .md file
            md_files = list(template_path.glob("*.md"))
            assert len(md_files) > 0, f"No .md files in {template}"

    def test_shared_library_package(self, project_root, live_test_enabled):
        """Verify assistant-skills-lib package is importable."""
        if not live_test_enabled:
            pytest.skip("Live tests disabled (set LIVE_TEST_ENABLED=true)")

        # Import from the published package
        import assistant_skills_lib
        from assistant_skills_lib import (
            formatters, validators, cache, error_handler,
            template_engine, project_detector
        )

        # Verify key functions/classes exist
        assert hasattr(assistant_skills_lib, 'format_table'), "package missing format_table"
        assert hasattr(assistant_skills_lib, 'validate_url'), "package missing validate_url"
        assert hasattr(assistant_skills_lib, 'Cache'), "package missing Cache"
        assert hasattr(assistant_skills_lib, 'handle_errors'), "package missing handle_errors"
        assert hasattr(assistant_skills_lib, 'load_template'), "package missing load_template"
        assert hasattr(assistant_skills_lib, 'detect_project'), "package missing detect_project"

        # Verify version exists
        assert hasattr(assistant_skills_lib, '__version__'), "package missing __version__"


@pytest.mark.live
@pytest.mark.integration  
class TestPluginStructureLive:
    """Live tests for plugin structure validation."""

    def test_plugin_json_valid(self, project_root, live_test_enabled):
        """Verify plugin.json is valid JSON with required fields."""
        if not live_test_enabled:
            pytest.skip("Live tests disabled (set LIVE_TEST_ENABLED=true)")
        
        import json
        
        plugin_json = project_root / ".claude-plugin" / "plugin.json"
        assert plugin_json.exists(), f"plugin.json not found at {plugin_json}"
        
        with open(plugin_json) as f:
            data = json.load(f)
        
        assert "name" in data, "plugin.json missing 'name'"
        assert "version" in data, "plugin.json missing 'version'"
        assert "description" in data, "plugin.json missing 'description'"

    def test_skills_have_valid_structure(self, project_root, live_test_enabled):
        """Verify each skill has valid structure."""
        if not live_test_enabled:
            pytest.skip("Live tests disabled (set LIVE_TEST_ENABLED=true)")
        
        skills_dir = project_root / "skills"
        
        for skill_dir in skills_dir.iterdir():
            if not skill_dir.is_dir():
                continue
            if skill_dir.name == "shared":
                continue
                
            skill_md = skill_dir / "SKILL.md"
            assert skill_md.exists(), f"{skill_dir.name} missing SKILL.md"
            
            content = skill_md.read_text()
            assert content.startswith("---"), f"{skill_dir.name} SKILL.md missing frontmatter"
            assert "name:" in content, f"{skill_dir.name} SKILL.md missing name field"
            assert "description:" in content, f"{skill_dir.name} SKILL.md missing description field"

    def test_dual_directory_sync(self, project_root, live_test_enabled):
        """Verify skills/ and .claude/skills/ are in sync."""
        if not live_test_enabled:
            pytest.skip("Live tests disabled (set LIVE_TEST_ENABLED=true)")
        
        skills_dir = project_root / "skills"
        claude_skills_dir = project_root / ".claude" / "skills"
        
        if not claude_skills_dir.exists():
            pytest.skip(".claude/skills/ not found")
        
        # Get skill names from both directories
        skills_names = {d.name for d in skills_dir.iterdir() if d.is_dir()}
        claude_skills_names = {d.name for d in claude_skills_dir.iterdir() if d.is_dir()}
        
        assert skills_names == claude_skills_names, \
            f"Directories not in sync. Only in skills/: {skills_names - claude_skills_names}, " \
            f"Only in .claude/skills/: {claude_skills_names - skills_names}"
