"""
Shared pytest fixtures for simple-agent tests.
"""

import pytest
import os
from pathlib import Path
from typing import Dict


@pytest.fixture
def fixtures_dir():
    """Return path to test fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def skills_fixtures_dir(fixtures_dir):
    """Return path to skills fixtures directory."""
    return fixtures_dir / "skills"


@pytest.fixture
def valid_skill_path(skills_fixtures_dir):
    """Return path to valid skill fixture."""
    return skills_fixtures_dir / "valid-skill" / "SKILL.md"


@pytest.fixture
def minimal_skill_path(skills_fixtures_dir):
    """Return path to minimal skill fixture."""
    return skills_fixtures_dir / "minimal-skill" / "SKILL.md"


@pytest.fixture
def invalid_yaml_skill_path(skills_fixtures_dir):
    """Return path to invalid YAML skill fixture."""
    return skills_fixtures_dir / "invalid-yaml" / "SKILL.md"


@pytest.fixture
def missing_fields_skill_path(skills_fixtures_dir):
    """Return path to missing fields skill fixture."""
    return skills_fixtures_dir / "missing-fields" / "SKILL.md"


@pytest.fixture
def skill_with_resources_path(skills_fixtures_dir):
    """Return path to skill with resources fixture."""
    return skills_fixtures_dir / "skill-with-resources" / "SKILL.md"


# Path testing fixtures
@pytest.fixture
def temp_skills_dir(tmp_path):
    """Create a temporary skills directory with subdirectories."""
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()

    # Create some skill subdirectories
    (skills_dir / "skill-one").mkdir()
    (skills_dir / "skill-two").mkdir()

    # Create SKILL.md files in each
    (skills_dir / "skill-one" / "SKILL.md").write_text("---\nname: skill-one\ndescription: Test skill\n---\n", encoding='utf-8')
    (skills_dir / "skill-two" / "SKILL.md").write_text("---\nname: skill-two\ndescription: Test skill\n---\n", encoding='utf-8')

    return skills_dir


@pytest.fixture
def temp_global_dir(tmp_path):
    """Create a temporary global skills directory."""
    global_dir = tmp_path / "global" / ".simple-agent" / "skills"
    global_dir.mkdir(parents=True)

    # Create a global skill
    (global_dir / "global-skill").mkdir()
    (global_dir / "global-skill" / "SKILL.md").write_text("---\nname: global-skill\ndescription: Global skill\n---\n", encoding='utf-8')

    return global_dir


@pytest.fixture
def temp_project_dir(tmp_path):
    """Create a temporary project directory with local skills."""
    project_dir = tmp_path / "project"
    project_dir.mkdir()

    skills_dir = project_dir / "skills"
    skills_dir.mkdir()

    # Create a project-local skill
    (skills_dir / "local-skill").mkdir()
    (skills_dir / "local-skill" / "SKILL.md").write_text("---\nname: local-skill\ndescription: Local skill\n---\n", encoding='utf-8')

    return project_dir


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Factory fixture to mock environment variables."""
    def _mock_env(env_dict: Dict[str, str]):
        for key, value in env_dict.items():
            monkeypatch.setenv(key, value)
    return _mock_env


# SkillLoader testing fixtures
@pytest.fixture
def temp_skills_tree(tmp_path):
    """Create a multi-level directory structure with nested skills."""
    root = tmp_path / "skills_tree"
    root.mkdir()

    # Top level skill
    (root / "top-skill").mkdir()
    (root / "top-skill" / "SKILL.md").write_text(
        "---\nname: top-skill\ndescription: Top level skill\n---\n",
        encoding='utf-8'
    )

    # Nested skill (one level deep)
    (root / "category" / "nested-skill").mkdir(parents=True)
    (root / "category" / "nested-skill" / "SKILL.md").write_text(
        "---\nname: nested-skill\ndescription: Nested skill\n---\n",
        encoding='utf-8'
    )

    # Deeply nested skill (two levels deep)
    (root / "category" / "subcategory" / "deep-skill").mkdir(parents=True)
    (root / "category" / "subcategory" / "deep-skill" / "SKILL.md").write_text(
        "---\nname: deep-skill\ndescription: Deeply nested skill\n---\n",
        encoding='utf-8'
    )

    return root


