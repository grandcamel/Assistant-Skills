"""
Tests for add_skill.py
"""

import pytest
import sys
from pathlib import Path

# Add scripts to path for importing script modules
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))


class TestAddSkill:
    """Tests for add_skill functionality."""

    def test_generate_skill_md(self):
        """Test SKILL.md generation for a new skill (CLI-reference style)."""
        from add_skill import generate_skill_md

        content = generate_skill_md(
            topic="github",
            skill_name="issues",
            description="Issue management",
            operations=["list", "get", "create"],
            cli_tool="gh",
            project_name="GitHub-Assistant-Skills"
        )

        assert "github-issues" in content
        assert "Issue management" in content
        # CLI-reference style - references commands, not scripts
        assert "gh issues list" in content or "gh issue list" in content
        assert "Risk" in content  # Has risk levels

    def test_generate_skill_md_with_risk_levels(self):
        """Test that SKILL.md includes proper risk levels."""
        from add_skill import generate_skill_md

        content = generate_skill_md(
            topic="test",
            skill_name="resource",
            description="Resource operations",
            operations=["list", "get", "create", "update", "delete"],
            cli_tool="test-cli"
        )

        # Check risk level indicators
        assert "⚠️" in content  # Caution for create/update
        assert "⚠️⚠️" in content  # Warning for delete
        assert "Risk Legend" in content

    def test_generate_best_practices_md(self):
        """Test best practices documentation generation."""
        from add_skill import generate_best_practices_md

        content = generate_best_practices_md(
            topic="github",
            skill_name="issues",
            cli_tool="gh"
        )

        assert "Best Practices" in content
        assert "Safety Checklist" in content
        assert "gh" in content

    def test_operation_presets(self):
        """Test that operation presets are defined correctly."""
        from add_skill import OPERATION_PRESETS

        assert OPERATION_PRESETS['crud'] == ['list', 'get', 'create', 'update', 'delete']
        assert OPERATION_PRESETS['readonly'] == ['list', 'get', 'search']
        assert 'export' in OPERATION_PRESETS['all']

    def test_add_skill_dry_run(self, sample_project_new):
        """Test add_skill in dry-run mode."""
        from add_skill import add_skill

        result = add_skill(
            project_dir=sample_project_new,
            skill_name="newskill",
            description="New skill",
            operations=["list", "get"],
            dry_run=True
        )

        # Should return files but not create them
        assert len(result['files']) > 0
        skill_dir = Path(sample_project_new) / "skills" / "test-newskill"
        assert not skill_dir.exists()

    def test_add_skill_creates_structure(self, sample_project_new):
        """Test that add_skill creates correct structure (new pattern)."""
        from add_skill import add_skill

        result = add_skill(
            project_dir=sample_project_new,
            skill_name="items",
            description="Item operations",
            operations=["list", "get", "create"],
            dry_run=False
        )

        skill_dir = Path(result['skill_dir'])

        # Check directories (new pattern - no scripts)
        assert skill_dir.exists()
        assert (skill_dir / "docs").exists()

        # Check files (new pattern)
        assert (skill_dir / "SKILL.md").exists()
        assert (skill_dir / "docs" / "BEST_PRACTICES.md").exists()

        # No scripts directory in new pattern
        assert not (skill_dir / "scripts").exists()

    def test_add_skill_detects_project_type(self, sample_project_new):
        """Test that add_skill correctly detects project type."""
        from add_skill import detect_project_type

        result = detect_project_type(Path(sample_project_new))

        assert result['topic'] == 'test'
        # CLI tool defaults to topic for cli-wrapper
        assert result['cli_tool'] is not None


class TestProjectDetection:
    """Tests for project detection in add_skill."""

    def test_detects_project(self, sample_project):
        """Test that existing project (old structure) is detected."""
        from assistant_skills_lib import detect_project

        project = detect_project(sample_project)

        assert project is not None
        assert project['name'] == "Test-Skills"
        assert project['topic_prefix'] == "test"
        assert project['has_settings'] is True

    def test_detects_skills(self, sample_project):
        """Test that existing skills are detected."""
        from assistant_skills_lib import list_skills

        skills = list_skills(sample_project)

        assert len(skills) == 1
        assert skills[0]['name'] == "test-sample"
        assert skills[0]['has_skill_md'] is True

    def test_detects_new_structure(self, sample_project_new):
        """Test detection of new structure (.claude-plugin/)."""
        from add_skill import detect_project_type

        result = detect_project_type(Path(sample_project_new))

        assert result['topic'] == 'test'
        # Should detect cli-wrapper type (no library dir)
        assert result['type'] == 'cli-wrapper'
