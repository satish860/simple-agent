"""
SimpleAgent - LLM Agent with Progressive Disclosure Architecture

Implements agent loop with tool calling support:
Gather -> Act -> Verify -> Repeat
"""

import os
import json
from typing import Dict, Any, List, Optional
from pathlib import Path
from dotenv import load_dotenv
import litellm
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from .tools import ToolRegistry, LoadSkillTool
from .skills import (
    SkillPathResolver,
    SkillValidator,
    SkillLoader,
    SkillRegistry,
    PromptBuilder
)

# Load environment variables (automatically searches parent directories)
load_dotenv()

# Initialize rich console for beautiful output
console = Console()


class SimpleAgent:
    """
    Core agent that uses LiteLLM and tools to accomplish tasks.

    Features:
    - Single-turn task execution with run()
    - Multi-turn conversations with chat()
    - Tool calling support (file operations, search, etc.)
    - Agent loop: while(tool_calls) -> execute -> repeat
    - Beautiful console output with Rich
    - Proper error handling and validation

    Future:
    - Skills system for progressive disclosure
    - Sub-agent support via task tool
    """

    def __init__(
        self,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        system_prompt: Optional[str] = None,
        timeout: int = 30,
        tool_registry: Optional[ToolRegistry] = None,
        max_iterations: int = 15,
        skills_dir: Optional[str] = None,
        enable_skills: bool = True
    ):
        """
        Initialize SimpleAgent.

        Args:
            model: LiteLLM model identifier (e.g., "openrouter/anthropic/claude-haiku-4.5")
                   If not provided, reads from LITELLM_MODEL env var
            api_key: API key for the model provider
                     If not provided, reads from OPENROUTER_API_KEY env var
            system_prompt: Base system prompt for the agent
            timeout: Request timeout in seconds (default: 30)
            tool_registry: ToolRegistry with registered tools (optional)
            max_iterations: Maximum agent loop iterations (default: 15)
            skills_dir: Path to skills directory (optional, defaults to ./skills/ and ~/.simple-agent/skills/)
            enable_skills: Whether to enable skills system (default: True)

        Raises:
            ValueError: If API key is not provided and not in environment

        Example:
            >>> agent = SimpleAgent()
            >>> result = agent.run("What is 2+2?")
            >>> print(result['result'])

        Example with skills:
            >>> agent = SimpleAgent(skills_dir="./my-skills")
            >>> result = agent.run("Use the code-review skill to review my code")
        """
        # Get configuration from params or environment
        self.model = model or os.getenv("LITELLM_MODEL", "openrouter/anthropic/claude-haiku-4.5")
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.timeout = timeout
        self.max_iterations = max_iterations
        self.enable_skills = enable_skills

        if not self.api_key:
            raise ValueError(
                "API key is required. Provide via api_key parameter or OPENROUTER_API_KEY env var"
            )

        # Initialize skills system if enabled
        self.skill_registry = None
        if self.enable_skills:
            self.skill_registry = self._initialize_skills(skills_dir)

        # Initialize or augment tool registry
        if tool_registry is None:
            self.tool_registry = ToolRegistry()
        else:
            self.tool_registry = tool_registry

        # Register skills tool if skills are enabled
        if self.enable_skills and self.skill_registry:
            load_skill_tool = LoadSkillTool(registry=self.skill_registry)
            self.tool_registry.register(load_skill_tool)

        # Set default system prompt
        base_prompt = system_prompt or """You are a helpful AI assistant.
You accomplish tasks by thinking through them step by step.
When you have access to tools, use them to complete tasks more effectively.
Be concise and clear in your responses."""

        # Inject Tier 1 skills metadata if available
        if self.enable_skills and self.skill_registry:
            tier1_prompt = self._build_tier1_prompt()
            if tier1_prompt:
                self.system_prompt = f"{base_prompt}\n\n{tier1_prompt}"
            else:
                self.system_prompt = base_prompt
        else:
            self.system_prompt = base_prompt

        # Initialize conversation with system prompt
        self.conversation: List[Dict[str, Any]] = [
            {"role": "system", "content": self.system_prompt}
        ]

        # Track iteration count
        self.iteration = 0

    def _initialize_skills(self, skills_dir: Optional[str] = None) -> Optional[SkillRegistry]:
        """
        Initialize the skills system.

        Args:
            skills_dir: Optional explicit skills directory path

        Returns:
            SkillRegistry instance or None if initialization fails
        """
        try:
            # Setup skill path resolver
            explicit_paths = [skills_dir] if skills_dir else None
            path_resolver = SkillPathResolver(explicit_paths=explicit_paths)

            # Setup validator and loader
            validator = SkillValidator()
            loader = SkillLoader(path_resolver=path_resolver, validator=validator)

            # Create and return registry
            registry = SkillRegistry(skill_loader=loader)

            if registry.count_total() > 0:
                console.print(f"[cyan]Loaded {registry.count_total()} skill(s)[/cyan]")

            return registry

        except Exception as e:
            console.print(f"[yellow]Warning: Failed to initialize skills system: {e}[/yellow]")
            return None

    def _build_tier1_prompt(self) -> str:
        """
        Build Tier 1 system prompt with skill metadata.

        Returns:
            Tier 1 prompt string or empty string if no skills
        """
        if not self.skill_registry:
            return ""

        try:
            prompt_builder = PromptBuilder(registry=self.skill_registry)
            return prompt_builder.build_tier1_prompt()
        except Exception as e:
            console.print(f"[yellow]Warning: Failed to build skills prompt: {e}[/yellow]")
            return ""

    def run(self, task: str) -> Dict[str, Any]:
        """
        Run agent on a task with tool calling support.

        This method uses an agent loop:
        1. Send task to LLM with available tools
        2. If LLM returns tool calls, execute them
        3. Send tool results back to LLM
        4. Repeat until LLM completes without tool calls or max iterations reached

        Args:
            task: String describing what to do

        Returns:
            Dict with:
                - success: bool indicating if task completed
                - result: final response from agent
                - iterations: number of loop iterations used
                - usage: dict with total token counts

        Raises:
            ValueError: If task is empty or too long

        Example:
            >>> agent = SimpleAgent(tool_registry=registry)
            >>> result = agent.run("Read the file example.txt")
            >>> if result['success']:
            ...     print(result['result'])
        """
        # Validate input
        self._validate_input(task, "Task")

        # Display task in panel
        console.print(Panel(
            f"[bold cyan]{task}[/bold cyan]",
            title="[bold]SimpleAgent Task[/bold]",
            border_style="cyan"
        ))

        # Reset conversation for fresh task
        self.conversation = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": task}
        ]

        self.iteration = 0
        total_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

        # Get tool definitions if registry provided
        tools = self.tool_registry.get_definitions() if self.tool_registry else None

        # Agent loop: while(tool_calls) pattern
        while self.iteration < self.max_iterations:
            self.iteration += 1
            console.print(f"\n[dim]--- Iteration {self.iteration}/{self.max_iterations} ---[/dim]")

            try:
                # Call LiteLLM
                response = litellm.completion(
                    model=self.model,
                    messages=self.conversation,
                    api_key=self.api_key,
                    timeout=self.timeout,
                    tools=tools
                )

                # Track token usage
                usage = response.usage
                total_usage["prompt_tokens"] += usage.prompt_tokens
                total_usage["completion_tokens"] += usage.completion_tokens
                total_usage["total_tokens"] += usage.total_tokens

                # Extract response
                message = response.choices[0].message

                # Check if there are tool calls
                tool_calls = getattr(message, 'tool_calls', None)

                if not tool_calls:
                    # No tool calls - task complete
                    content = message.content

                    # Display final response
                    console.print("\n[bold green]Response:[/bold green]")
                    console.print(content)

                    # Display token usage
                    self._display_usage(total_usage)

                    console.print(f"\n[green]Task completed in {self.iteration} iteration(s)[/green]")

                    return {
                        "success": True,
                        "result": content,
                        "iterations": self.iteration,
                        "usage": total_usage
                    }

                # Tool calls exist - execute them
                console.print(f"\n[yellow]Tool calls: {len(tool_calls)}[/yellow]")

                # Add assistant message with tool calls to conversation
                self.conversation.append({
                    "role": "assistant",
                    "content": message.content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        }
                        for tc in tool_calls
                    ]
                })

                # Execute each tool call
                for tool_call in tool_calls:
                    tool_name = tool_call.function.name
                    tool_args_str = tool_call.function.arguments

                    # Parse arguments
                    try:
                        tool_args = json.loads(tool_args_str) if isinstance(tool_args_str, str) else tool_args_str
                    except json.JSONDecodeError:
                        tool_args = {}

                    console.print(f"  [cyan]→[/cyan] {tool_name}({', '.join(f'{k}={v}' for k, v in tool_args.items())})")

                    # Execute tool via registry
                    if not self.tool_registry:
                        tool_result = json.dumps({"error": "No tool registry available"})
                    else:
                        try:
                            tool_result = self.tool_registry.execute(tool_name, tool_args)
                        except Exception as e:
                            tool_result = json.dumps({"error": str(e)})
                            console.print(f"    [red]Error: {str(e)}[/red]")

                    # Add tool result to conversation
                    self.conversation.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_result
                    })

                # Continue loop - LLM will process tool results

            except litellm.exceptions.AuthenticationError as e:
                error_msg = "Authentication failed. Check your API key."
                console.print(f"\n[bold red]Error:[/bold red] {error_msg}", style="red")
                console.print(f"[dim]Details: {str(e)}[/dim]")
                return {
                    "success": False,
                    "result": error_msg,
                    "iterations": self.iteration,
                    "error": str(e)
                }

            except litellm.exceptions.RateLimitError as e:
                error_msg = "Rate limit exceeded. Please wait and try again."
                console.print(f"\n[bold red]Error:[/bold red] {error_msg}", style="red")
                console.print(f"[dim]Details: {str(e)}[/dim]")
                return {
                    "success": False,
                    "result": error_msg,
                    "iterations": self.iteration,
                    "error": str(e)
                }

            except litellm.exceptions.Timeout as e:
                error_msg = f"Request timed out after {self.timeout} seconds."
                console.print(f"\n[bold red]Error:[/bold red] {error_msg}", style="red")
                console.print(f"[dim]Details: {str(e)}[/dim]")
                return {
                    "success": False,
                    "result": error_msg,
                    "iterations": self.iteration,
                    "error": str(e)
                }

            except litellm.exceptions.APIError as e:
                error_msg = "API error occurred."
                console.print(f"\n[bold red]Error:[/bold red] {error_msg}", style="red")
                console.print(f"[dim]Details: {str(e)}[/dim]")
                return {
                    "success": False,
                    "result": error_msg,
                    "iterations": self.iteration,
                    "error": str(e)
                }

            except Exception as e:
                error_msg = "Unexpected error occurred."
                console.print(f"\n[bold red]Error:[/bold red] {error_msg}", style="red")
                console.print_exception(show_locals=False)
                return {
                    "success": False,
                    "result": error_msg,
                    "iterations": self.iteration,
                    "error": str(e)
                }

        # Max iterations reached
        console.print(f"\n[yellow]Max iterations ({self.max_iterations}) reached[/yellow]")
        return {
            "success": False,
            "result": "Task did not complete within maximum iterations",
            "iterations": self.iteration,
            "usage": total_usage
        }

    def chat(self, message: str) -> str:
        """
        Continue multi-turn conversation (no tool support).

        This method maintains conversation history across calls.
        For single-turn tasks with tools, use run() instead.

        Args:
            message: User message

        Returns:
            Assistant response as string

        Raises:
            ValueError: If message is empty or too long

        Example:
            >>> agent = SimpleAgent()
            >>> response1 = agent.chat("What is 2+2?")
            >>> response2 = agent.chat("What about 3+3?")
            >>> response3 = agent.chat("Add those results together")
        """
        # Validate input
        self._validate_input(message, "Message")

        # Add user message to conversation
        self.conversation.append({
            "role": "user",
            "content": message
        })

        try:
            # Get response (no tools in chat mode)
            response = litellm.completion(
                model=self.model,
                messages=self.conversation,
                api_key=self.api_key,
                timeout=self.timeout
            )

            content = response.choices[0].message.content

            # Add to conversation history
            self.conversation.append({
                "role": "assistant",
                "content": content
            })

            return content

        except litellm.exceptions.AuthenticationError as e:
            return f"Error: Authentication failed. Check your API key. ({str(e)})"

        except litellm.exceptions.RateLimitError as e:
            return f"Error: Rate limit exceeded. Please wait and try again. ({str(e)})"

        except litellm.exceptions.Timeout as e:
            return f"Error: Request timed out after {self.timeout} seconds. ({str(e)})"

        except litellm.exceptions.APIError as e:
            return f"Error: API error occurred. ({str(e)})"

        except Exception as e:
            return f"Error: Unexpected error occurred. ({str(e)})"

    def reset(self):
        """
        Reset conversation history to initial state.

        Clears all messages except the system prompt.
        Useful for starting fresh conversations without creating new agent.

        Example:
            >>> agent = SimpleAgent()
            >>> agent.chat("Hello")
            >>> agent.chat("What did I just say?")  # Remembers "Hello"
            >>> agent.reset()
            >>> agent.chat("What did I just say?")  # Doesn't remember
        """
        self.conversation = [
            {"role": "system", "content": self.system_prompt}
        ]
        self.iteration = 0

    def _validate_input(self, text: str, field_name: str):
        """
        Validate user input for safety and sanity.

        Args:
            text: Input text to validate
            field_name: Name of the field (for error messages)

        Raises:
            ValueError: If validation fails
        """
        if not text or not text.strip():
            raise ValueError(f"{field_name} cannot be empty")

        if len(text) > 50000:
            raise ValueError(
                f"{field_name} too long ({len(text)} chars). Maximum is 50,000 characters."
            )

    def _display_usage(self, usage: Dict[str, int]):
        """Display token usage statistics."""
        usage_table = Table(show_header=False, box=None)
        usage_table.add_row("[cyan]Prompt tokens:[/cyan]", str(usage["prompt_tokens"]))
        usage_table.add_row("[cyan]Completion tokens:[/cyan]", str(usage["completion_tokens"]))
        usage_table.add_row("[bold cyan]Total tokens:[/bold cyan]", f"[bold]{usage['total_tokens']}[/bold]")
        console.print("\n", usage_table)