@pytest.fixture
def temp_multiple_skill_dirs(tmp_path):
    """Create multiple separate skill directories."""
    dir1 = tmp_path / "dir1"
    dir2 = tmp_path / "dir2"
    dir1.mkdir()
    dir2.mkdir()

    # Skills in dir1
    (dir1 / "skill-a").mkdir()
    (dir1 / "skill-a" / "SKILL.md").write_text(
        "---\nname: skill-a\ndescription: Skill A\n---\n",
        encoding='utf-8'
    )

    (dir1 / "skill-b").mkdir()
    (dir1 / "skill-b" / "SKILL.md").write_text(
        "---\nname: skill-b\ndescription: Skill B\n---\n",
        encoding='utf-8'
    )

    # Skills in dir2
    (dir2 / "skill-c").mkdir()
    (dir2 / "skill-c" / "SKILL.md").write_text(
        "---\nname: skill-c\ndescription: Skill C\n---\n",
        encoding='utf-8'
    )

    return [dir1, dir2]


@pytest.fixture
def temp_mixed_content_dir(tmp_path):
    """Create a directory with skills and non-skill files."""
    root = tmp_path / "mixed"
    root.mkdir()

    # Valid skill
    (root / "valid-skill").mkdir()
    (root / "valid-skill" / "SKILL.md").write_text(
        "---\nname: valid-skill\ndescription: Valid skill\n---\n",
        encoding='utf-8'
    )

    # Regular markdown file (not a skill)
    (root / "README.md").write_text("# Not a skill", encoding='utf-8')

    # Regular directory without SKILL.md
    (root / "not-a-skill").mkdir()
    (root / "not-a-skill" / "some-file.txt").write_text("data", encoding='utf-8')

    # Python files
    (root / "script.py").write_text("print('hello')", encoding='utf-8')

    # Invalid skill (invalid YAML)
    (root / "invalid-skill").mkdir()
    (root / "invalid-skill" / "SKILL.md").write_text(
        "---\nname: [invalid yaml\n---\n",
        encoding='utf-8'
    )

    # Skill missing required fields
    (root / "incomplete-skill").mkdir()
    (root / "incomplete-skill" / "SKILL.md").write_text(
        "---\nname: incomplete-skill\n---\n",  # missing description
        encoding='utf-8'
    )

    return root


@pytest.fixture
def temp_duplicate_skills_dirs(tmp_path):
    """Create multiple directories with duplicate skill names."""
    dir1 = tmp_path / "priority1"
    dir2 = tmp_path / "priority2"
    dir1.mkdir()
    dir2.mkdir()

    # Same skill name in both directories (different descriptions)
    (dir1 / "duplicate-skill").mkdir()
    (dir1 / "duplicate-skill" / "SKILL.md").write_text(
        "---\nname: duplicate-skill\ndescription: First occurrence (priority 1)\nversion: 1.0.0\n---\n",
        encoding='utf-8'
    )

    (dir2 / "duplicate-skill").mkdir()
    (dir2 / "duplicate-skill" / "SKILL.md").write_text(
        "---\nname: duplicate-skill\ndescription: Second occurrence (priority 2)\nversion: 2.0.0\n---\n",
        encoding='utf-8'
    )

    # Unique skill in dir2
    (dir2 / "unique-skill").mkdir()
    (dir2 / "unique-skill" / "SKILL.md").write_text(
        "---\nname: unique-skill\ndescription: Unique to dir2\n---\n",
        encoding='utf-8'
    )

    return [dir1, dir2]


@pytest.fixture
def temp_empty_skills_dir(tmp_path):
    """Create an empty skills directory."""
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    return empty_dir
