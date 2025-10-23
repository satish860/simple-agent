"""
Tool Registry

Central management system for all agent tools.
Handles registration, schema generation, and execution.
"""

from typing import Dict, List, Any, Optional
from .base import BaseTool
from rich.console import Console

console = Console()


class ToolRegistry:
    """
    Central registry for managing agent tools.

    Responsibilities:
    - Register tools
    - Convert tools to LiteLLM format
    - Execute tools by name
    - Handle tool errors gracefully
    """

    def __init__(self):
        """Initialize empty tool registry."""
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        """
        Register a tool in the registry.

        Args:
            tool: BaseTool instance to register

        Raises:
            ValueError: If tool with same name already registered
        """
        if tool.name in self._tools:
            raise ValueError(f"Tool '{tool.name}' is already registered")

        self._tools[tool.name] = tool
        console.print(f"[dim]Registered tool: {tool.name}[/dim]")

    def register_multiple(self, tools: List[BaseTool]) -> None:
        """
        Register multiple tools at once.

        Args:
            tools: List of BaseTool instances

        Raises:
            ValueError: If any tool name is duplicate
        """
        for tool in tools:
            self.register(tool)

    def get_tool(self, name: str) -> Optional[BaseTool]:
        """
        Get a tool by name.

        Args:
            name: Tool name

        Returns:
            BaseTool instance or None if not found
        """
        return self._tools.get(name)

    def has_tool(self, name: str) -> bool:
        """
        Check if a tool is registered.

        Args:
            name: Tool name

        Returns:
            True if tool exists, False otherwise
        """
        return name in self._tools

    def list_tools(self) -> List[str]:
        """
        Get list of all registered tool names.

        Returns:
            List of tool names
        """
        return list(self._tools.keys())

    def get_definitions(self) -> List[Dict[str, Any]]:
        """
        Get all tool definitions in LiteLLM format.

        Returns:
            List of tool definitions suitable for litellm.completion(tools=...)
        """
        return [tool.to_openai_tool() for tool in self._tools.values()]

    def execute(self, name: str, arguments: Dict[str, Any]) -> str:
        """
        Execute a tool by name with given arguments.

        Args:
            name: Tool name
            arguments: Dictionary of tool arguments

        Returns:
            Tool execution result (formatted with system reminder if applicable)

        Raises:
            ValueError: If tool not found
            RuntimeError: If tool execution fails
        """
        tool = self.get_tool(name)

        if not tool:
            available = ", ".join(self.list_tools())
            raise ValueError(
                f"Tool '{name}' not found. Available tools: {available}"
            )

        try:
            # Execute tool
            result = tool.execute(**arguments)

            # Format with system reminder
            formatted_result = tool.format_result(result)

            return formatted_result

        except TypeError as e:
            # Invalid arguments
            raise ValueError(
                f"Invalid arguments for tool '{name}': {str(e)}"
            ) from e

        except Exception as e:
            # Tool execution error
            raise RuntimeError(
                f"Tool '{name}' execution failed: {str(e)}"
            ) from e

    def get_tools_summary(self) -> str:
        """
        Get human-readable summary of all registered tools.

        Returns:
            Formatted string listing all tools and their descriptions
        """
        if not self._tools:
            return "No tools registered"

        lines = ["Registered Tools:"]
        for tool in self._tools.values():
            approval = " [requires approval]" if tool.requires_approval else ""
            lines.append(f"  - {tool.name}{approval}: {tool.description}")

        return "\n".join(lines)

    def clear(self) -> None:
        """Remove all registered tools."""
        self._tools.clear()

    def __len__(self) -> int:
        """Return number of registered tools."""
        return len(self._tools)

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<ToolRegistry: {len(self)} tools registered>"
