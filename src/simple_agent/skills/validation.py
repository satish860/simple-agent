"""
Skill validation module for parsing and validating SKILL.md files.

This is the lowest-level component with no dependencies on other skill modules.
"""

import re
import yaml
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, List, Tuple


class SkillValidationError(Exception):
    """Raised when skill validation fails."""
    pass


@dataclass
class SkillMetadata:
    """
    Metadata extracted from a SKILL.md file.

    Tier 1 information loaded at agent startup.
    """
    name: str
    description: str
    skill_path: Path
    version: Optional[str] = None
    author: Optional[str] = None
    allowed_tools: Optional[List[str]] = None


class SkillValidator:
    """
    Validates and parses SKILL.md files.

    Extracts YAML frontmatter and validates required fields.
    """

    # Regex for valid skill names: lowercase, hyphens, numbers only
    NAME_PATTERN = re.compile(r'^[a-z0-9-]+$')
    MAX_NAME_LENGTH = 64
    MAX_DESCRIPTION_LENGTH = 1024

    def parse(self, skill_path: Path) -> SkillMetadata:
        """
        Parse and validate a SKILL.md file.

        Args:
            skill_path: Path to SKILL.md file

        Returns:
            SkillMetadata with parsed information

        Raises:
            FileNotFoundError: If file doesn't exist
            SkillValidationError: If validation fails
        """
        if not skill_path.exists():
            raise FileNotFoundError(f"Skill file not found: {skill_path}")

        # Read file content
        content = skill_path.read_text(encoding='utf-8')

        # Extract frontmatter
        frontmatter_text, body = self.extract_frontmatter(content)

        # Parse YAML
        try:
            frontmatter = yaml.safe_load(frontmatter_text)
        except yaml.YAMLError as e:
            raise SkillValidationError(f"Invalid YAML in frontmatter: {e}")

        if not isinstance(frontmatter, dict):
            raise SkillValidationError("Frontmatter must be a YAML dictionary")

        # Validate required fields
        if 'name' not in frontmatter:
            raise SkillValidationError("Missing required field: name")
        if 'description' not in frontmatter:
            raise SkillValidationError("Missing required field: description")

        # Validate field formats
        self.validate_name(frontmatter['name'])
        self.validate_description(frontmatter['description'])

        # Build metadata
        metadata = SkillMetadata(
            name=frontmatter['name'],
            description=frontmatter['description'],
            skill_path=skill_path,
            version=frontmatter.get('version'),
            author=frontmatter.get('author'),
            allowed_tools=frontmatter.get('allowed-tools')
        )

        return metadata

    def validate_name(self, name: str) -> bool:
        """
        Validate skill name format.

        Rules:
        - Lowercase letters, numbers, hyphens only
        - Maximum 64 characters
        - Not empty

        Args:
            name: Skill name to validate

        Returns:
            True if valid

        Raises:
            SkillValidationError: If validation fails
        """
        if not name or not name.strip():
            raise SkillValidationError("Skill name cannot be empty")

        if len(name) > self.MAX_NAME_LENGTH:
            raise SkillValidationError(
                f"Skill name must be at most {self.MAX_NAME_LENGTH} characters, got {len(name)}"
            )

        if not self.NAME_PATTERN.match(name):
            if any(c.isupper() for c in name):
                raise SkillValidationError(
                    f"Skill name cannot contain uppercase letters: {name}"
                )
            else:
                raise SkillValidationError(
                    f"Skill name can only contain lowercase letters, numbers, and hyphens: {name}. "
                    "No special characters or spaces allowed."
                )

        return True

    def validate_description(self, description: str) -> bool:
        """
        Validate skill description.

        Rules:
        - Not empty (after stripping whitespace)
        - Maximum 1024 characters

        Args:
            description: Skill description to validate

        Returns:
            True if valid

        Raises:
            SkillValidationError: If validation fails
        """
        if not description or not description.strip():
            raise SkillValidationError("Skill description cannot be empty")

        if len(description) > self.MAX_DESCRIPTION_LENGTH:
            raise SkillValidationError(
                f"Skill description must be at most {self.MAX_DESCRIPTION_LENGTH} characters, "
                f"got {len(description)}"
            )

        return True

    def extract_frontmatter(self, content: str) -> Tuple[str, str]:
        """
        Extract YAML frontmatter from markdown content.

        Frontmatter is delimited by --- at start and end.

        Args:
            content: Full file content

        Returns:
            Tuple of (frontmatter_text, body_text)

        Raises:
            SkillValidationError: If frontmatter format is invalid
        """
        if not content.startswith('---'):
            raise SkillValidationError("No YAML frontmatter found (must start with ---)")

        # Find closing delimiter
        lines = content.split('\n')
        closing_index = None

        for i, line in enumerate(lines[1:], start=1):
            if line.strip() == '---':
                closing_index = i
                break

        if closing_index is None:
            raise SkillValidationError("No closing delimiter (---) found in frontmatter")

        # Extract frontmatter and body
        frontmatter_lines = lines[1:closing_index]
        frontmatter_text = '\n'.join(frontmatter_lines) + '\n'

        body_lines = lines[closing_index + 1:]
        body_text = '\n'.join(body_lines)

        return frontmatter_text, body_text
