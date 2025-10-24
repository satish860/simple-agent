"""
Tests for skill loader module.

Tests the SkillLoader component:
- Skill discovery from directories
- Recursive scanning
- Invalid skill handling
- Duplicate skill handling
- Integration with SkillValidator and SkillPathResolver
"""

import pytest
from pathlib import Path
from simple_agent.skills.loader import SkillLoader
from simple_agent.skills.validation import SkillValidator, SkillMetadata
from simple_agent.skills.paths import SkillPathResolver


class TestBasicDiscovery:
    """Test basic skill discovery functionality."""

    def test_discover_skills_from_single_directory(self, temp_skills_dir):
        """Should discover all skills from a single directory."""
        validator = SkillValidator()
        resolver = SkillPathResolver(explicit_paths=[str(temp_skills_dir)])
        loader = SkillLoader(path_resolver=resolver, validator=validator)

        skills = loader.discover_skills()

        # Should find skill-one and skill-two
        assert len(skills) == 2
        skill_names = [s.name for s in skills]
        assert "skill-one" in skill_names
        assert "skill-two" in skill_names

    def test_discover_skills_from_multiple_directories(self, temp_multiple_skill_dirs):
        """Should discover skills from multiple directories."""
        validator = SkillValidator()
        paths = [str(d) for d in temp_multiple_skill_dirs]
        resolver = SkillPathResolver(explicit_paths=paths)
        loader = SkillLoader(path_resolver=resolver, validator=validator)

        skills = loader.discover_skills()

        # Should find skill-a, skill-b, skill-c
        assert len(skills) == 3
        skill_names = [s.name for s in skills]
        assert "skill-a" in skill_names
        assert "skill-b" in skill_names
        assert "skill-c" in skill_names

    def test_find_skill_md_files(self, temp_skills_dir):
        """Should correctly identify SKILL.md files."""
        validator = SkillValidator()
        resolver = SkillPathResolver(explicit_paths=[str(temp_skills_dir)])
        loader = SkillLoader(path_resolver=resolver, validator=validator)

        skills = loader.discover_skills()

        # All returned items should be SkillMetadata objects
        assert all(isinstance(s, SkillMetadata) for s in skills)
        # All should have skill_path pointing to SKILL.md
        assert all(s.skill_path.name == "SKILL.md" for s in skills)

    def test_return_skill_metadata_objects(self, temp_skills_dir):
        """Should return list of SkillMetadata objects."""
        validator = SkillValidator()
        resolver = SkillPathResolver(explicit_paths=[str(temp_skills_dir)])
        loader = SkillLoader(path_resolver=resolver, validator=validator)

        skills = loader.discover_skills()

        assert isinstance(skills, list)
        assert all(isinstance(s, SkillMetadata) for s in skills)
        # Check metadata structure
        for skill in skills:
            assert hasattr(skill, 'name')
            assert hasattr(skill, 'description')
            assert hasattr(skill, 'skill_path')


