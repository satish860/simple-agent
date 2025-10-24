"""
Tests for skill registry module.

Tests the SkillRegistry component:
- Skill registration and indexing
- Skill lookup and retrieval
- Loaded state tracking (Tier 2/3)
- Integration with SkillLoader
"""

import pytest
from pathlib import Path
from simple_agent.skills.registry import SkillRegistry
from simple_agent.skills.loader import SkillLoader
from simple_agent.skills.validation import SkillValidator, SkillMetadata
from simple_agent.skills.paths import SkillPathResolver


class TestInitializationAndRegistration:
    """Test registry initialization and skill registration."""

    def test_initialize_registry_with_loader(self, temp_skills_dir):
        """Should initialize registry with SkillLoader."""
        validator = SkillValidator()
        resolver = SkillPathResolver(explicit_paths=[str(temp_skills_dir)])
        loader = SkillLoader(path_resolver=resolver, validator=validator)

        registry = SkillRegistry(skill_loader=loader)

        assert registry is not None
        assert isinstance(registry, SkillRegistry)

    def test_auto_discover_skills_on_init(self, temp_skills_dir):
        """Should automatically discover and register skills on initialization."""
        validator = SkillValidator()
        resolver = SkillPathResolver(explicit_paths=[str(temp_skills_dir)])
        loader = SkillLoader(path_resolver=resolver, validator=validator)

        registry = SkillRegistry(skill_loader=loader)

        # Should have discovered skills from temp_skills_dir
        assert registry.count_total() > 0
        assert "skill-one" in registry.get_skill_names()
        assert "skill-two" in registry.get_skill_names()

    def test_handle_empty_skill_list(self, temp_empty_skills_dir):
        """Should handle initialization with no skills."""
        validator = SkillValidator()
        resolver = SkillPathResolver(explicit_paths=[str(temp_empty_skills_dir)])
        loader = SkillLoader(path_resolver=resolver, validator=validator)

        registry = SkillRegistry(skill_loader=loader)

        assert registry.count_total() == 0
        assert registry.list_skills() == []

    def test_skills_indexed_by_name(self, temp_skills_dir):
        """Skills should be indexed and retrievable by name."""
        validator = SkillValidator()
        resolver = SkillPathResolver(explicit_paths=[str(temp_skills_dir)])
        loader = SkillLoader(path_resolver=resolver, validator=validator)

        registry = SkillRegistry(skill_loader=loader)

        # Should be able to retrieve by name
        skill = registry.get_skill("skill-one")
        assert skill is not None
        assert skill.name == "skill-one"


class TestSkillLookup:
    """Test skill lookup operations."""

    def test_get_skill_by_name_exists(self, temp_skills_dir):
        """Should retrieve skill when it exists."""
        validator = SkillValidator()
        resolver = SkillPathResolver(explicit_paths=[str(temp_skills_dir)])
        loader = SkillLoader(path_resolver=resolver, validator=validator)
        registry = SkillRegistry(skill_loader=loader)

        skill = registry.get_skill("skill-one")

        assert skill is not None
        assert isinstance(skill, SkillMetadata)
        assert skill.name == "skill-one"

    def test_get_skill_by_name_not_found(self, temp_skills_dir):
        """Should return None when skill doesn't exist."""
        validator = SkillValidator()
        resolver = SkillPathResolver(explicit_paths=[str(temp_skills_dir)])
        loader = SkillLoader(path_resolver=resolver, validator=validator)
        registry = SkillRegistry(skill_loader=loader)

        skill = registry.get_skill("nonexistent-skill")

        assert skill is None

    def test_get_skill_returns_correct_metadata(self, temp_skills_dir):
        """Retrieved skill should have correct metadata."""
        validator = SkillValidator()
        resolver = SkillPathResolver(explicit_paths=[str(temp_skills_dir)])
        loader = SkillLoader(path_resolver=resolver, validator=validator)
        registry = SkillRegistry(skill_loader=loader)

        skill = registry.get_skill("skill-one")

        assert skill.name == "skill-one"
        assert skill.description == "Test skill"
        assert skill.skill_path.exists()
        assert skill.skill_path.name == "SKILL.md"

    def test_case_sensitive_name_matching(self, temp_skills_dir):
        """Skill name matching should be case-sensitive."""
        validator = SkillValidator()
        resolver = SkillPathResolver(explicit_paths=[str(temp_skills_dir)])
        loader = SkillLoader(path_resolver=resolver, validator=validator)
        registry = SkillRegistry(skill_loader=loader)

        # Should not find with different case
        skill = registry.get_skill("Skill-One")
        assert skill is None

        # Should find with exact case
        skill = registry.get_skill("skill-one")
        assert skill is not None

    def test_get_skill_with_none_or_empty_name(self, temp_skills_dir):
        """Should handle None or empty name gracefully."""
        validator = SkillValidator()
        resolver = SkillPathResolver(explicit_paths=[str(temp_skills_dir)])
        loader = SkillLoader(path_resolver=resolver, validator=validator)
        registry = SkillRegistry(skill_loader=loader)

        assert registry.get_skill(None) is None
        assert registry.get_skill("") is None
        assert registry.get_skill("   ") is None


