"""
Tool Demo - Demonstrating SimpleAgent with File Tools

This example shows how to use SimpleAgent with tool calling capabilities.
The agent can read, write, list, and search files using the file tools.
"""

from simple_agent import SimpleAgent
from simple_agent.tools import (
    ToolRegistry,
    ReadFileTool,
    WriteFileTool,
    ListFilesTool,
    SearchFilesTool
)
from rich.console import Console
from rich.panel import Panel

console = Console()


def setup_agent_with_tools():
    """Create an agent with file manipulation tools."""
    # Create tool registry
    registry = ToolRegistry()

    # Register file tools
    registry.register_multiple([
        ReadFileTool(),
        WriteFileTool(),
        ListFilesTool(),
        SearchFilesTool()
    ])

    console.print("\n[dim]" + registry.get_tools_summary() + "[/dim]\n")

    # Create agent with tools
    agent = SimpleAgent(tool_registry=registry)

    return agent


def example_write_and_read():
    """Example 1: Write a file and then read it back."""
    console.print(Panel(
        "[bold]Example 1: Write and Read File[/bold]\n"
        "The agent will create a file and read it back.",
        border_style="blue"
    ))

    agent = setup_agent_with_tools()

    result = agent.run(
        "Create a file called 'test_example.txt' with the content 'Hello from SimpleAgent!' "
        "and then read it back to verify it was created correctly."
    )

    console.print(f"\n[green]Success: {result['success']}[/green]")
    console.print(f"[cyan]Iterations: {result['iterations']}[/cyan]\n")


def example_list_files():
    """Example 2: List files in a directory."""
    console.print(Panel(
        "[bold]Example 2: List Files[/bold]\n"
        "The agent will list Python files in the examples directory.",
        border_style="blue"
    ))

    agent = setup_agent_with_tools()

    result = agent.run(
        "List all Python files in the 'examples' directory using a pattern match."
    )

    console.print(f"\n[green]Success: {result['success']}[/green]")
    console.print(f"[cyan]Iterations: {result['iterations']}[/cyan]\n")


def example_search_files():
    """Example 3: Search for text in files."""
    console.print(Panel(
        "[bold]Example 3: Search Files[/bold]\n"
        "The agent will search for 'SimpleAgent' in Python files.",
        border_style="blue"
    ))

    agent = setup_agent_with_tools()

    result = agent.run(
        "Search for the text 'SimpleAgent' in all Python files in the 'src' directory. "
        "Show me the first few matches."
    )

    console.print(f"\n[green]Success: {result['success']}[/green]")
    console.print(f"[cyan]Iterations: {result['iterations']}[/cyan]\n")


def example_multi_step_task():
    """Example 4: Multi-step task requiring multiple tool calls."""
    console.print(Panel(
        "[bold]Example 4: Multi-Step Task[/bold]\n"
        "The agent will perform multiple operations to complete a complex task.",
        border_style="blue"
    ))

    agent = setup_agent_with_tools()

    result = agent.run(
        "Create a file called 'task_list.txt' with three TODO items. "
        "Then read the file back and count how many tasks are in it."
    )

    console.print(f"\n[green]Success: {result['success']}[/green]")
    console.print(f"[cyan]Iterations: {result['iterations']}[/cyan]\n")


def example_error_handling():
    """Example 5: Error handling when file doesn't exist."""
    console.print(Panel(
        "[bold]Example 5: Error Handling[/bold]\n"
        "The agent will handle errors gracefully when a file doesn't exist.",
        border_style="blue"
    ))

    agent = setup_agent_with_tools()

    result = agent.run(
        "Try to read the file 'nonexistent_file.txt'. If it doesn't exist, "
        "create it with some sample content and then read it."
    )

    console.print(f"\n[green]Success: {result['success']}[/green]")
    console.print(f"[cyan]Iterations: {result['iterations']}[/cyan]\n")


def main():
    """Run all tool demonstrations."""
    console.print("\n")
    console.print(Panel.fit(
        "[bold cyan]SimpleAgent Tool Calling Demo[/bold cyan]\n"
        "Demonstrating file manipulation with tools",
        border_style="cyan"
    ))
    console.print("\n")

    # Run examples
    example_write_and_read()
    console.print("\n" + "="*80 + "\n")

    example_list_files()
    console.print("\n" + "="*80 + "\n")

    example_search_files()
    console.print("\n" + "="*80 + "\n")

    example_multi_step_task()
    console.print("\n" + "="*80 + "\n")

    example_error_handling()
    console.print("\n" + "="*80 + "\n")

    console.print(Panel(
        "[bold green]All examples completed![/bold green]\n"
        "The agent successfully used tools to complete various file operations.",
        border_style="green"
    ))


if __name__ == "__main__":
    main()
