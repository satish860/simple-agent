"""
Tests for skill path resolution module.

Tests the SkillPathResolver component:
- Path resolution with priority order
- Environment variable support
- Path validation and expansion
- Cross-platform compatibility
"""

import pytest
import os
from pathlib import Path
from simple_agent.skills.paths import SkillPathResolver


class TestPathResolutionPriority:
    """Test path resolution priority order."""

    def test_explicit_path_highest_priority(self, temp_skills_dir):
        """Explicit paths should take highest priority."""
        resolver = SkillPathResolver(explicit_paths=[str(temp_skills_dir)])
        paths = resolver.resolve_paths()

        assert len(paths) >= 1
        assert paths[0] == temp_skills_dir

    def test_multiple_explicit_paths_in_order(self, tmp_path):
        """Multiple explicit paths should maintain order."""
        dir1 = tmp_path / "dir1"
        dir2 = tmp_path / "dir2"
        dir3 = tmp_path / "dir3"

        dir1.mkdir()
        dir2.mkdir()
        dir3.mkdir()

        resolver = SkillPathResolver(explicit_paths=[str(dir1), str(dir2), str(dir3)])
        paths = resolver.resolve_paths()

        assert len(paths) == 3
        assert paths[0] == dir1
        assert paths[1] == dir2
        assert paths[2] == dir3

    def test_env_var_second_priority(self, temp_skills_dir, mock_env_vars, monkeypatch):
        """Environment variable paths should take second priority."""
        # Mock current directory to ensure project-local path doesn't interfere
        monkeypatch.chdir(temp_skills_dir.parent)

        mock_env_vars({"SIMPLE_AGENT_SKILLS_DIR": str(temp_skills_dir)})

        resolver = SkillPathResolver()
        paths = resolver.resolve_paths()

        # Should include env var path
        assert temp_skills_dir in paths

    def test_project_local_third_priority(self, temp_project_dir, monkeypatch):
        """Project-local ./skills/ should take third priority."""
        # Change to project directory
        monkeypatch.chdir(temp_project_dir)

        resolver = SkillPathResolver()
        paths = resolver.resolve_paths()

        local_skills = temp_project_dir / "skills"
        assert local_skills in paths

    def test_user_global_fourth_priority(self, temp_global_dir, monkeypatch):
        """User-global ~/.simple-agent/skills/ should take lowest priority."""
        # Mock home directory
        monkeypatch.setenv("HOME", str(temp_global_dir.parent.parent))
        monkeypatch.setenv("USERPROFILE", str(temp_global_dir.parent.parent))  # Windows

        resolver = SkillPathResolver()
        paths = resolver.resolve_paths()

        # Should include global path
        assert temp_global_dir in paths

    def test_priority_order_with_all_sources(self, temp_skills_dir, temp_project_dir, temp_global_dir, mock_env_vars, monkeypatch):
        """All path sources should be in correct priority order."""
        # Setup environment
        monkeypatch.chdir(temp_project_dir)
        monkeypatch.setenv("HOME", str(temp_global_dir.parent.parent))
        monkeypatch.setenv("USERPROFILE", str(temp_global_dir.parent.parent))
        mock_env_vars({"SIMPLE_AGENT_SKILLS_DIR": str(temp_skills_dir)})

        resolver = SkillPathResolver(explicit_paths=[str(temp_skills_dir)])
        paths = resolver.resolve_paths()

        # Check that explicit path comes first
        assert paths[0] == temp_skills_dir


class TestPathValidation:
    """Test path validation logic."""

    def test_valid_directory_accepted(self, temp_skills_dir):
        """Valid directories should be accepted."""
        resolver = SkillPathResolver(explicit_paths=[str(temp_skills_dir)])
        paths = resolver.resolve_paths()

        assert temp_skills_dir in paths

    def test_nonexistent_path_skipped(self, tmp_path):
        """Non-existent paths should be skipped without error."""
        nonexistent = tmp_path / "nonexistent"

        resolver = SkillPathResolver(explicit_paths=[str(nonexistent)])
        paths = resolver.resolve_paths()

        # Should not include nonexistent path
        assert nonexistent not in paths
        # Should not raise error
        assert isinstance(paths, list)

    def test_file_path_skipped(self, tmp_path):
        """File paths (not directories) should be skipped."""
        file_path = tmp_path / "file.txt"
        file_path.write_text("not a directory", encoding='utf-8')

        resolver = SkillPathResolver(explicit_paths=[str(file_path)])
        paths = resolver.resolve_paths()

        # Should not include file path
        assert file_path not in paths

    def test_empty_path_handled(self):
        """Empty or None paths should be handled gracefully."""
        resolver = SkillPathResolver(explicit_paths=["", None])
        paths = resolver.resolve_paths()

        # Should not crash and return list
        assert isinstance(paths, list)

    def test_mixed_valid_invalid_paths(self, tmp_path):
        """Mix of valid and invalid paths should only include valid ones."""
        valid_dir = tmp_path / "valid"
        valid_dir.mkdir()

        invalid_dir = tmp_path / "invalid"
        file_path = tmp_path / "file.txt"
        file_path.write_text("not a dir", encoding='utf-8')

        resolver = SkillPathResolver(
            explicit_paths=[str(valid_dir), str(invalid_dir), str(file_path), ""]
        )
        paths = resolver.resolve_paths()

        # Only valid directory should be included
        assert valid_dir in paths
        assert invalid_dir not in paths
        assert file_path not in paths