class TestSkillListing:
    """Test skill listing operations."""

    def test_list_all_available_skills(self, temp_skills_dir):
        """Should list all available skills."""
        validator = SkillValidator()
        resolver = SkillPathResolver(explicit_paths=[str(temp_skills_dir)])
        loader = SkillLoader(path_resolver=resolver, validator=validator)
        registry = SkillRegistry(skill_loader=loader)

        skills = registry.list_skills()

        assert isinstance(skills, list)
        assert len(skills) == 2
        skill_names = [s.name for s in skills]
        assert "skill-one" in skill_names
        assert "skill-two" in skill_names

    def test_list_returns_correct_count(self, temp_multiple_skill_dirs):
        """List should return correct number of skills."""
        validator = SkillValidator()
        paths = [str(d) for d in temp_multiple_skill_dirs]
        resolver = SkillPathResolver(explicit_paths=paths)
        loader = SkillLoader(path_resolver=resolver, validator=validator)
        registry = SkillRegistry(skill_loader=loader)

        skills = registry.list_skills()

        assert len(skills) == 3  # skill-a, skill-b, skill-c

    def test_list_returns_skill_metadata_objects(self, temp_skills_dir):
        """List should return SkillMetadata objects."""
        validator = SkillValidator()
        resolver = SkillPathResolver(explicit_paths=[str(temp_skills_dir)])
        loader = SkillLoader(path_resolver=resolver, validator=validator)
        registry = SkillRegistry(skill_loader=loader)

        skills = registry.list_skills()

        assert all(isinstance(s, SkillMetadata) for s in skills)

    def test_list_is_immutable(self, temp_skills_dir):
        """Modifying returned list should not affect registry."""
        validator = SkillValidator()
        resolver = SkillPathResolver(explicit_paths=[str(temp_skills_dir)])
        loader = SkillLoader(path_resolver=resolver, validator=validator)
        registry = SkillRegistry(skill_loader=loader)

        skills1 = registry.list_skills()
        original_count = len(skills1)

        # Try to modify the returned list
        skills1.clear()

        # Registry should still have all skills
        skills2 = registry.list_skills()
        assert len(skills2) == original_count


class TestSkillExistence:
    """Test skill existence checking."""

    def test_has_skill_returns_true(self, temp_skills_dir):
        """Should return True when skill exists."""
        validator = SkillValidator()
        resolver = SkillPathResolver(explicit_paths=[str(temp_skills_dir)])
        loader = SkillLoader(path_resolver=resolver, validator=validator)
        registry = SkillRegistry(skill_loader=loader)

        assert registry.has_skill("skill-one") is True
        assert registry.has_skill("skill-two") is True

    def test_has_skill_returns_false(self, temp_skills_dir):
        """Should return False when skill doesn't exist."""
        validator = SkillValidator()
        resolver = SkillPathResolver(explicit_paths=[str(temp_skills_dir)])
        loader = SkillLoader(path_resolver=resolver, validator=validator)
        registry = SkillRegistry(skill_loader=loader)

        assert registry.has_skill("nonexistent") is False

    def test_get_skill_names(self, temp_skills_dir):
        """Should return list of all skill names."""
        validator = SkillValidator()
        resolver = SkillPathResolver(explicit_paths=[str(temp_skills_dir)])
        loader = SkillLoader(path_resolver=resolver, validator=validator)
        registry = SkillRegistry(skill_loader=loader)

        names = registry.get_skill_names()

        assert isinstance(names, list)
        assert "skill-one" in names
        assert "skill-two" in names
        assert len(names) == 2


