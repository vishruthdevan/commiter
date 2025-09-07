"""Main CLI application for commiter."""

import sys
from typing import List, Optional
import typer

from .commands import CommitCommand, ConfigCommand


def commit(
    interactive: bool = typer.Option(
        False, "--interactive", "-i", 
        help="Use interactive mode to choose from multiple commit message options"
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
    
    By default, this tool auto-commits with the first generated message.
    Use --interactive to choose from multiple options or --custom to enter your own.
    """
    commit_command = CommitCommand()
    returncode = commit_command.execute(interactive, custom, git_args)
    raise typer.Exit(returncode)


def config(
    key: Optional[str] = typer.Argument(
        None,
        help="Configuration key to set (e.g., interactive_mode, max_choices, llm_provider, llm_model, llm_base_url)"
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
        commit config interactive_mode true
        commit config max_choices 5
        commit config llm_model llama3.2
        commit config llm_base_url http://localhost:11434
        commit config --show
    """
    config_command = ConfigCommand()
    returncode = config_command.execute(key, value, show)
    raise typer.Exit(returncode)


# Create the main app
app = typer.Typer(
    name="commiter",
    help="A CLI tool that provides AI-generated commit messages for git",
    add_completion=False,
    no_args_is_help=True,
)

# Add config as a subcommand
app.command(name="config")(config)

# Add commit as a subcommand for explicit commit behavior
app.command(name="commit")(commit)


if __name__ == "__main__":
    app()