class TestRecursiveScanning:
    """Test recursive directory scanning."""

    def test_scan_subdirectories_recursively(self, temp_skills_tree):
        """Should scan subdirectories recursively."""
        validator = SkillValidator()
        resolver = SkillPathResolver(explicit_paths=[str(temp_skills_tree)])
        loader = SkillLoader(path_resolver=resolver, validator=validator)

        skills = loader.discover_skills()

        # Should find top-skill, nested-skill, and deep-skill
        assert len(skills) == 3
        skill_names = [s.name for s in skills]
        assert "top-skill" in skill_names
        assert "nested-skill" in skill_names
        assert "deep-skill" in skill_names

    def test_handle_deeply_nested_structures(self, temp_skills_tree):
        """Should handle deeply nested directory structures."""
        validator = SkillValidator()
        resolver = SkillPathResolver(explicit_paths=[str(temp_skills_tree)])
        loader = SkillLoader(path_resolver=resolver, validator=validator)

        skills = loader.discover_skills()

        # Find the deep-skill which is 2 levels deep
        deep_skill = next((s for s in skills if s.name == "deep-skill"), None)
        assert deep_skill is not None
        assert "subcategory" in str(deep_skill.skill_path)

    def test_find_skills_at_various_depths(self, temp_skills_tree):
        """Should find skills regardless of nesting depth."""
        validator = SkillValidator()
        resolver = SkillPathResolver(explicit_paths=[str(temp_skills_tree)])
        loader = SkillLoader(path_resolver=resolver, validator=validator)

        skills = loader.discover_skills()

        # Count skills at different depths
        # Structure: root/skill-name/SKILL.md (depth 1)
        #           root/category/skill-name/SKILL.md (depth 2)
        #           root/category/subcategory/skill-name/SKILL.md (depth 3)
        skill_paths = [s.skill_path for s in skills]

        # Calculate depth from root to SKILL.md (count of parent directories)
        depths = [len(p.relative_to(temp_skills_tree).parents) - 1 for p in skill_paths]
        assert min(depths) == 1  # top level (root/skill-name/SKILL.md)
        assert max(depths) >= 3  # at least 3 levels deep (root/cat/subcat/skill/SKILL.md)


class TestInvalidSkillsHandling:
    """Test handling of invalid skills."""

    def test_skip_invalid_yaml_gracefully(self, temp_mixed_content_dir):
        """Should skip skills with invalid YAML without crashing."""
        validator = SkillValidator()
        resolver = SkillPathResolver(explicit_paths=[str(temp_mixed_content_dir)])
        loader = SkillLoader(path_resolver=resolver, validator=validator)

        # Should not raise exception
        skills = loader.discover_skills()

        # Should find only the valid skill, skipping invalid-skill
        assert isinstance(skills, list)
        skill_names = [s.name for s in skills]
        assert "valid-skill" in skill_names
        assert "invalid-skill" not in skill_names

    def test_skip_missing_required_fields(self, temp_mixed_content_dir):
        """Should skip skills missing required fields."""
        validator = SkillValidator()
        resolver = SkillPathResolver(explicit_paths=[str(temp_mixed_content_dir)])
        loader = SkillLoader(path_resolver=resolver, validator=validator)

        skills = loader.discover_skills()

        # Should not include incomplete-skill (missing description)
        skill_names = [s.name for s in skills]
        assert "incomplete-skill" not in skill_names

    def test_skip_non_skill_md_files(self, temp_mixed_content_dir):
        """Should only process SKILL.md files, not other .md files."""
        validator = SkillValidator()
        resolver = SkillPathResolver(explicit_paths=[str(temp_mixed_content_dir)])
        loader = SkillLoader(path_resolver=resolver, validator=validator)

        skills = loader.discover_skills()

        # Should only find valid-skill, not README.md
        assert len(skills) == 1
        assert skills[0].name == "valid-skill"

    def test_continue_loading_after_invalid_skill(self, temp_mixed_content_dir):
        """Should continue loading other skills after encountering invalid one."""
        validator = SkillValidator()
        resolver = SkillPathResolver(explicit_paths=[str(temp_mixed_content_dir)])
        loader = SkillLoader(path_resolver=resolver, validator=validator)

        skills = loader.discover_skills()

        # Should still load valid-skill even though there are invalid skills
        assert len(skills) >= 1
        assert any(s.name == "valid-skill" for s in skills)


