"""
Simple Chat Example - SimpleAgent Wrapper

Demonstrates using the SimpleAgent class with:
- Single-turn task execution (run)
- Multi-turn conversations (chat)
- Beautiful rich console output
- Error handling
"""

from simple_agent import SimpleAgent
from rich.console import Console
from rich.panel import Panel

console = Console()


def example_single_turn():
    """Example 1: Single-turn task execution."""
    console.print(Panel(
        "[bold]Example 1: Single-Turn Task Execution[/bold]\n"
        "The run() method executes a single task and returns the result.",
        border_style="blue"
    ))

    # Create agent (reads config from .env)
    agent = SimpleAgent()

    # Run a simple task
    result = agent.run("Explain what you are in one sentence.")

    # Result information is already displayed by agent with rich formatting
    console.print(f"\n[green]Task completed successfully: {result['success']}[/green]\n")


def example_multi_turn():
    """Example 2: Multi-turn conversation."""
    console.print(Panel(
        "[bold]Example 2: Multi-Turn Conversation[/bold]\n"
        "The chat() method maintains conversation context across multiple turns.",
        border_style="blue"
    ))

    # Create fresh agent with custom system prompt
    agent = SimpleAgent(
        system_prompt="You are a helpful math tutor. Be concise."
    )

    # Have a conversation (context is maintained)
    questions = [
        "What is 2+2?",
        "What about 3+3?",
        "Add those two results together."
    ]

    for question in questions:
        console.print(f"\n[bold cyan]User:[/bold cyan] {question}")
        response = agent.chat(question)
        console.print(f"[bold green]Agent:[/bold green] {response}")

    console.print(f"\n[green]Conversation completed![/green]\n")


def example_reset():
    """Example 3: Resetting conversation."""
    console.print(Panel(
        "[bold]Example 3: Resetting Conversation[/bold]\n"
        "The reset() method clears conversation history.",
        border_style="blue"
    ))

    agent = SimpleAgent()

    # First conversation
    console.print(f"\n[bold cyan]User:[/bold cyan] My favorite color is blue.")
    response1 = agent.chat("My favorite color is blue.")
    console.print(f"[bold green]Agent:[/bold green] {response1}")

    console.print(f"\n[bold cyan]User:[/bold cyan] What is my favorite color?")
    response2 = agent.chat("What is my favorite color?")
    console.print(f"[bold green]Agent:[/bold green] {response2}")

    # Reset and ask again
    console.print(f"\n[yellow]--- Resetting conversation ---[/yellow]\n")
    agent.reset()

    console.print(f"[bold cyan]User:[/bold cyan] What is my favorite color?")
    response3 = agent.chat("What is my favorite color?")
    console.print(f"[bold green]Agent:[/bold green] {response3}")

    console.print(f"\n[green]Reset example completed![/green]\n")


def example_configurable_timeout():
    """Example 4: Configurable timeout."""
    console.print(Panel(
        "[bold]Example 4: Configurable Timeout[/bold]\n"
        "You can configure request timeout when creating the agent.",
        border_style="blue"
    ))

    # Create agent with custom timeout
    agent = SimpleAgent(timeout=60)  # 60 second timeout

    result = agent.run("List 3 programming languages and describe each in one sentence.")

    console.print(f"\n[green]Completed with custom timeout (60s)[/green]\n")


def main():
    """Run all examples."""
    console.print("\n")
    console.print(Panel.fit(
        "[bold cyan]SimpleAgent Examples[/bold cyan]\n"
        "Demonstrating single-turn tasks, multi-turn chat, and features",
        border_style="cyan"
    ))
    console.print("\n")

    # Run examples
    example_single_turn()
    console.print("\n" + "="*60 + "\n")

    example_multi_turn()
    console.print("\n" + "="*60 + "\n")

    example_reset()
    console.print("\n" + "="*60 + "\n")

    example_configurable_timeout()
    console.print("\n" + "="*60 + "\n")

    console.print(Panel(
        "[bold green]All examples completed successfully![/bold green]",
        border_style="green"
    ))


if __name__ == "__main__":
    main()
