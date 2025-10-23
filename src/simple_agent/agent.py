"""
SimpleAgent - LLM Agent with Progressive Disclosure Architecture

Implements single-turn task execution and multi-turn chat.
Agent loop will be restored when tool calling support is added.
"""

import os
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
import litellm
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Load environment variables (automatically searches parent directories)
load_dotenv()

# Initialize rich console for beautiful output
console = Console()


class SimpleAgent:
    """
    Core agent that uses LiteLLM to accomplish tasks.

    Current Implementation:
    - Single-turn task execution with run()
    - Multi-turn conversations with chat()
    - Beautiful console output with Rich
    - Proper error handling and validation

    Future:
    - Tool calling support
    - Agent loop (Gather -> Act -> Verify -> Repeat)
    - Skills system for progressive disclosure
    """

    def __init__(
        self,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        system_prompt: Optional[str] = None,
        timeout: int = 30
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

        Raises:
            ValueError: If API key is not provided and not in environment

        Example:
            >>> agent = SimpleAgent()
            >>> result = agent.run("What is 2+2?")
            >>> print(result['result'])
        """
        # Get configuration from params or environment
        self.model = model or os.getenv("LITELLM_MODEL", "openrouter/anthropic/claude-haiku-4.5")
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.timeout = timeout

        if not self.api_key:
            raise ValueError(
                "API key is required. Provide via api_key parameter or OPENROUTER_API_KEY env var"
            )

        # Set default system prompt
        self.system_prompt = system_prompt or """You are a helpful AI assistant.
You accomplish tasks by thinking through them step by step.
Be concise and clear in your responses."""

        # Initialize conversation with system prompt
        self.conversation: List[Dict[str, str]] = [
            {"role": "system", "content": self.system_prompt}
        ]

    def run(self, task: str) -> Dict[str, Any]:
        """
        Run agent on a task (single-turn execution).

        This method resets the conversation and executes a single task.
        For multi-turn conversations, use chat() instead.

        Args:
            task: String describing what to do

        Returns:
            Dict with:
                - success: bool indicating if task completed
                - result: final response from agent
                - usage: dict with token counts (prompt, completion, total)

        Raises:
            ValueError: If task is empty or too long

        Example:
            >>> agent = SimpleAgent()
            >>> result = agent.run("Explain recursion briefly")
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

        try:
            # Call LiteLLM
            response = litellm.completion(
                model=self.model,
                messages=self.conversation,
                api_key=self.api_key,
                timeout=self.timeout
            )

            # Extract response content
            content = response.choices[0].message.content

            # Display response with rich (handles Unicode automatically)
            console.print("\n[bold green]Response:[/bold green]")
            console.print(content)

            # Display token usage
            usage = response.usage
            usage_table = Table(show_header=False, box=None)
            usage_table.add_row("[cyan]Prompt tokens:[/cyan]", str(usage.prompt_tokens))
            usage_table.add_row("[cyan]Completion tokens:[/cyan]", str(usage.completion_tokens))
            usage_table.add_row("[bold cyan]Total tokens:[/bold cyan]", f"[bold]{usage.total_tokens}[/bold]")
            console.print("\n", usage_table)

            return {
                "success": True,
                "result": content,
                "usage": {
                    "prompt_tokens": usage.prompt_tokens,
                    "completion_tokens": usage.completion_tokens,
                    "total_tokens": usage.total_tokens
                }
            }

        except litellm.exceptions.AuthenticationError as e:
            error_msg = "Authentication failed. Check your API key."
            console.print(f"\n[bold red]Error:[/bold red] {error_msg}", style="red")
            console.print(f"[dim]Details: {str(e)}[/dim]")
            return {
                "success": False,
                "result": error_msg,
                "error": str(e)
            }

        except litellm.exceptions.RateLimitError as e:
            error_msg = "Rate limit exceeded. Please wait and try again."
            console.print(f"\n[bold red]Error:[/bold red] {error_msg}", style="red")
            console.print(f"[dim]Details: {str(e)}[/dim]")
            return {
                "success": False,
                "result": error_msg,
                "error": str(e)
            }

        except litellm.exceptions.Timeout as e:
            error_msg = f"Request timed out after {self.timeout} seconds."
            console.print(f"\n[bold red]Error:[/bold red] {error_msg}", style="red")
            console.print(f"[dim]Details: {str(e)}[/dim]")
            return {
                "success": False,
                "result": error_msg,
                "error": str(e)
            }

        except litellm.exceptions.APIError as e:
            error_msg = "API error occurred."
            console.print(f"\n[bold red]Error:[/bold red] {error_msg}", style="red")
            console.print(f"[dim]Details: {str(e)}[/dim]")
            return {
                "success": False,
                "result": error_msg,
                "error": str(e)
            }

        except Exception as e:
            error_msg = "Unexpected error occurred."
            console.print(f"\n[bold red]Error:[/bold red] {error_msg}", style="red")
            console.print_exception(show_locals=False)
            return {
                "success": False,
                "result": error_msg,
                "error": str(e)
            }

    def chat(self, message: str) -> str:
        """
        Continue multi-turn conversation.

        This method maintains conversation history across calls.
        For single-turn tasks, use run() instead.

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
            # Get response
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