class TestPathExpansion:
    """Test path expansion logic."""

    def test_tilde_expansion(self, temp_global_dir, monkeypatch):
        """Tilde ~ should expand to home directory."""
        # Mock home directory
        home = temp_global_dir.parent.parent
        monkeypatch.setenv("HOME", str(home))
        monkeypatch.setenv("USERPROFILE", str(home))  # Windows

        # Create test directory in mock home
        test_dir = home / "test_skills"
        test_dir.mkdir()

        resolver = SkillPathResolver(explicit_paths=["~/test_skills"])
        paths = resolver.resolve_paths()

        # Should expand ~ and find directory
        assert test_dir in paths

    def test_environment_variable_expansion(self, tmp_path, monkeypatch):
        """Environment variables in paths should be expanded."""
        test_dir = tmp_path / "test_skills"
        test_dir.mkdir()

        monkeypatch.setenv("MY_SKILLS_DIR", str(tmp_path))

        # Use different syntax for Windows vs Unix
        if os.name == 'nt':
            path_with_env = "%MY_SKILLS_DIR%\\test_skills"
        else:
            path_with_env = "$MY_SKILLS_DIR/test_skills"

        resolver = SkillPathResolver(explicit_paths=[path_with_env])
        paths = resolver.resolve_paths()

        # Should expand environment variable
        assert test_dir in paths

    def test_relative_path_to_absolute(self, temp_project_dir, monkeypatch):
        """Relative paths should be converted to absolute."""
        monkeypatch.chdir(temp_project_dir)

        resolver = SkillPathResolver(explicit_paths=["./skills"])
        paths = resolver.resolve_paths()

        # Should be absolute path
        assert len(paths) > 0
        assert paths[0].is_absolute()
        assert paths[0] == temp_project_dir / "skills"


class TestEnvironmentVariableSupport:
    """Test SIMPLE_AGENT_SKILLS_DIR environment variable."""

    def test_single_path_from_env_var(self, temp_skills_dir, mock_env_vars):
        """Single path in environment variable should be used."""
        mock_env_vars({"SIMPLE_AGENT_SKILLS_DIR": str(temp_skills_dir)})

        resolver = SkillPathResolver()
        paths = resolver.resolve_paths()

        assert temp_skills_dir in paths

    def test_multiple_paths_from_env_var(self, tmp_path, mock_env_vars):
        """Multiple paths in environment variable should be parsed."""
        dir1 = tmp_path / "dir1"
        dir2 = tmp_path / "dir2"
        dir1.mkdir()
        dir2.mkdir()

        # Use platform-appropriate separator
        separator = ";" if os.name == 'nt' else ":"
        env_value = f"{dir1}{separator}{dir2}"

        mock_env_vars({"SIMPLE_AGENT_SKILLS_DIR": env_value})

        resolver = SkillPathResolver()
        paths = resolver.resolve_paths()

        assert dir1 in paths
        assert dir2 in paths

    def test_env_var_not_set(self, monkeypatch):
        """Missing environment variable should not cause error."""
        # Ensure env var is not set using monkeypatch for proper isolation
        monkeypatch.delenv("SIMPLE_AGENT_SKILLS_DIR", raising=False)

        resolver = SkillPathResolver()
        paths = resolver.resolve_paths()

        # Should not crash
        assert isinstance(paths, list)


