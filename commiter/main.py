"""Main CLI application for commiter."""

import subprocess
import sys
from typing import List, Optional
import typer
from rich.console import Console

from .config import config_manager
from .commit_generator import generate_commit_messages, get_commit_message_from_user
from .interactive import (
    display_commit_choices, 
    display_git_status, 
    confirm_commit,
    ask_for_custom_message,
    display_help
)

console = Console()


def run_git_commit(message: str, git_args: List[str]) -> int:
    """Run git commit with the given message and arguments."""
    cmd = ["git", "commit", "-m", message] + git_args
    
    try:
        result = subprocess.run(cmd, check=True)
        return result.returncode
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Git commit failed: {e}[/red]")
        return e.returncode
    except FileNotFoundError:
        console.print("[red]Git not found. Please ensure git is installed.[/red]")
        return 1


def check_git_repo() -> bool:
    """Check if we're in a git repository."""
    try:
        subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            capture_output=True,
            check=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def check_staged_changes() -> bool:
    """Check if there are staged changes to commit."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            capture_output=True
        )
        return result.returncode != 0  # Non-zero means there are staged changes
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def main(
    interactive: bool = typer.Option(
        None, "--interactive", "-i", 
        help="Use interactive mode to choose commit message"
    ),
    auto: bool = typer.Option(
        False, "--auto", "-a",
        help="Auto-commit with the first generated message"
    ),
    custom: bool = typer.Option(
        False, "--custom", "-c",
        help="Enter a custom commit message"
    ),
    git_args: Optional[List[str]] = typer.Argument(
        default=None,
        help="Additional arguments to pass to git commit"
    )
):
    """
    A CLI tool that provides AI-generated commit messages for git.
    
    This tool acts as an alias to git commit but with AI-generated commit messages.
    You can choose from generated messages or provide your own.
    """
    
    # Handle None git_args
    if git_args is None:
        git_args = []
    
    # Check if we're in a git repository
    if not check_git_repo():
        console.print("[red]Error: Not in a git repository[/red]")
        console.print("Please run this command from within a git repository.")
        raise typer.Exit(1)
    
    # Check if there are staged changes
    if not check_staged_changes():
        console.print("[yellow]No staged changes found.[/yellow]")
        console.print("Use 'git add <file>' to stage changes before committing.")
        raise typer.Exit(0)
    
    # Load configuration
    config = config_manager.get_config()
    
    # Determine behavior based on flags and config
    if custom:
        # Custom message mode
        message = ask_for_custom_message()
        if not message:
            console.print("[yellow]No message provided, aborting commit[/yellow]")
            raise typer.Exit(0)
        
        if confirm_commit(message):
            returncode = run_git_commit(message, git_args)
            if returncode == 0:
                console.print("[green]✓ Commit successful![/green]")
            raise typer.Exit(returncode)
    
    elif auto or (interactive is False and config.auto_commit):
        # Auto-commit mode
        messages = generate_commit_messages(1)
        if messages:
            message = messages[0]
            console.print(f"[blue]Auto-committing with message: {message}[/blue]")
            returncode = run_git_commit(message, git_args)
            if returncode == 0:
                console.print("[green]✓ Commit successful![/green]")
            raise typer.Exit(returncode)
    
    else:
        # Interactive mode (default)
        display_git_status()
        
        # Generate commit message options
        messages = generate_commit_messages(config.max_choices)
        
        if not messages:
            console.print("[red]Failed to generate commit messages[/red]")
            raise typer.Exit(1)
        
        # Display choices and get selection
        choice_idx = display_commit_choices(messages)
        selected_message = messages[choice_idx]
        
        # Confirm commit
        if confirm_commit(selected_message):
            returncode = run_git_commit(selected_message, git_args)
            if returncode == 0:
                console.print("[green]✓ Commit successful![/green]")
            raise typer.Exit(returncode)
        else:
            console.print("[yellow]Commit cancelled[/yellow]")
            raise typer.Exit(0)


def config_cmd(
    key: Optional[str] = typer.Argument(
        None,
        help="Configuration key to set (e.g., auto_commit, interactive_mode, max_choices)"
    ),
    value: Optional[str] = typer.Argument(
        None,
        help="Value to set for the configuration key"
    ),
    show: bool = typer.Option(
        False, "--show", "-s",
        help="Show current configuration"
    )
):
    """Manage commiter configuration.
    
    Examples:
        commit config auto_commit true
        commit config interactive_mode false
        commit config max_choices 5
        commit config --show
    """
    
    if show:
        config = config_manager.get_config()
        console.print("\n[bold blue]Current Configuration:[/bold blue]")
        console.print(f"  Interactive Mode: {config.interactive_mode}")
        console.print(f"  Auto Commit: {config.auto_commit}")
        console.print(f"  Max Choices: {config.max_choices}")
        console.print(f"  AI Provider: {config.ai_provider}")
        console.print(f"  AI Model: {config.ai_model}")
        return
    
    if not key or not value:
        console.print("[red]Error: Both key and value are required[/red]")
        console.print("Usage: commit config <key> <value>")
        console.print("Example: commit config auto_commit true")
        raise typer.Exit(1)
    
    # Parse the value based on the key
    updates = {}
    
    if key == "auto_commit":
        if value.lower() in ("true", "1", "yes", "on"):
            updates['auto_commit'] = True
        elif value.lower() in ("false", "0", "no", "off"):
            updates['auto_commit'] = False
        else:
            console.print(f"[red]Error: Invalid value for auto_commit: {value}[/red]")
            console.print("Valid values: true, false, 1, 0, yes, no, on, off")
            raise typer.Exit(1)
    
    elif key == "interactive_mode":
        if value.lower() in ("true", "1", "yes", "on"):
            updates['interactive_mode'] = True
        elif value.lower() in ("false", "0", "no", "off"):
            updates['interactive_mode'] = False
        else:
            console.print(f"[red]Error: Invalid value for interactive_mode: {value}[/red]")
            console.print("Valid values: true, false, 1, 0, yes, no, on, off")
            raise typer.Exit(1)
    
    elif key == "max_choices":
        try:
            updates['max_choices'] = int(value)
            if updates['max_choices'] < 1:
                console.print("[red]Error: max_choices must be at least 1[/red]")
                raise typer.Exit(1)
        except ValueError:
            console.print(f"[red]Error: Invalid value for max_choices: {value}[/red]")
            console.print("max_choices must be a positive integer")
            raise typer.Exit(1)
    
    else:
        console.print(f"[red]Error: Unknown configuration key: {key}[/red]")
        console.print("Valid keys: auto_commit, interactive_mode, max_choices")
        raise typer.Exit(1)
    
    # Update configuration
    config_manager.update_config(**updates)
    console.print(f"[green]Configuration updated: {key} = {value}[/green]")


# Create the main app
app = typer.Typer(
    name="commit",
    help="A CLI tool that provides AI-generated commit messages for git",
    add_completion=False,
    no_args_is_help=False,
    invoke_without_command=True
)

# Add config as a subcommand
app.command(name="config")(config_cmd)

# Set main as the callback (default behavior)
app.callback()(main)

if __name__ == "__main__":
    app()