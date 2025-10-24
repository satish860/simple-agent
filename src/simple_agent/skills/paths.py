"""
Skill path resolution module for locating skill directories.

This is a low-level component with minimal dependencies.
Handles path resolution with priority ordering:
1. Explicit paths (constructor argument)
2. Environment variable (SIMPLE_AGENT_SKILLS_DIR)
3. Project-local (./skills/)
4. User-global (~/.simple-agent/skills/)

Edge Cases and Behavior:
    - Symlinks: Followed and resolved to their actual locations
    - Network paths: Supported (UNC paths on Windows, NFS mounts on Unix)
    - Permission denied: Silently skipped (path.exists() returns False)
    - Case sensitivity: Follows filesystem behavior (case-sensitive on Unix,
      case-insensitive on Windows/macOS)
    - Path traversal: Allowed (paths with .. are resolved to absolute paths)
    - Malformed paths: Silently skipped (e.g., null bytes, invalid characters)
    - Duplicate paths: Automatically deduplicated after resolution

Security Considerations:
    - This module reads from user-controlled inputs (environment variables,
      constructor arguments)
    - No path traversal protection is implemented by design
    - Intended for reading skill definitions, not executing code
    - Users should only configure trusted skill directories

Environment Variables:
    SIMPLE_AGENT_SKILLS_DIR: Colon-separated (Unix) or semicolon-separated
                             (Windows) list of skill directory paths.
                             Supports ~ and environment variable expansion.
"""

import os
from pathlib import Path
from typing import List, Optional


__all__ = ["SkillPathResolver"]


