"""
Skill loader module for discovering and loading skills from directories.

This is a medium-level component that uses SkillValidator and SkillPathResolver.
Handles skill discovery, validation, and deduplication.
"""

import logging
from pathlib import Path
from typing import List, Set, Optional

from .validation import SkillValidator, SkillMetadata, SkillValidationError
from .paths import SkillPathResolver


logger = logging.getLogger(__name__)


class SkillLoader:
    """
    Discovers and loads skills from directories.

    Uses SkillPathResolver to get directories to scan and SkillValidator
    to validate each SKILL.md file found.

    Handles:
    - Recursive directory scanning
    - Invalid skill files (logs warnings, continues loading)
    - Duplicate skill names (first occurrence wins based on path priority)
    - Empty or non-existent directories
    """

    def __init__(self, path_resolver: SkillPathResolver, validator: SkillValidator):
        """
        Initialize the skill loader.

        Args:
            path_resolver: SkillPathResolver instance for finding skill directories
            validator: SkillValidator instance for validating skills
        """
        self.path_resolver = path_resolver
        self.validator = validator

    def discover_skills(self) -> List[SkillMetadata]:
        """
        Discover all skills from configured paths.

        Scans all directories provided by path_resolver, recursively finds
        SKILL.md files, validates them, and returns metadata for all valid skills.

        Duplicate skill names are handled by keeping the first occurrence
        (based on path priority from resolver).

        Returns:
            List of SkillMetadata objects for all discovered valid skills.
            Returns empty list if no skills found or all paths are invalid.

        Note:
            This method never raises exceptions. Invalid skills are logged
            and skipped, allowing other skills to load successfully.
        """
        all_skills: List[SkillMetadata] = []
        seen_names: Set[str] = set()

        # Get directories to scan from path resolver
        skill_dirs = self.path_resolver.resolve_paths()

        if not skill_dirs:
            logger.debug("No skill directories found to scan")
            return all_skills

        logger.debug(f"Scanning {len(skill_dirs)} skill directories")

        # Scan each directory
        for skill_dir in skill_dirs:
            logger.debug(f"Scanning directory: {skill_dir}")

            try:
                dir_skills = self._scan_directory(skill_dir, seen_names)
                all_skills.extend(dir_skills)
                logger.debug(f"Found {len(dir_skills)} new skills in {skill_dir}")

            except Exception as e:
                logger.warning(f"Error scanning directory {skill_dir}: {e}")
                continue

        logger.info(f"Discovered {len(all_skills)} total skills")
        return all_skills

    def _scan_directory(self, directory: Path, seen_names: Set[str]) -> List[SkillMetadata]:
        """
        Scan a single directory for skills.

        Args:
            directory: Directory path to scan
            seen_names: Set of skill names already discovered (for duplicate detection)

        Returns:
            List of SkillMetadata objects found in this directory
        """
        skills: List[SkillMetadata] = []

        # Find all SKILL.md files recursively
        skill_files = self._find_skill_files(directory)

        logger.debug(f"Found {len(skill_files)} SKILL.md files in {directory}")

        # Load each skill file
        for skill_file in skill_files:
            skill = self._load_skill(skill_file, seen_names)
            if skill:
                skills.append(skill)
                seen_names.add(skill.name)

        return skills

    def _find_skill_files(self, directory: Path) -> List[Path]:
        """
        Find all SKILL.md files in a directory recursively.

        Args:
            directory: Directory to search

        Returns:
            List of Path objects for SKILL.md files found
        """
        try:
            # Use rglob for recursive search
            skill_files = list(directory.rglob("SKILL.md"))
            return skill_files

        except (OSError, PermissionError) as e:
            logger.warning(f"Error accessing directory {directory}: {e}")
            return []

    def _load_skill(self, skill_path: Path, seen_names: Set[str]) -> Optional[SkillMetadata]:
        """
        Load and validate a single skill file.

        Args:
            skill_path: Path to SKILL.md file
            seen_names: Set of skill names already loaded (for duplicate detection)

        Returns:
            SkillMetadata if valid, None if invalid or duplicate

        Note:
            Logs warnings for invalid skills and duplicates, but does not raise exceptions.
        """
        try:
            # Validate and parse the skill
            metadata = self.validator.parse(skill_path)

            # Check for duplicate names
            if self._is_duplicate(metadata.name, seen_names):
                logger.warning(
                    f"Duplicate skill name '{metadata.name}' found at {skill_path}. "
                    f"Skipping (first occurrence takes precedence)"
                )
                return None

            logger.debug(f"Loaded skill '{metadata.name}' from {skill_path}")
            return metadata

        except SkillValidationError as e:
            logger.warning(f"Invalid skill at {skill_path}: {e}")
            return None

        except FileNotFoundError as e:
            logger.warning(f"Skill file not found: {skill_path}: {e}")
            return None

        except PermissionError as e:
            logger.warning(f"Permission denied reading skill: {skill_path}: {e}")
            return None

        except Exception as e:
            logger.warning(f"Unexpected error loading skill at {skill_path}: {e}")
            return None

    def _is_duplicate(self, skill_name: str, seen_names: Set[str]) -> bool:
        """
        Check if a skill name has already been loaded.

        Args:
            skill_name: Name of skill to check
            seen_names: Set of already-loaded skill names

        Returns:
            True if duplicate, False otherwise
        """
        return skill_name in seen_names
