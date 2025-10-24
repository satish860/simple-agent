"""
Shared pytest fixtures for simple-agent tests.
"""

import pytest
from pathlib import Path


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
