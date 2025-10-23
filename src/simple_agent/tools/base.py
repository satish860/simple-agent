"""
Base Tool Class

Defines the abstract interface that all tools must implement.
Inspired by Claude Code's tool architecture.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BaseTool(ABC):
    """
    Abstract base class for all agent tools.

    Each tool must define:
    - name: Unique tool identifier
    - description: What the tool does (shown to LLM)
    - parameters: JSON schema for tool arguments
    - execute(): Method that performs the tool's action

    Optional:
    - requires_approval: Whether tool needs user confirmation
    - system_reminder: Text added to tool result to reinforce behavior
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier for this tool."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Description of what this tool does (shown to LLM)."""
        pass

    @property
    @abstractmethod
    def parameters(self) -> Dict[str, Any]:
        """
        JSON Schema defining the tool's parameters.

        Example:
        {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the file"
                }
            },
            "required": ["file_path"]
        }
        """
        pass

    @property
    def requires_approval(self) -> bool:
        """
        Whether this tool requires user approval before execution.

        Default: False
        Override to True for dangerous operations (e.g., bash, file deletion)
        """
        return False

    @property
    def system_reminder(self) -> Optional[str]:
        """
        Optional reminder text appended to tool results.

        System reminders reinforce behavioral guidelines and are more
        effective than system-prompt-only approaches for long sessions.

        Default: None
        Override to provide tool-specific guidance.
        """
        return None

    @abstractmethod
    def execute(self, **kwargs) -> str:
        """
        Execute the tool with given arguments.

        Args:
            **kwargs: Tool parameters as defined in the parameters schema

        Returns:
            str: Tool execution result

        Raises:
            ValueError: If arguments are invalid
            RuntimeError: If execution fails
        """
        pass

    def to_openai_tool(self) -> Dict[str, Any]:
        """
        Convert tool definition to OpenAI/LiteLLM tool format.

        Returns:
            Dict in the format expected by LiteLLM:
            {
                "type": "function",
                "function": {
                    "name": "tool_name",
                    "description": "Tool description",
                    "parameters": {...}
                }
            }
        """
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }

    def format_result(self, result: str) -> str:
        """
        Format tool result with optional system reminder.

        Args:
            result: Raw tool execution result

        Returns:
            Formatted result with system reminder appended if defined
        """
        if self.system_reminder:
            return f"{result}\n\n<system-reminder>\n{self.system_reminder}\n</system-reminder>"
        return result

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<{self.__class__.__name__}: {self.name}>"