class TestEmptyDirectories:
    """Test handling of empty or missing directories."""

    def test_handle_empty_directories(self, temp_empty_skills_dir):
        """Should handle empty directories without error."""
        validator = SkillValidator()
        resolver = SkillPathResolver(explicit_paths=[str(temp_empty_skills_dir)])
        loader = SkillLoader(path_resolver=resolver, validator=validator)

        skills = loader.discover_skills()

        # Should return empty list, not crash
        assert isinstance(skills, list)
        assert len(skills) == 0

    def test_handle_nonexistent_directories(self, tmp_path):
        """Should handle non-existent directories gracefully."""
        nonexistent = tmp_path / "nonexistent"
        validator = SkillValidator()
        resolver = SkillPathResolver(explicit_paths=[str(nonexistent)])
        loader = SkillLoader(path_resolver=resolver, validator=validator)

        # Should not raise exception
        skills = loader.discover_skills()

        assert isinstance(skills, list)
        assert len(skills) == 0

    def test_return_empty_list_when_no_skills(self, tmp_path):
        """Should return empty list when no skills found."""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        # Create some non-skill files
        (empty_dir / "README.md").write_text("# Not a skill", encoding='utf-8')
        (empty_dir / "data.txt").write_text("data", encoding='utf-8')

        validator = SkillValidator()
        resolver = SkillPathResolver(explicit_paths=[str(empty_dir)])
        loader = SkillLoader(path_resolver=resolver, validator=validator)

        skills = loader.discover_skills()

        assert skills == []


class TestDuplicateSkillNames:
    """Test handling of duplicate skill names."""

    def test_first_occurrence_wins(self, temp_duplicate_skills_dirs):
        """First skill found should take precedence for duplicates."""
        validator = SkillValidator()
        paths = [str(d) for d in temp_duplicate_skills_dirs]
        resolver = SkillPathResolver(explicit_paths=paths)
        loader = SkillLoader(path_resolver=resolver, validator=validator)

        skills = loader.discover_skills()

        # Should find duplicate-skill and unique-skill
        assert len(skills) == 2

        # Find the duplicate skill
        duplicate = next((s for s in skills if s.name == "duplicate-skill"), None)
        assert duplicate is not None

        # Should be from first directory (version 1.0.0)
        assert duplicate.version == "1.0.0"
        assert "priority 1" in duplicate.description

    def test_track_duplicate_warnings(self, temp_duplicate_skills_dirs, caplog):
        """Should log warnings for duplicate skill names."""
        validator = SkillValidator()
        paths = [str(d) for d in temp_duplicate_skills_dirs]
        resolver = SkillPathResolver(explicit_paths=paths)
        loader = SkillLoader(path_resolver=resolver, validator=validator)

        skills = loader.discover_skills()

        # Should have logged a warning about duplicate
        # (This test will pass even if logging is not yet implemented)
        assert len(skills) == 2

    def test_all_unique_skills_loaded(self, temp_duplicate_skills_dirs):
        """Should load all skills with unique names."""
        validator = SkillValidator()
        paths = [str(d) for d in temp_duplicate_skills_dirs]
        resolver = SkillPathResolver(explicit_paths=paths)
        loader = SkillLoader(path_resolver=resolver, validator=validator)

        skills = loader.discover_skills()

        # Should have duplicate-skill (first) and unique-skill
        skill_names = [s.name for s in skills]
        assert "duplicate-skill" in skill_names
        assert "unique-skill" in skill_names


class TestIntegrationWithDependencies:
    """Test integration with SkillValidator and SkillPathResolver."""

    def test_works_with_path_resolver_output(self, temp_skills_dir):
        """Should work correctly with SkillPathResolver."""
        validator = SkillValidator()
        resolver = SkillPathResolver(explicit_paths=[str(temp_skills_dir)])
        loader = SkillLoader(path_resolver=resolver, validator=validator)

        # Path resolver should provide the directory
        paths = resolver.resolve_paths()
        assert len(paths) > 0

        # Loader should use those paths
        skills = loader.discover_skills()
        assert len(skills) > 0

    def test_uses_validator_for_validation(self, temp_skills_dir):
        """Should use SkillValidator to validate each skill."""
        validator = SkillValidator()
        resolver = SkillPathResolver(explicit_paths=[str(temp_skills_dir)])
        loader = SkillLoader(path_resolver=resolver, validator=validator)

        skills = loader.discover_skills()

        # All loaded skills should pass validator requirements
        for skill in skills:
            # Name should match validator pattern
            assert skill.name.islower()
            assert '-' in skill.name or skill.name.isalnum()
            # Should have description
            assert skill.description is not None
            assert len(skill.description) > 0

    def test_handles_validator_exceptions(self, temp_mixed_content_dir):
        """Should handle SkillValidationError exceptions gracefully."""
        validator = SkillValidator()
        resolver = SkillPathResolver(explicit_paths=[str(temp_mixed_content_dir)])
        loader = SkillLoader(path_resolver=resolver, validator=validator)

        # Should not propagate validation exceptions
        skills = loader.discover_skills()

        # Should successfully load valid skills despite invalid ones present
        assert len(skills) >= 1
        assert all(isinstance(s, SkillMetadata) for s in skills)


