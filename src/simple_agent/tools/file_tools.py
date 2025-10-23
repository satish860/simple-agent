"""
File Operation Tools

Tools for interacting with the filesystem.
Inspired by Claude Code's file manipulation capabilities.
"""

import os
from pathlib import Path
from typing import Dict, Any
from .base import BaseTool


class ReadFileTool(BaseTool):
    """Read contents of a file."""

    @property
    def name(self) -> str:
        return "read_file"

    @property
    def description(self) -> str:
        return "Read the contents of a file from the filesystem"

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Absolute or relative path to the file to read"
                }
            },
            "required": ["file_path"]
        }

    @property
    def system_reminder(self) -> str:
        return """When reading files, always check if the file exists before attempting to read it.
If the file is large, consider reading it in chunks or asking the user before proceeding."""

    def execute(self, file_path: str) -> str:
        """
        Read file contents.

        Args:
            file_path: Path to file

        Returns:
            File contents

        Raises:
            FileNotFoundError: If file doesn't exist
            RuntimeError: If file cannot be read
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if not path.is_file():
            raise ValueError(f"Not a file: {file_path}")

        try:
            # Read with UTF-8 encoding
            content = path.read_text(encoding='utf-8')
            return f"File: {file_path}\n{'='*60}\n{content}"

        except UnicodeDecodeError:
            # Try binary read if UTF-8 fails
            raise RuntimeError(
                f"Cannot read file '{file_path}': File appears to be binary"
            )

        except Exception as e:
            raise RuntimeError(
                f"Error reading file '{file_path}': {str(e)}"
            )


class WriteFileTool(BaseTool):
    """Write content to a file (creates or overwrites)."""

    @property
    def name(self) -> str:
        return "write_file"

    @property
    def description(self) -> str:
        return "Write content to a file. Creates new file or overwrites existing file."

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Absolute or relative path to the file to write"
                },
                "content": {
                    "type": "string",
                    "description": "Content to write to the file"
                }
            },
            "required": ["file_path", "content"]
        }

    @property
    def system_reminder(self) -> str:
        return """IMPORTANT: This tool OVERWRITES existing files. Always read the file first if you need to preserve existing content.
For editing existing files, read first, modify, then write back."""

    def execute(self, file_path: str, content: str) -> str:
        """
        Write content to file.

        Args:
            file_path: Path to file
            content: Content to write

        Returns:
            Success message

        Raises:
            RuntimeError: If write fails
        """
        path = Path(file_path)

        try:
            # Check if file exists before writing
            existed_before = path.exists()

            # Create parent directories if needed
            path.parent.mkdir(parents=True, exist_ok=True)

            # Write file with UTF-8 encoding
            path.write_text(content, encoding='utf-8')

            # Calculate file size
            size = len(content)
            lines = content.count('\n') + 1

            action = "Overwrote" if existed_before else "Created"
            return f"{action} file: {file_path}\nSize: {size} characters, {lines} lines"

        except Exception as e:
            raise RuntimeError(
                f"Error writing file '{file_path}': {str(e)}"
            )


class ListFilesTool(BaseTool):
    """List files and directories in a given path."""

    @property
    def name(self) -> str:
        return "list_files"

    @property
    def description(self) -> str:
        return "List files and directories in a given directory path"

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "directory": {
                    "type": "string",
                    "description": "Directory path to list (defaults to current directory)"
                },
                "pattern": {
                    "type": "string",
                    "description": "Optional glob pattern to filter files (e.g., '*.py', '**/*.txt')"
                }
            },
            "required": []
        }

    @property
    def system_reminder(self) -> str:
        return """Use glob patterns to filter files efficiently (e.g., '*.py' for Python files, '**/*.txt' for all text files recursively).
