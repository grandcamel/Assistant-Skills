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
        """Test SKILL.md generation for a new skill."""
        from add_skill import generate_skill_md

        content = generate_skill_md(
            topic="github",
            skill_name="issues",
            description="Issue management",
            scripts=["list", "get", "create"]
        )

        assert "github-issues" in content
        assert "Issue management" in content
        assert "list_issues.py" in content
        assert "get_issues.py" in content
        assert "create_issues.py" in content

    def test_generate_script_template(self):
        """Test script template generation."""
        from add_skill import generate_script_template

        content = generate_script_template(
            topic="github",
            skill_name="issues",
            script_name="list"
        )

        assert "#!/usr/bin/env python3" in content
        assert "argparse" in content
        assert "--profile" in content
        assert "--output" in content

    def test_generate_test_template(self):
        """Test test file template generation."""
        from add_skill import generate_test_template

        content = generate_test_template(
            topic="github",
            skill_name="issues",
            script_name="list"
        )

        assert "import pytest" in content
        assert "class TestListIssues" in content
        assert "def test_list_returns_results" in content

    def test_generate_conftest(self):
        """Test conftest.py generation."""
        from add_skill import generate_conftest

        content = generate_conftest(
            topic="github",
            skill_name="issues"
        )

        assert "@pytest.fixture" in content
        assert "mock_client" in content
        assert "sample_issues" in content

    def test_add_skill_dry_run(self, sample_project):
        """Test add_skill in dry-run mode."""
        from add_skill import add_skill

        result = add_skill(
            project_dir=sample_project,
            skill_name="newskill",
            description="New skill",
            scripts=["list", "get"],
            dry_run=True
        )

        # Should return files but not create them
        assert len(result['files']) > 0
        skill_dir = Path(sample_project) / ".claude" / "skills" / "test-newskill"
        assert not skill_dir.exists()

    def test_add_skill_creates_structure(self, sample_project):
        """Test that add_skill creates correct structure."""
        from add_skill import add_skill

        result = add_skill(
            project_dir=sample_project,
            skill_name="items",
            description="Item operations",
            scripts=["list", "get", "create"],
            dry_run=False
        )

        skill_dir = Path(result['skill_dir'])

        # Check directories
        assert skill_dir.exists()
        assert (skill_dir / "scripts").exists()
        assert (skill_dir / "tests").exists()

        # Check files
        assert (skill_dir / "SKILL.md").exists()
        assert (skill_dir / "scripts" / "list_items.py").exists()
        assert (skill_dir / "scripts" / "get_items.py").exists()
        assert (skill_dir / "tests" / "test_list_items.py").exists()

    def test_script_presets(self):
        """Test that script presets expand correctly."""
        from add_skill import SCRIPT_PRESETS

        assert SCRIPT_PRESETS['crud'] == ['list', 'get', 'create', 'update', 'delete']
        assert SCRIPT_PRESETS['list-get'] == ['list', 'get']
        assert 'search' in SCRIPT_PRESETS['all']


class TestProjectDetection:
    """Tests for project detection in add_skill."""

    def test_detects_project(self, sample_project):
        """Test that existing project is detected."""
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