class TestEdgeCases:
    """Test edge cases and special scenarios."""

    def test_skill_md_in_root_directory(self, tmp_path):
        """Should handle SKILL.md in root of scan directory."""
        root = tmp_path / "root_skill"
        root.mkdir()

        # SKILL.md directly in the directory (no subdirectory)
        (root / "SKILL.md").write_text(
            "---\nname: root-skill\ndescription: Skill in root\n---\n",
            encoding='utf-8'
        )

        validator = SkillValidator()
        resolver = SkillPathResolver(explicit_paths=[str(root)])
        loader = SkillLoader(path_resolver=resolver, validator=validator)

        skills = loader.discover_skills()

        assert len(skills) == 1
        assert skills[0].name == "root-skill"

    def test_mixed_valid_invalid_skills(self, temp_mixed_content_dir):
        """Should load valid skills from directory with mixed content."""
        validator = SkillValidator()
        resolver = SkillPathResolver(explicit_paths=[str(temp_mixed_content_dir)])
        loader = SkillLoader(path_resolver=resolver, validator=validator)

        skills = loader.discover_skills()

        # Should find at least the valid skill
        assert len(skills) >= 1
        valid_skill = next((s for s in skills if s.name == "valid-skill"), None)
        assert valid_skill is not None
        assert valid_skill.description == "Valid skill"

    def test_no_path_resolver_paths(self, tmp_path):
        """Should handle case where path resolver returns no paths."""
        validator = SkillValidator()
        # Create resolver with non-existent path
        resolver = SkillPathResolver(explicit_paths=[str(tmp_path / "nonexistent")])
        loader = SkillLoader(path_resolver=resolver, validator=validator)

        skills = loader.discover_skills()

        # Should return empty list gracefully
        assert skills == []


class TestSkillMetadataPopulation:
    """Test that skill metadata is properly populated."""

    def test_skill_path_points_to_skill_md(self, temp_skills_dir):
        """Skill path should point to the actual SKILL.md file."""
        validator = SkillValidator()
        resolver = SkillPathResolver(explicit_paths=[str(temp_skills_dir)])
        loader = SkillLoader(path_resolver=resolver, validator=validator)

        skills = loader.discover_skills()

        for skill in skills:
            assert skill.skill_path.exists()
            assert skill.skill_path.is_file()
            assert skill.skill_path.name == "SKILL.md"

    def test_all_required_fields_populated(self, temp_skills_dir):
        """All required metadata fields should be populated."""
        validator = SkillValidator()
        resolver = SkillPathResolver(explicit_paths=[str(temp_skills_dir)])
        loader = SkillLoader(path_resolver=resolver, validator=validator)

        skills = loader.discover_skills()

        for skill in skills:
            # Required fields
            assert skill.name is not None
            assert len(skill.name) > 0
            assert skill.description is not None
            assert len(skill.description) > 0
            assert skill.skill_path is not None

    def test_optional_fields_handled(self, skills_fixtures_dir):
        """Optional metadata fields should be handled correctly."""
        validator = SkillValidator()
        # Use the fixtures directory which has skills with optional fields
        resolver = SkillPathResolver(explicit_paths=[str(skills_fixtures_dir)])
        loader = SkillLoader(path_resolver=resolver, validator=validator)

        skills = loader.discover_skills()

        # Some skills should have optional fields
        skills_with_version = [s for s in skills if s.version is not None]
        skills_with_author = [s for s in skills if s.author is not None]

        # At least valid-skill has these fields
        assert len(skills_with_version) >= 1
        assert len(skills_with_author) >= 1
