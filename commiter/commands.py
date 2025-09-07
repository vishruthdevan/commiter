"""CLI commands component for commiter."""

from typing import List, Optional

from rich.console import Console
from rich.panel import Panel

from .config import config_manager
from .git_operations import GitOperations
from .interactive import (
    ask_for_custom_message,
    confirm_commit,
    display_commit_choices,
    display_git_status,
)
from .llm_provider import LLMProvider

console = Console()


class CommitCommand:
    """Main commit command handler."""

    def __init__(self):
        self.git_ops = GitOperations()
        self.config = config_manager.get_config()
        self.llm = LLMProvider(
            provider=self.config.llm_provider,
            model=self.config.llm_model,
            base_url=self.config.llm_base_url,
        )

    def execute(
        self,
        interactive: bool = False,
        custom: bool = False,
        git_args: Optional[List[str]] = None,
    ) -> int:
        """Execute the commit command with given options."""

        # Handle None git_args
        if git_args is None:
            git_args = []

        # Validate git environment
        is_valid, error_msg = self.git_ops.validate_git_environment()
        if not is_valid:
            console.print(f"[red]Error: {error_msg}[/red]")
            return 1

        # Load fresh configuration
        self.config = config_manager.get_config()

        # Determine behavior based on flags
        if custom:
            return self._handle_custom_commit(git_args)
        elif interactive:
            return self._handle_interactive_commit(git_args)
        else:
            # Default behavior: auto-commit with first generated message
            return self._handle_auto_commit(git_args)

    def _handle_custom_commit(self, git_args: List[str]) -> int:
        """Handle custom commit message input."""
        message = ask_for_custom_message()
        if not message:
            console.print("[yellow]No message provided, aborting commit[/yellow]")
            return 0

        if confirm_commit(message):
            return self._execute_commit(message, git_args)
        else:
            console.print("[yellow]Commit cancelled[/yellow]")
            return 0

    def _handle_auto_commit(self, git_args: List[str]) -> int:
        """Handle auto-commit with first generated message."""
        # Show current status similar to interactive mode
        display_git_status()

        messages = self._generate_commit_messages(1)
        if not messages:
            console.print("[red]Failed to generate commit messages[/red]")
            return 1

        message = messages[0]
        # Display auto mode banner and the selected message in panels
        console.print(
            Panel.fit(
                "Auto mode: committing with the first generated message",
                title="Auto commit",
                border_style="blue",
            )
        )

        console.print(Panel.fit(message, border_style="blue", title="Commit message"))
        return self._execute_commit(message, git_args)

    def _handle_interactive_commit(self, git_args: List[str]) -> int:
        """Handle interactive commit message selection."""
        display_git_status()

        # Generate commit message options
        messages = self._generate_commit_messages(self.config.max_choices)

        if not messages:
            console.print("[red]Failed to generate commit messages[/red]")
            return 1

        # Display choices and get selection
        choice_idx = display_commit_choices(messages)
        selected_message = messages[choice_idx]

        # Confirm commit
        if confirm_commit(selected_message):
            return self._execute_commit(selected_message, git_args)
        else:
            console.print("[yellow]Commit cancelled[/yellow]")
            return 0

    def _generate_commit_messages(self, max_choices: int) -> List[str]:
        """Generate commit messages using the LLM provider."""
        try:
            # Get diff content
            diff_content = self.git_ops.get_diff_content()
            if not diff_content:
                console.print("[yellow]No staged changes found[/yellow]")
                return []

            # Generate messages using LLM with a spinner/status
            with console.status(
                "[bold blue]Generating commit message options...[/bold blue]",
                spinner="dots",
            ):
                messages = self.llm.generate_commit_messages(diff_content, max_choices)
            return messages

        except Exception as e:
            console.print(f"[red]Error generating commit messages: {e}[/red]")
            return []

    def _execute_commit(self, message: str, git_args: List[str]) -> int:
        """Execute the git commit command."""
        returncode, output = self.git_ops.commit(message, git_args)

        if returncode == 0:
            console.print("[green]✓ Commit successful![/green]")
            if output:
                console.print(output)
        else:
            console.print(f"[red]{output}[/red]")

        return returncode


class ConfigCommand:
    """Config command handler."""

    def execute(
        self, key: Optional[str] = None, value: Optional[str] = None, show: bool = False
    ) -> int:
        """Execute the config command."""

        if show:
            self._show_config()
            return 0

        if not key or not value:
            console.print("[red]Error: Both key and value are required[/red]")
            console.print("Usage: commit config <key> <value>")
            console.print("Example: commit config auto_commit true")
            return 1

        # Parse and validate the configuration
        updates = self._parse_config_update(key, value)
        if updates is None:
            return 1

        # Update configuration
        config_manager.update_config(**updates)
        console.print(f"[green]Configuration updated: {key} = {value}[/green]")
        return 0

    def _show_config(self):
        """Show current configuration."""
        config = config_manager.get_config()
        console.print("\n[bold blue]Current Configuration:[/bold blue]")
        console.print("  Default Mode: Auto-commit (use --interactive for choice mode)")
        console.print(f"  Max Choices: {config.max_choices}")
        console.print(f"  LLM Provider: {config.llm_provider}")
        console.print(f"  LLM Model: {config.llm_model}")
        console.print(f"  LLM Base URL: {config.llm_base_url}")

    def _parse_config_update(self, key: str, value: str) -> Optional[dict]:
        """Parse and validate configuration update."""
        updates = {}

        if key == "interactive_mode":
            if value.lower() in ("true", "1", "yes", "on"):
                updates["interactive_mode"] = True
            elif value.lower() in ("false", "0", "no", "off"):
                updates["interactive_mode"] = False
            else:
                console.print(
                    f"[red]Error: Invalid value for interactive_mode: {value}[/red]"
                )
                console.print("Valid values: true, false, 1, 0, yes, no, on, off")
                return None

        elif key == "max_choices":
            try:
                updates["max_choices"] = int(value)
                if updates["max_choices"] < 1:
                    console.print("[red]Error: max_choices must be at least 1[/red]")
                    return None
            except ValueError:
                console.print(
                    f"[red]Error: Invalid value for max_choices: {value}[/red]"
                )
                console.print("max_choices must be a positive integer")
                return None

        elif key == "llm_provider":
            if value.lower() in ("ollama", "openai", "anthropic"):
                updates["llm_provider"] = value.lower()
            else:
                console.print(
                    f"[red]Error: Invalid value for llm_provider: {value}[/red]"
                )
                console.print("Valid values: ollama, openai, anthropic")
                return None

        elif key == "llm_model":
            updates["llm_model"] = value

        elif key == "llm_base_url":
            updates["llm_base_url"] = value

        else:
            console.print(f"[red]Error: Unknown configuration key: {key}[/red]")
            console.print(
                "Valid keys: interactive_mode, max_choices, llm_provider, llm_model, llm_base_url"
            )
            return None

        return updates