class SkillPathResolver:
    """
    Resolves skill directory paths from multiple sources with priority ordering.

    Priority order (highest to lowest):
    1. Explicit paths provided to constructor
    2. SIMPLE_AGENT_SKILLS_DIR environment variable
    3. Project-local ./skills/ directory
    4. User-global ~/.simple-agent/skills/ directory

    Only existing directories are returned. Invalid paths are silently skipped.

    Example:
        Basic usage with automatic path discovery:

        >>> resolver = SkillPathResolver()
        >>> paths = resolver.resolve_paths()
        >>> for path in paths:
        ...     print(f"Found skills directory: {path}")

    Example:
        With explicit custom paths:

        >>> resolver = SkillPathResolver(explicit_paths=[
        ...     "/opt/company-skills",
        ...     "~/my-custom-skills"
        ... ])
        >>> paths = resolver.resolve_paths()

    Example:
        Using environment variable (highest priority after explicit):

        >>> import os
        >>> os.environ["SIMPLE_AGENT_SKILLS_DIR"] = "/shared/skills:/local/skills"
        >>> resolver = SkillPathResolver()
        >>> paths = resolver.resolve_paths()

    Note:
        - Relative paths are resolved based on current working directory
        - Tilde (~) is expanded to home directory
        - Environment variables in paths are expanded (%VAR% or $VAR)
        - Duplicate paths are automatically deduplicated
        - Non-existent paths are silently skipped
    """

    ENV_VAR_NAME = "SIMPLE_AGENT_SKILLS_DIR"

    def __init__(self, explicit_paths: Optional[List[str]] = None):
        """
        Initialize the path resolver.

        Args:
            explicit_paths: Optional list of explicit paths to check first.
                          These take highest priority. Empty strings and None
                          values are filtered out automatically.

        Raises:
            TypeError: If explicit_paths is not a list or None
        """
        if explicit_paths is None:
            self.explicit_paths = []
        elif isinstance(explicit_paths, list):
            # Filter out None and empty strings, keep only valid string paths
            self.explicit_paths = [p for p in explicit_paths if p and isinstance(p, str)]
        else:
            raise TypeError(
                f"explicit_paths must be a list of strings or None, got {type(explicit_paths).__name__}"
            )

    def resolve_paths(self) -> List[Path]:
        """
        Resolve all skill directory paths in priority order.

        Returns:
            List of Path objects for existing directories, in priority order.
            Duplicates are removed, keeping the first occurrence.
        """
        paths: List[Path] = []

        # 1. Add explicit paths (highest priority)
        # Note: empty strings and None already filtered in __init__
        for path_str in self.explicit_paths:
            expanded = self._expand_path(path_str)
            if expanded and self._validate_path(expanded):
                paths.append(expanded)

        # 2. Add environment variable paths
        env_paths = self._get_env_paths()
        for path in env_paths:
            if self._validate_path(path):
                paths.append(path)

        # 3. Add project-local path
        project_local = self._get_project_local_path()
        if project_local and self._validate_path(project_local):
            paths.append(project_local)

        # 4. Add user-global path
        user_global = self._get_user_global_path()
        if user_global and self._validate_path(user_global):
            paths.append(user_global)

        # Deduplicate while maintaining order
        seen = set()
        deduplicated = []
        for path in paths:
            # Resolve to handle different representations of same path
            resolved = path.resolve()
            if resolved not in seen:
                seen.add(resolved)
                deduplicated.append(resolved)

        return deduplicated

    def _expand_path(self, path_str: str) -> Optional[Path]:
        """
        Expand a path string, handling ~ and environment variables.

        This method performs the following expansions:
        1. Environment variables (%VAR% on Windows, $VAR on Unix)
        2. Tilde (~) expansion to home directory
        3. Relative to absolute path conversion

        Args:
            path_str: Path string to expand

        Returns:
            Expanded Path object, or None if path is invalid

        Note:
            Returns None silently for malformed paths (e.g., paths with
            null bytes, invalid characters, or paths that cannot be
            resolved). This is intentional to allow graceful degradation -
            invalid paths are simply skipped rather than causing errors.

            Relative paths are resolved based on the current working
            directory at the time this method is called.
        """
        if not path_str or not path_str.strip():
            return None

        try:
            # Expand environment variables
            # Windows uses %VAR%, Unix uses $VAR
            expanded = os.path.expandvars(path_str)

            # Expand ~ to home directory
            expanded = os.path.expanduser(expanded)

            # Convert to Path and resolve to absolute
            path = Path(expanded)

            # Convert relative paths to absolute based on current directory
            if not path.is_absolute():
                path = path.resolve()

            return path

        except (ValueError, RuntimeError):
            # Silently handle invalid path strings (null bytes, invalid chars, etc.)
            # Graceful degradation: skip invalid paths rather than failing
            return None

    def _validate_path(self, path: Path) -> bool:
        """
        Validate that a path exists and is a directory.

        Args:
            path: Path to validate

        Returns:
            True if path exists and is a directory, False otherwise
        """
        try:
            return path.exists() and path.is_dir()
        except (OSError, ValueError):
            return False

    def _get_env_paths(self) -> List[Path]:
        """
        Get paths from SIMPLE_AGENT_SKILLS_DIR environment variable.

        Supports multiple paths separated by : (Unix) or ; (Windows).

        Returns:
            List of Path objects from environment variable
        """
        env_value = os.environ.get(self.ENV_VAR_NAME)

        if not env_value:
            return []

        # Use platform-appropriate path separator (: on Unix, ; on Windows)
        separator = os.pathsep

        # Split and expand each path
        paths = []
        for path_str in env_value.split(separator):
            if path_str.strip():
                expanded = self._expand_path(path_str.strip())
                if expanded:
                    paths.append(expanded)

        return paths

    def _get_project_local_path(self) -> Optional[Path]:
        """
        Get project-local skills directory (./skills/ from current directory).

        Returns:
            Path to project-local skills directory, or None if not in a project
        """
        try:
            current_dir = Path.cwd()
            skills_dir = current_dir / "skills"
            return skills_dir
        except (OSError, RuntimeError):
            return None

    def _get_user_global_path(self) -> Optional[Path]:
        """
        Get user-global skills directory (~/.simple-agent/skills/).

        Returns:
            Path to user-global skills directory
        """
        try:
            # Get home directory (works on both Windows and Unix)
            home = Path.home()
            global_dir = home / ".simple-agent" / "skills"
            return global_dir
        except (OSError, RuntimeError):
            return None
