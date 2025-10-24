"""
Tests for skill validation module.

Tests the lowest-level component: SkillValidator
- YAML frontmatter parsing
- Field validation (name, description)
- Error handling for invalid skills
"""

import pytest
from pathlib import Path
from simple_agent.skills.validation import SkillValidator, SkillMetadata, SkillValidationError


class TestSkillMetadata:
    """Test SkillMetadata dataclass."""

    def test_skill_metadata_creation(self):
        """Test creating SkillMetadata with all fields."""
        metadata = SkillMetadata(
            name="test-skill",
            description="Test description",
            version="1.0.0",
            author="Test Author",
            allowed_tools=["Read", "Write"],
            skill_path=Path("./test-skill/SKILL.md")
        )

        assert metadata.name == "test-skill"
        assert metadata.description == "Test description"
        assert metadata.version == "1.0.0"
        assert metadata.author == "Test Author"
        assert metadata.allowed_tools == ["Read", "Write"]
        assert metadata.skill_path == Path("./test-skill/SKILL.md")

    def test_skill_metadata_minimal(self):
        """Test creating SkillMetadata with only required fields."""
        metadata = SkillMetadata(
            name="test-skill",
            description="Test description",
            skill_path=Path("./test-skill/SKILL.md")
        )

        assert metadata.name == "test-skill"
        assert metadata.description == "Test description"
        assert metadata.version is None
        assert metadata.author is None
        assert metadata.allowed_tools is None


class TestSkillValidator:
    """Test SkillValidator class."""

    def test_parse_valid_skill(self, valid_skill_path):
        """Test parsing a valid skill with all fields."""
        validator = SkillValidator()
        metadata = validator.parse(valid_skill_path)

        assert metadata.name == "valid-skill"
        assert metadata.description == "A valid skill for testing with all optional fields included"
        assert metadata.version == "1.0.0"
        assert metadata.author == "Test Author"
        assert metadata.allowed_tools == ["Read", "Write"]
        assert metadata.skill_path == valid_skill_path

    def test_parse_minimal_skill(self, minimal_skill_path):
        """Test parsing a minimal valid skill."""
        validator = SkillValidator()
        metadata = validator.parse(minimal_skill_path)

        assert metadata.name == "minimal-skill"
        assert metadata.description == "Minimal valid skill with only required fields"
        assert metadata.version is None
        assert metadata.author is None
        assert metadata.allowed_tools is None

    def test_parse_invalid_yaml(self, invalid_yaml_skill_path):
        """Test parsing skill with invalid YAML frontmatter."""
        validator = SkillValidator()

        with pytest.raises(SkillValidationError, match="Invalid YAML"):
            validator.parse(invalid_yaml_skill_path)

    def test_parse_missing_required_field(self, missing_fields_skill_path):
        """Test parsing skill missing required description field."""
        validator = SkillValidator()

        with pytest.raises(SkillValidationError, match="Missing required field"):
            validator.parse(missing_fields_skill_path)

    def test_parse_nonexistent_file(self):
        """Test parsing nonexistent file."""
        validator = SkillValidator()
        nonexistent_path = Path("./nonexistent/SKILL.md")

        with pytest.raises(FileNotFoundError):
            validator.parse(nonexistent_path)

    def test_validate_name_format(self):
        """Test name validation - lowercase, hyphens, max 64 chars."""
        validator = SkillValidator()

        # Valid names
        assert validator.validate_name("valid-skill") is True
        assert validator.validate_name("skill-123") is True
        assert validator.validate_name("a") is True
        assert validator.validate_name("skill-with-many-hyphens") is True

        # Invalid names
        with pytest.raises(SkillValidationError, match="uppercase"):
            validator.validate_name("Invalid-Skill")

        with pytest.raises(SkillValidationError, match="special characters"):
            validator.validate_name("skill_with_underscores")

        with pytest.raises(SkillValidationError, match="special characters"):
            validator.validate_name("skill with spaces")

        with pytest.raises(SkillValidationError, match="64 characters"):
            validator.validate_name("a" * 65)

        with pytest.raises(SkillValidationError, match="empty"):
            validator.validate_name("")

    def test_validate_description_length(self):
        """Test description validation - max 1024 chars."""
        validator = SkillValidator()

        # Valid descriptions
        assert validator.validate_description("Short description") is True
        assert validator.validate_description("a" * 1024) is True

        # Invalid descriptions
        with pytest.raises(SkillValidationError, match="1024 characters"):
            validator.validate_description("a" * 1025)

        with pytest.raises(SkillValidationError, match="empty"):
            validator.validate_description("")

        with pytest.raises(SkillValidationError, match="empty"):
            validator.validate_description("   ")

    def test_extract_frontmatter(self):
        """Test YAML frontmatter extraction from markdown."""
        validator = SkillValidator()

        content = """---
name: test
description: Test skill
---

# Content here
"""

        frontmatter, body = validator.extract_frontmatter(content)

        assert frontmatter == "name: test\ndescription: Test skill\n"
        assert "# Content here" in body

    def test_extract_frontmatter_no_delimiter(self):
        """Test frontmatter extraction when no delimiter present."""
        validator = SkillValidator()

        content = "# Just content, no frontmatter"

        with pytest.raises(SkillValidationError, match="No YAML frontmatter"):
            validator.extract_frontmatter(content)

    def test_extract_frontmatter_incomplete_delimiter(self):
        """Test frontmatter extraction with incomplete delimiter."""
        validator = SkillValidator()

        content = """---
name: test
description: Test
# Missing closing ---
"""

        with pytest.raises(SkillValidationError, match="No closing"):
            validator.extract_frontmatter(content)