class TestLoadedStateTracking:
    """Test tracking of loaded skills (Tier 2/3)."""

    def test_mark_skill_as_loaded(self, temp_skills_dir):
        """Should mark skill as loaded."""
        validator = SkillValidator()
        resolver = SkillPathResolver(explicit_paths=[str(temp_skills_dir)])
        loader = SkillLoader(path_resolver=resolver, validator=validator)
        registry = SkillRegistry(skill_loader=loader)

        # Initially not loaded
        assert registry.is_loaded("skill-one") is False

        # Mark as loaded
        result = registry.mark_loaded("skill-one")

        assert result is True
        assert registry.is_loaded("skill-one") is True

    def test_is_loaded_returns_true(self, temp_skills_dir):
        """Should return True when skill is loaded."""
        validator = SkillValidator()
        resolver = SkillPathResolver(explicit_paths=[str(temp_skills_dir)])
        loader = SkillLoader(path_resolver=resolver, validator=validator)
        registry = SkillRegistry(skill_loader=loader)

        registry.mark_loaded("skill-one")

        assert registry.is_loaded("skill-one") is True

    def test_is_loaded_returns_false(self, temp_skills_dir):
        """Should return False when skill is not loaded."""
        validator = SkillValidator()
        resolver = SkillPathResolver(explicit_paths=[str(temp_skills_dir)])
        loader = SkillLoader(path_resolver=resolver, validator=validator)
        registry = SkillRegistry(skill_loader=loader)

        assert registry.is_loaded("skill-one") is False

    def test_mark_nonexistent_skill_as_loaded(self, temp_skills_dir):
        """Should handle marking non-existent skill as loaded."""
        validator = SkillValidator()
        resolver = SkillPathResolver(explicit_paths=[str(temp_skills_dir)])
        loader = SkillLoader(path_resolver=resolver, validator=validator)
        registry = SkillRegistry(skill_loader=loader)

        # Should return False or log warning
        result = registry.mark_loaded("nonexistent")

        assert result is False

    def test_get_list_of_loaded_skills(self, temp_skills_dir):
        """Should return list of loaded skill names."""
        validator = SkillValidator()
        resolver = SkillPathResolver(explicit_paths=[str(temp_skills_dir)])
        loader = SkillLoader(path_resolver=resolver, validator=validator)
        registry = SkillRegistry(skill_loader=loader)

        # Mark some skills as loaded
        registry.mark_loaded("skill-one")
        registry.mark_loaded("skill-two")

        loaded = registry.get_loaded_skills()

        assert isinstance(loaded, list)
        assert "skill-one" in loaded
        assert "skill-two" in loaded
        assert len(loaded) == 2

    def test_unload_skill_functionality(self, temp_skills_dir):
        """Should unload a skill if implemented."""
        validator = SkillValidator()
        resolver = SkillPathResolver(explicit_paths=[str(temp_skills_dir)])
        loader = SkillLoader(path_resolver=resolver, validator=validator)
        registry = SkillRegistry(skill_loader=loader)

        # Load then unload
        registry.mark_loaded("skill-one")
        assert registry.is_loaded("skill-one") is True

        result = registry.unload_skill("skill-one")

        assert result is True
        assert registry.is_loaded("skill-one") is False


class TestIntegration:
    """Test integration with other components."""

    def test_registry_integrates_with_loader(self, temp_skills_tree):
        """Should integrate seamlessly with SkillLoader."""
        validator = SkillValidator()
        resolver = SkillPathResolver(explicit_paths=[str(temp_skills_tree)])
        loader = SkillLoader(path_resolver=resolver, validator=validator)

        registry = SkillRegistry(skill_loader=loader)

        # Should have discovered all skills from tree
        assert registry.count_total() == 3
        assert registry.has_skill("top-skill")
        assert registry.has_skill("nested-skill")
        assert registry.has_skill("deep-skill")

    def test_registry_discovers_skills_on_init(self, temp_multiple_skill_dirs):
        """Should discover all skills from multiple directories."""
        validator = SkillValidator()
        paths = [str(d) for d in temp_multiple_skill_dirs]
        resolver = SkillPathResolver(explicit_paths=paths)
        loader = SkillLoader(path_resolver=resolver, validator=validator)

        registry = SkillRegistry(skill_loader=loader)

        # Should have found skill-a, skill-b, skill-c
        assert registry.count_total() == 3
        names = registry.get_skill_names()
        assert "skill-a" in names
        assert "skill-b" in names
        assert "skill-c" in names

    def test_registry_handles_duplicates(self, temp_duplicate_skills_dirs):
        """Registry should handle duplicate names (loader handles this)."""
        validator = SkillValidator()
        paths = [str(d) for d in temp_duplicate_skills_dirs]
        resolver = SkillPathResolver(explicit_paths=paths)
        loader = SkillLoader(path_resolver=resolver, validator=validator)

        registry = SkillRegistry(skill_loader=loader)

        # Should have duplicate-skill (first) and unique-skill
        assert registry.count_total() == 2

        # Should be first occurrence
        skill = registry.get_skill("duplicate-skill")
        assert skill.version == "1.0.0"

    def test_end_to_end_workflow(self, temp_skills_dir):
        """Test complete workflow: paths → loader → registry → operations."""
        # Phase 2: Path resolution
        resolver = SkillPathResolver(explicit_paths=[str(temp_skills_dir)])
        paths = resolver.resolve_paths()
        assert len(paths) > 0

        # Phase 1: Validation
        validator = SkillValidator()

        # Phase 3: Loading
        loader = SkillLoader(path_resolver=resolver, validator=validator)

        # Phase 4: Registry
        registry = SkillRegistry(skill_loader=loader)

        # Operations
        assert registry.count_total() == 2
        skill = registry.get_skill("skill-one")
        assert skill is not None

        # Load tracking
        registry.mark_loaded("skill-one")
        assert registry.is_loaded("skill-one")
        assert registry.count_loaded() == 1