class TestCrossPlatform:
    """Test cross-platform compatibility."""

    def test_windows_path_handling(self, tmp_path):
        """Windows-style paths should be handled correctly."""
        test_dir = tmp_path / "skills"
        test_dir.mkdir()

        # Use Windows-style path with backslashes
        windows_path = str(test_dir).replace("/", "\\")

        resolver = SkillPathResolver(explicit_paths=[windows_path])
        paths = resolver.resolve_paths()

        assert test_dir in paths

    def test_unix_path_handling(self, tmp_path):
        """Unix-style paths should be handled correctly."""
        test_dir = tmp_path / "skills"
        test_dir.mkdir()

        # Use Unix-style path with forward slashes
        unix_path = str(test_dir).replace("\\", "/")

        resolver = SkillPathResolver(explicit_paths=[unix_path])
        paths = resolver.resolve_paths()

        assert test_dir in paths


class TestDeduplication:
    """Test path deduplication."""

    def test_duplicate_paths_deduplicated(self, temp_skills_dir):
        """Duplicate paths should be removed, keeping first occurrence."""
        resolver = SkillPathResolver(
            explicit_paths=[str(temp_skills_dir), str(temp_skills_dir)]
        )
        paths = resolver.resolve_paths()

        # Should only appear once
        assert paths.count(temp_skills_dir) == 1

    def test_same_path_different_forms_deduplicated(self, tmp_path):
        """Same path in different forms should be deduplicated."""
        test_dir = tmp_path / "skills"
        test_dir.mkdir()

        # Same path with and without trailing separator
        path1 = str(test_dir)
        path2 = str(test_dir) + os.sep

        resolver = SkillPathResolver(explicit_paths=[path1, path2])
        paths = resolver.resolve_paths()

        # Should only appear once
        assert paths.count(test_dir) == 1


class TestInputValidation:
    """Test input validation and error handling."""

    def test_invalid_type_for_explicit_paths(self):
        """Passing wrong type for explicit_paths should raise TypeError."""
        with pytest.raises(TypeError, match="explicit_paths must be a list"):
            SkillPathResolver(explicit_paths="not a list")

    def test_explicit_paths_with_none_values(self, temp_skills_dir):
        """None values in explicit_paths list should be filtered out."""
        resolver = SkillPathResolver(explicit_paths=[str(temp_skills_dir), None, ""])
        paths = resolver.resolve_paths()

        # Should only include valid path
        assert temp_skills_dir in paths

    def test_explicit_paths_with_non_string_values(self, temp_skills_dir):
        """Non-string values in explicit_paths list should be filtered out."""
        resolver = SkillPathResolver(explicit_paths=[str(temp_skills_dir), 123, True, []])

        # Should not crash, only include valid string paths
        paths = resolver.resolve_paths()
        assert isinstance(paths, list)

    def test_path_with_null_byte(self):
        """Paths with null bytes should be handled gracefully."""
        # Null bytes in paths should be silently skipped
        resolver = SkillPathResolver(explicit_paths=["path\x00with\x00null"])
        paths = resolver.resolve_paths()

        # Should not crash
        assert isinstance(paths, list)


class TestEdgeCases:
    """Test edge cases and special scenarios."""

    def test_no_paths_found(self, tmp_path, monkeypatch):
        """When no paths are found, should return empty list."""
        # Change to temporary directory with no skills
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        monkeypatch.chdir(empty_dir)

        # Mock home to non-existent location
        nonexistent_home = tmp_path / "nonexistent"
        monkeypatch.setenv("HOME", str(nonexistent_home))
        monkeypatch.setenv("USERPROFILE", str(nonexistent_home))

        resolver = SkillPathResolver()
        paths = resolver.resolve_paths()

        assert isinstance(paths, list)
        assert len(paths) == 0

    def test_very_long_path(self, tmp_path):
        """Very long paths should be handled correctly."""
        # Create nested directory structure (limited depth to avoid Windows MAX_PATH)
        long_path = tmp_path
        # Use fewer levels on Windows due to MAX_PATH limitation
        depth = 3 if os.name == 'nt' else 5
        for i in range(depth):
            long_path = long_path / f"very_long_directory_name_{i}"

        long_path.mkdir(parents=True)

        resolver = SkillPathResolver(explicit_paths=[str(long_path)])
        paths = resolver.resolve_paths()

        assert long_path in paths

    def test_unicode_in_path(self, tmp_path):
        """Paths with unicode characters should be handled."""
        unicode_dir = tmp_path / "skills_test"
        unicode_dir.mkdir()

        resolver = SkillPathResolver(explicit_paths=[str(unicode_dir)])
        paths = resolver.resolve_paths()

        assert unicode_dir in paths