This is faster and more precise than listing all files and filtering manually."""

    def execute(self, directory: str = ".", pattern: str = None) -> str:
        """
        List files in directory.

        Args:
            directory: Directory path (default: current directory)
            pattern: Optional glob pattern

        Returns:
            Formatted list of files and directories

        Raises:
            FileNotFoundError: If directory doesn't exist
            RuntimeError: If listing fails
        """
        path = Path(directory)

        if not path.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")

        if not path.is_dir():
            raise ValueError(f"Not a directory: {directory}")

        try:
            if pattern:
                # Use glob pattern
                items = sorted(path.glob(pattern))
            else:
                # List all items
                items = sorted(path.iterdir())

            if not items:
                return f"Directory: {directory}\nNo files found" + (f" matching '{pattern}'" if pattern else "")

            # Format output
            lines = [f"Directory: {directory}"]
            if pattern:
                lines.append(f"Pattern: {pattern}")
            lines.append("="*60)

            for item in items:
                item_type = "[DIR]" if item.is_dir() else "[FILE]"
                rel_path = item.relative_to(path) if item.is_relative_to(path) else item
                lines.append(f"{item_type} {rel_path}")

            lines.append(f"\nTotal: {len(items)} items")

            return "\n".join(lines)

        except Exception as e:
            raise RuntimeError(
                f"Error listing directory '{directory}': {str(e)}"
            )


class SearchFilesTool(BaseTool):
    """Search for text patterns in files."""

    @property
    def name(self) -> str:
        return "search_files"

    @property
    def description(self) -> str:
        return "Search for a text pattern in files within a directory"

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "description": "Text pattern to search for"
                },
                "directory": {
                    "type": "string",
                    "description": "Directory to search in (defaults to current directory)"
                },
                "file_pattern": {
                    "type": "string",
                    "description": "Optional glob pattern to filter files (e.g., '*.py')"
                },
                "case_sensitive": {
                    "type": "boolean",
                    "description": "Whether search should be case-sensitive (default: False)"
                }
            },
            "required": ["pattern"]
        }

    @property
    def system_reminder(self) -> str:
        return """For large codebases, use file_pattern to limit search scope (e.g., '*.py' for Python files only).
This improves performance and reduces noise in results."""

    def execute(
        self,
        pattern: str,
        directory: str = ".",
        file_pattern: str = "*",
        case_sensitive: bool = False
    ) -> str:
        """
        Search for pattern in files.

        Args:
            pattern: Text to search for
            directory: Directory to search in
            file_pattern: Glob pattern for files to search
            case_sensitive: Case-sensitive search

        Returns:
            Search results with file paths and line numbers

        Raises:
            FileNotFoundError: If directory doesn't exist
            RuntimeError: If search fails
        """
        path = Path(directory)

        if not path.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")

        if not path.is_dir():
            raise ValueError(f"Not a directory: {directory}")

        # Prepare search pattern
        search_pattern = pattern if case_sensitive else pattern.lower()

        results = []
        files_searched = 0

        try:
            # Find matching files
            for file_path in path.rglob(file_pattern):
                if not file_path.is_file():
                    continue

                try:
                    content = file_path.read_text(encoding='utf-8')
                    files_searched += 1

                    # Search line by line
                    for line_num, line in enumerate(content.splitlines(), start=1):
                        search_line = line if case_sensitive else line.lower()

                        if search_pattern in search_line:
                            results.append({
                                "file": str(file_path.relative_to(path)),
                                "line": line_num,
                                "content": line.strip()
                            })

                except (UnicodeDecodeError, PermissionError):
                    # Skip binary files or files we can't read
                    continue

            # Format output
            if not results:
                return f"Pattern: '{pattern}'\nDirectory: {directory}\nFiles searched: {files_searched}\n\nNo matches found"

            lines = [
                f"Pattern: '{pattern}'",
                f"Directory: {directory}",
                f"Files searched: {files_searched}",
                "="*60,
                ""
            ]

            for result in results[:50]:  # Limit to first 50 results
                lines.append(f"{result['file']}:{result['line']}")
                lines.append(f"  {result['content']}")
                lines.append("")

            if len(results) > 50:
                lines.append(f"... and {len(results) - 50} more matches")

            lines.append(f"\nTotal matches: {len(results)}")

            return "\n".join(lines)

        except Exception as e:
            raise RuntimeError(
                f"Error searching files in '{directory}': {str(e)}"
            )
