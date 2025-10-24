"""
End-to-End Integration Test for Skills System with Real LLM

This script tests the complete skills workflow:
1. Agent initialization with skills
2. Tier 1 metadata in system prompt
3. LLM recognizing and loading skills
4. Tier 2 content delivery
5. Complete task execution

Run this to verify the skills system works with a real LLM.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from simple_agent import SimpleAgent
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()


def print_section(title: str):
    """Print a section header."""
    console.print(f"\n[bold blue]=== {title} ===[/bold blue]\n")


def test_skills_initialization():
    """Test 1: Skills system initializes correctly."""
    print_section("Test 1: Skills System Initialization")

    try:
        agent = SimpleAgent()

        if agent.skill_registry:
            skill_count = agent.skill_registry.count_total()
            console.print(f"[green]SUCCESS:[/green] Skills system initialized")
            console.print(f"  Skills found: {skill_count}")

            if skill_count > 0:
                skills = agent.skill_registry.list_skills()
                console.print("\n  Available skills:")
                for skill in skills:
                    console.print(f"    - {skill.name}: {skill.description}")
                return True
            else:
                console.print("[yellow]No skills found in skills/ directory[/yellow]")
                return False
        else:
            console.print("[red]FAILED:[/red] Skills system not initialized")
            return False

    except Exception as e:
        console.print(f"[red]ERROR:[/red] {e}")
        return False


def test_tier1_prompt():
    """Test 2: Tier 1 metadata appears in system prompt."""
    print_section("Test 2: Tier 1 Prompt Injection")

    try:
        agent = SimpleAgent()

        if "Available skills:" in agent.system_prompt:
            console.print("[green]SUCCESS:[/green] Tier 1 metadata injected into system prompt")
            console.print("\nSystem prompt excerpt:")
            # Show last 500 chars which should contain the skills section
            excerpt = agent.system_prompt[-500:]
            console.print(Panel(excerpt, title="System Prompt (excerpt)", border_style="cyan"))
            return True
        else:
            console.print("[yellow]WARNING:[/yellow] No skills metadata in system prompt")
            console.print("This is expected if no skills are available")
            return False

    except Exception as e:
        console.print(f"[red]ERROR:[/red] {e}")
        return False


def test_load_skill_tool():
    """Test 3: load_skill tool is registered."""
    print_section("Test 3: LoadSkillTool Registration")

    try:
        agent = SimpleAgent()

        if agent.tool_registry:
            tools = agent.tool_registry.get_definitions()
            tool_names = [tool["function"]["name"] for tool in tools] if tools else []

            if "load_skill" in tool_names:
                console.print("[green]SUCCESS:[/green] load_skill tool is registered")
                console.print(f"\nTotal tools available: {len(tool_names)}")
                console.print(f"Tools: {', '.join(tool_names)}")
                return True
            else:
                console.print("[yellow]WARNING:[/yellow] load_skill tool not found")
                console.print(f"Available tools: {tool_names}")
                return False
        else:
            console.print("[yellow]WARNING:[/yellow] No tool registry available")
            return False

    except Exception as e:
        console.print(f"[red]ERROR:[/red] {e}")
        return False


def test_with_real_llm():
    """Test 4: Real LLM interaction with skills."""
    print_section("Test 4: Real LLM Integration Test")

    # Check if running in non-interactive mode
    import sys
    if not sys.stdin.isatty():
        console.print("[yellow]SKIPPED:[/yellow] Non-interactive environment detected")
        console.print("Run manually to test real LLM integration:")
        console.print("  [cyan]uv run python examples/test_skills_e2e.py --llm[/cyan]")
        return None

    console.print("[yellow]This test makes a real API call to the LLM[/yellow]")
    console.print("Press Enter to continue, or Ctrl+C to skip...")
    try:
        input()
    except (KeyboardInterrupt, EOFError):
        console.print("\n[yellow]Skipped[/yellow]")
        return None

    try:
        agent = SimpleAgent()

        if not agent.skill_registry or agent.skill_registry.count_total() == 0:
            console.print("[yellow]SKIPPED:[/yellow] No skills available for testing")
            return None

        # Get first skill name for testing
        skills = agent.skill_registry.list_skills()
        test_skill_name = skills[0].name

        console.print(f"\nAsking LLM to use skill: [cyan]{test_skill_name}[/cyan]")

        # Create a task that should trigger skill loading
        task = f"Please load the {test_skill_name} skill and tell me what it does."

        console.print(f"\n[bold]Task:[/bold] {task}\n")

        # Run the agent
        result = agent.run(task)

        if result['success']:
            console.print(f"\n[green]SUCCESS:[/green] Agent completed task")
            console.print(f"Iterations: {result['iterations']}")
            console.print(f"Total tokens: {result['usage']['total_tokens']}")

            # Check if skill was loaded
            if agent.skill_registry.is_loaded(test_skill_name):
                console.print(f"\n[green]VERIFIED:[/green] Skill '{test_skill_name}' was loaded (Tier 2)")
            else:
                console.print(f"\n[yellow]NOTE:[/yellow] Skill '{test_skill_name}' was not loaded")
                console.print("LLM may have decided it wasn't necessary")

            return True
        else:
            console.print(f"[red]FAILED:[/red] Agent did not complete task")
            console.print(f"Error: {result.get('error', 'Unknown error')}")
            return False

    except Exception as e:
        console.print(f"[red]ERROR:[/red] {e}")
        import traceback
        console.print(traceback.format_exc())
        return False


def test_skill_content_loading():
    """Test 5: Manually verify skill content loading."""
    print_section("Test 5: Skill Content Loading (Manual)")

    try:
        agent = SimpleAgent()

        if not agent.skill_registry or agent.skill_registry.count_total() == 0:
            console.print("[yellow]SKIPPED:[/yellow] No skills available")
            return None

        skills = agent.skill_registry.list_skills()
        test_skill = skills[0]

        console.print(f"Testing skill: [cyan]{test_skill.name}[/cyan]")

        # Read the skill content directly
        skill_path = test_skill.skill_path
        if skill_path.exists():
            content = skill_path.read_text(encoding='utf-8')
            console.print(f"\n[green]SUCCESS:[/green] Skill file readable")
            console.print(f"Skill path: {skill_path}")
            console.print(f"Content length: {len(content)} characters")

            # Show first 300 chars
            console.print("\nSkill content preview:")
            console.print(Panel(content[:300] + "...", title="SKILL.md Preview", border_style="green"))

            return True
        else:
            console.print(f"[red]FAILED:[/red] Skill file not found at {skill_path}")
            return False

    except Exception as e:
        console.print(f"[red]ERROR:[/red] {e}")
        return False


def main():
    """Run all integration tests."""
    console.print(Panel(
        "[bold cyan]Skills System End-to-End Integration Test[/bold cyan]\n\n"
        "This script tests the complete skills workflow with a real LLM.",
        title="Simple Agent - Skills E2E Test",
        border_style="cyan"
    ))

    # Run all tests
    results = {}
    results["initialization"] = test_skills_initialization()
    results["tier1_prompt"] = test_tier1_prompt()
    results["load_skill_tool"] = test_load_skill_tool()
    results["skill_content"] = test_skill_content_loading()
    results["real_llm"] = test_with_real_llm()

    # Summary
    print_section("Test Summary")

    passed = sum(1 for v in results.values() if v is True)
    failed = sum(1 for v in results.values() if v is False)
    skipped = sum(1 for v in results.values() if v is None)

    console.print(f"[green]Passed:[/green]  {passed}")
    console.print(f"[red]Failed:[/red]   {failed}")
    console.print(f"[yellow]Skipped:[/yellow] {skipped}")

    # Detailed results
    console.print("\nDetailed Results:")
    for test_name, result in results.items():
        if result is True:
            status = "[green]PASS[/green]"
        elif result is False:
            status = "[red]FAIL[/red]"
        else:
            status = "[yellow]SKIP[/yellow]"
        console.print(f"  {status} - {test_name}")

    # Final verdict
    if failed == 0:
        console.print(f"\n[bold green]All tests passed![/bold green]")
        return 0
    else:
        console.print(f"\n[bold red]{failed} test(s) failed[/bold red]")
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        console.print("\n[yellow]Tests interrupted by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"\n[red]Fatal error:[/red] {e}")
        import traceback
        console.print(traceback.format_exc())
        sys.exit(1)
