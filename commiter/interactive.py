"""Interactive CLI functionality for commit message selection."""

import textwrap
from typing import Any, List, Optional, cast

from InquirerPy import inquirer as _inquirer
from rich.box import ROUNDED
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table

from .git_operations import GitOperations

console = Console()
# Workaround for type-checkers: InquirerPy exposes dynamic factories like select()
inquirer = cast(Any, _inquirer)


def display_commit_choices(messages: List[str]) -> int:
    """
    Display commit message choices and return the selected index.

    Args:
        messages: List of commit message options

    Returns:
        Index of selected message (0-based)
    """
    console.print(
        Panel.fit(
            "Use arrow keys to navigate, Enter to select",
            title="Choose a commit message",
            border_style="blue",
        )
    )

    # Build choices for InquirerPy (truncate long lines nicely)
    choices = []
    for idx, msg in enumerate(messages):
        display = textwrap.shorten(
            msg, width=100, break_long_words=False, placeholder="…"
        )
        choices.append({"name": f"{idx + 1}. {display}", "value": idx})

    try:
        selected_index = inquirer.select(
            message="Select a commit message",
            choices=choices,
            default=0,
            instruction="Use ↑/↓ to navigate, Enter to select",
            pointer="❯",
            qmark="›",
            cycle=True,
            max_height=12,
        ).execute()
        return int(selected_index)
    except Exception:
        # Fallback to simple numeric input if InquirerPy fails
        table = Table(show_header=True, header_style="bold magenta", box=ROUNDED)
        table.add_column("Option", style="cyan", width=6)
        table.add_column("Message", style="white")
        for i, message in enumerate(messages, 1):
            table.add_row(str(i), message)
        console.print(table)

        while True:
            try:
                choice = Prompt.ask(
                    f"\n[bold]Select option (1-{len(messages)})", default="1"
                )
                choice_num = int(choice)
                if 1 <= choice_num <= len(messages):
                    return choice_num - 1
                else:
                    console.print(
                        f"[red]Please enter a number between 1 and {len(messages)}[/red]"
                    )
            except ValueError:
                console.print("[red]Please enter a valid number[/red]")


def display_git_status() -> None:
    """Display current git status for context."""
    import subprocess

    try:
        # Ensure we are in a git repository
        if not GitOperations.check_git_repo():
            console.print("[red]Not in a git repository[/red]")
            return

        # Use name-status for robust parsing of staged files
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-status"],
            capture_output=True,
            text=True,
            check=False,
        )

        staged_files = []
        for raw_line in result.stdout.strip().split("\n"):
            if not raw_line:
                continue
            parts = raw_line.split("\t")
            status_token = parts[0]
            status = status_token[0] if status_token else "?"
            filename = parts[-1].strip() if len(parts) >= 2 else ""
            if status in "AMDR" and filename:
                staged_files.append((status, filename))

        if result.returncode != 0 and not staged_files:
            err = result.stderr.strip() if result.stderr else ""
            console.print(
                f"[red]Error getting git status[/red]{f': {err}' if err else ''}"
            )
            return

        if staged_files:
            table = Table(show_header=True, header_style="bold magenta", box=ROUNDED)
            table.add_column("Status", style="cyan", width=8)
            table.add_column("File", style="white")

            for status, filename in staged_files:
                status_color = {
                    "A": "green",
                    "M": "yellow",
                    "D": "red",
                    "R": "blue",
                }.get(status, "white")

                status_symbol = {"A": "+", "M": "~", "D": "-", "R": "→"}.get(
                    status, "?"
                )

                table.add_row(
                    f"[{status_color}]{status_symbol}[/{status_color}] {status}",
                    filename,
                )

            console.print(
                Panel.fit(
                    table,
                    title=f"Staged changes ({len(staged_files)})",
                    border_style="green",
                )
            )
        else:
            console.print(
                Panel.fit(
                    "No staged changes found",
                    title="Staged changes",
                    border_style="yellow",
                )
            )

    except subprocess.CalledProcessError:
        console.print("[red]Error getting git status[/red]")
    except FileNotFoundError:
        console.print("[red]Git not found[/red]")


def confirm_commit(message: str) -> bool:
    """Ask user to confirm the commit with the selected message."""
    console.print("\n[bold]Commit message:[/bold]")
    console.print(Panel.fit(message, border_style="blue", title="Commit message"))

    return Confirm.ask("\n[bold]Proceed with this commit message?[/bold]", default=True)


def ask_for_custom_message() -> Optional[str]:
    """Ask user to enter a custom commit message."""
    console.print("\n[bold blue]Enter custom commit message:[/bold blue]")
    message = Prompt.ask("Message", default="")

    if not message.strip():
        console.print("[yellow]Empty message, skipping custom input[/yellow]")
        return None

    return message.strip()


def display_help() -> None:
    """Display help information."""
    help_text = """
[bold]Commiter CLI Help[/bold]

This tool helps you create git commits with AI-generated messages.

[bold]Usage:[/bold]
  commit [OPTIONS] [GIT_OPTIONS]

[bold]Options:[/bold]
  --interactive, -i    Use interactive mode (default)
  --auto, -a          Auto-commit with first generated message
  --custom, -c        Enter custom commit message
  --help, -h          Show this help message

[bold]Configuration:[/bold]
  The tool uses ~/.commiter/config.json for settings.
  
  You can modify:
  - interactive_mode: true/false
  - auto_commit: true/false  
  - max_choices: number of message options (default: 3)

[bold]Examples:[/bold]
  commit                    # Interactive mode
  commit --auto            # Auto-commit
  commit --custom          # Custom message
  commit --amend           # Pass --amend to git
  commit -m "message"      # Pass -m to git directly
"""

    console.print(Panel(help_text, title="Help", border_style="green"))
