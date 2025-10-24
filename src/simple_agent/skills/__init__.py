"""
Skills system for progressive disclosure architecture.

Implements three-tier skill loading:
- Tier 1: Metadata (name, description) loaded at startup
- Tier 2: Full SKILL.md content loaded when relevant
- Tier 3: Supporting resources loaded on demand
"""

from .validation import SkillValidator, SkillMetadata, SkillValidationError
from .paths import SkillPathResolver

__all__ = [
    "SkillValidator",
    "SkillMetadata",
    "SkillValidationError",
    "SkillPathResolver",
]