class TestQueryOperations:
    """Test query and counting operations."""

    def test_count_total_skills(self, temp_skills_dir):
        """Should return correct total skill count."""
        validator = SkillValidator()
        resolver = SkillPathResolver(explicit_paths=[str(temp_skills_dir)])
        loader = SkillLoader(path_resolver=resolver, validator=validator)
        registry = SkillRegistry(skill_loader=loader)

        assert registry.count_total() == 2

    def test_count_loaded_skills(self, temp_skills_dir):
        """Should return correct loaded skill count."""
        validator = SkillValidator()
        resolver = SkillPathResolver(explicit_paths=[str(temp_skills_dir)])
        loader = SkillLoader(path_resolver=resolver, validator=validator)
        registry = SkillRegistry(skill_loader=loader)

        # Initially 0
        assert registry.count_loaded() == 0

        # Mark one as loaded
        registry.mark_loaded("skill-one")
        assert registry.count_loaded() == 1

        # Mark another as loaded
        registry.mark_loaded("skill-two")
        assert registry.count_loaded() == 2

    def test_get_skills_by_loaded_state(self, temp_skills_dir):
        """Should filter skills by loaded state."""
        validator = SkillValidator()
        resolver = SkillPathResolver(explicit_paths=[str(temp_skills_dir)])
        loader = SkillLoader(path_resolver=resolver, validator=validator)
        registry = SkillRegistry(skill_loader=loader)

        # Mark one as loaded
        registry.mark_loaded("skill-one")

        loaded = registry.get_loaded_skills()
        assert len(loaded) == 1
        assert "skill-one" in loaded
        assert "skill-two" not in loaded


class TestEdgeCases:
    """Test edge cases and special scenarios."""

    def test_empty_registry_behavior(self, temp_empty_skills_dir):
        """Empty registry should handle all operations gracefully."""
        validator = SkillValidator()
        resolver = SkillPathResolver(explicit_paths=[str(temp_empty_skills_dir)])
        loader = SkillLoader(path_resolver=resolver, validator=validator)
        registry = SkillRegistry(skill_loader=loader)

        assert registry.count_total() == 0
        assert registry.count_loaded() == 0
        assert registry.list_skills() == []
        assert registry.get_skill_names() == []
        assert registry.get_skill("any") is None
        assert registry.has_skill("any") is False
        assert registry.is_loaded("any") is False

    def test_large_number_of_skills(self, tmp_path):
        """Should handle large number of skills efficiently."""
        # Create many skills
        root = tmp_path / "many_skills"
        root.mkdir()

        for i in range(100):
            skill_dir = root / f"skill-{i}"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text(
                f"---\nname: skill-{i}\ndescription: Skill {i}\n---\n",
                encoding='utf-8'
            )

        validator = SkillValidator()
        resolver = SkillPathResolver(explicit_paths=[str(root)])
        loader = SkillLoader(path_resolver=resolver, validator=validator)
        registry = SkillRegistry(skill_loader=loader)

        # Should handle 100 skills
        assert registry.count_total() == 100

        # Lookups should be fast (O(1))
        skill = registry.get_skill("skill-50")
        assert skill is not None
        assert skill.name == "skill-50"

    def test_special_characters_in_skill_names(self, tmp_path):
        """Should handle skill names with hyphens and numbers."""
        root = tmp_path / "special"
        root.mkdir()

        (root / "my-skill-123").mkdir()
        (root / "my-skill-123" / "SKILL.md").write_text(
            "---\nname: my-skill-123\ndescription: Special skill\n---\n",
            encoding='utf-8'
        )

        validator = SkillValidator()
        resolver = SkillPathResolver(explicit_paths=[str(root)])
        loader = SkillLoader(path_resolver=resolver, validator=validator)
        registry = SkillRegistry(skill_loader=loader)

        skill = registry.get_skill("my-skill-123")
        assert skill is not None
        assert skill.name == "my-skill-123"
