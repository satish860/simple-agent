"""
Simple Tool Test - Quick test of tool calling functionality
"""

from simple_agent import SimpleAgent
from simple_agent.tools import (
    ToolRegistry,
    WriteFileTool,
    ReadFileTool
)

# Create tool registry
registry = ToolRegistry()
registry.register_multiple([
    WriteFileTool(),
    ReadFileTool()
])

# Create agent with tools
agent = SimpleAgent(tool_registry=registry)

# Test: Create a file and read it
result = agent.run(
    "Create a file called 'hello.txt' with the content 'Hello from SimpleAgent!' "
    "and then read it back to confirm."
)

print(f"\n\nFinal result:")
print(f"Success: {result['success']}")
print(f"Iterations: {result['iterations']}")
print(f"Total tokens: {result['usage']['total_tokens']}")
