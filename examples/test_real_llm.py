"""
Simple manual test to verify skills work with real LLM.

This script demonstrates:
1. Agent initialization with skills
2. Asking LLM to load a skill
3. Verifying the skill is loaded and used

Run: uv run python examples/test_real_llm.py
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from simple_agent import SimpleAgent
from rich.console import Console

console = Console()

def main():
    console.print("[bold cyan]Simple Agent - Real LLM Skills Test[/bold cyan]\n")

    # Create agent with skills
    console.print("Initializing agent with skills...")
    agent = SimpleAgent()

    if not agent.skill_registry or agent.skill_registry.count_total() == 0:
        console.print("[yellow]No skills found. Please add skills to ./skills/ directory[/yellow]")
        return

    console.print(f"[green]Loaded {agent.skill_registry.count_total()} skill(s)[/green]\n")

    # Show available skills
    skills = agent.skill_registry.list_skills()
    console.print("[bold]Available skills:[/bold]")
    for skill in skills:
        console.print(f"  - {skill.name}: {skill.description}")

    # Test with first skill
    test_skill = skills[0].name
    console.print(f"\n[bold]Testing with skill:[/bold] {test_skill}\n")

    # Create a task that should trigger skill loading
    task = f"Please load the {test_skill} skill and explain what it does based on its content."

    console.print(f"[bold]Task:[/bold] {task}\n")
    console.print("[yellow]Calling LLM...[/yellow]\n")

    # Run the agent
    result = agent.run(task)

    if result['success']:
        console.print(f"\n[green]Task completed successfully![/green]")
        console.print(f"Iterations: {result['iterations']}")
        console.print(f"Tokens used: {result['usage']['total_tokens']}")

        # Check if skill was loaded
        if agent.skill_registry.is_loaded(test_skill):
            console.print(f"\n[bold green]VERIFIED:[/bold green] Skill '{test_skill}' was loaded (Tier 2 Progressive Disclosure)")
        else:
            console.print(f"\n[yellow]NOTE:[/yellow] Skill was not loaded - LLM decided it wasn't necessary")
    else:
        console.print(f"\n[red]Task failed[/red]")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error:[/red] {e}")
        import traceback
        console.print(traceback.format_exc())
