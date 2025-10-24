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
