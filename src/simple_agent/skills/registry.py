"""
Skill registry module for managing and indexing discovered skills.

This is a medium-level component that uses SkillLoader.
Provides fast O(1) lookup, state tracking for progressive disclosure, and query operations.
"""

import logging
from typing import Dict, List, Set, Optional

from .loader import SkillLoader
from .validation import SkillMetadata


logger = logging.getLogger(__name__)


class SkillRegistry:
    """
    Manages and indexes discovered skills with fast lookup and state tracking.

    The registry serves as a central index for all discovered skills,
    providing O(1) lookup by name and tracking which skills have been
    loaded (Tier 2/3 progressive disclosure).

    Responsibilities:
    - Index skills by name for fast retrieval
    - Track loaded state for progressive disclosure
    - Provide query and filtering operations
    - Ensure data immutability for thread safety

    Usage:
        loader = SkillLoader(path_resolver, validator)
        registry = SkillRegistry(skill_loader=loader)

        # Lookup
        skill = registry.get_skill("code-review")

        # Track loading
        if not registry.is_loaded("code-review"):
            # Load Tier 2 content...
            registry.mark_loaded("code-review")
    """

    def __init__(self, skill_loader: SkillLoader):
        """
        Initialize the registry and discover skills.

        Args:
            skill_loader: SkillLoader instance for discovering skills

        Note:
            Skills are discovered and indexed immediately upon initialization.
        """
        self.skill_loader = skill_loader
        self._skills: Dict[str, SkillMetadata] = {}
        self._loaded: Set[str] = set()

        # Discover and register skills
        self._register_skills()

        logger.info(f"Initialized SkillRegistry with {self.count_total()} skills")

    def _register_skills(self) -> None:
        """
        Discover skills from loader and build index.

        This is called during initialization to populate the registry.
        """
        discovered_skills = self.skill_loader.discover_skills()
        self._skills = self._build_index(discovered_skills)

        logger.debug(f"Registered {len(self._skills)} skills in registry")

    def _build_index(self, skills: List[SkillMetadata]) -> Dict[str, SkillMetadata]:
        """
        Build name-to-metadata index from skill list.

        Args:
            skills: List of SkillMetadata objects

        Returns:
            Dictionary mapping skill name to metadata
        """
        index = {}
        for skill in skills:
            index[skill.name] = skill

        return index

    # Core Lookup Operations

    def get_skill(self, name: Optional[str]) -> Optional[SkillMetadata]:
        """
        Retrieve skill metadata by name.

        Args:
            name: Skill name to lookup

        Returns:
            SkillMetadata if found, None otherwise

        Note:
            Returns copy of metadata to ensure immutability.
            Name matching is case-sensitive.
        """
        if not name or not name.strip():
            return None

        skill = self._skills.get(name)

        # Return the skill (dataclass is already immutable enough for our purposes)
        return skill

    def has_skill(self, name: str) -> bool:
        """
        Check if a skill exists in the registry.

        Args:
            name: Skill name to check

        Returns:
            True if skill exists, False otherwise
        """
        return name in self._skills

    def list_skills(self) -> List[SkillMetadata]:
        """
        Get list of all registered skills.

        Returns:
            List of SkillMetadata objects (copy to ensure immutability)
        """
        # Return a copy of the list to prevent external modification
        return list(self._skills.values())

    def get_skill_names(self) -> List[str]:
        """
        Get list of all skill names.

        Returns:
            List of skill names
        """
        return list(self._skills.keys())

    # Loaded State Tracking (Tier 2/3 Progressive Disclosure)

    def mark_loaded(self, name: str) -> bool:
        """
        Mark a skill as loaded (Tier 2/3 content loaded).

        Args:
            name: Skill name to mark as loaded

        Returns:
            True if successful, False if skill doesn't exist

        Note:
            Logs warning if attempting to mark non-existent skill.
        """
        if not self.has_skill(name):
            logger.warning(f"Attempted to mark non-existent skill as loaded: {name}")
            return False

        self._loaded.add(name)
        logger.debug(f"Marked skill as loaded: {name}")
        return True

    def is_loaded(self, name: str) -> bool:
        """
        Check if a skill has been loaded (Tier 2/3).

        Args:
            name: Skill name to check

        Returns:
            True if loaded, False otherwise
        """
        return name in self._loaded

    def get_loaded_skills(self) -> List[str]:
        """
        Get list of all loaded skill names.

        Returns:
            List of loaded skill names
        """
        return list(self._loaded)

    def unload_skill(self, name: str) -> bool:
        """
        Unload a skill (mark as not loaded).

        Args:
            name: Skill name to unload

        Returns:
            True if successful, False if skill wasn't loaded or doesn't exist
        """
        if name not in self._loaded:
            return False

        self._loaded.remove(name)
        logger.debug(f"Unloaded skill: {name}")
        return True

    # Query Operations

    def count_total(self) -> int:
        """
        Get total number of registered skills.

        Returns:
            Total skill count
        """
        return len(self._skills)

    def count_loaded(self) -> int:
        """
        Get number of loaded skills.

        Returns:
            Loaded skill count
        """
        return len(self._loaded)
