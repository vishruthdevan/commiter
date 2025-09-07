"""Interactive CLI functionality for commit message selection."""

from typing import List, Optional
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.text import Text
from rich.table import Table

console = Console()


def display_commit_choices(messages: List[str]) -> int:
    """
    Display commit message choices and return the selected index.
    
    Args:
        messages: List of commit message options
        
    Returns:
        Index of selected message (0-based)
    """
    console.print("\n[bold blue]Choose a commit message:[/bold blue]\n")
    
    # Create a table for better formatting
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Option", style="cyan", width=6)
    table.add_column("Message", style="white")
    
    for i, message in enumerate(messages, 1):
        table.add_row(str(i), message)
    
    console.print(table)
    
    # Get user choice
    while True:
        try:
            choice = Prompt.ask(
                f"\n[bold]Select option (1-{len(messages)})",
                default="1"
            )
            
            choice_num = int(choice)
            if 1 <= choice_num <= len(messages):
                return choice_num - 1  # Convert to 0-based index
            else:
                console.print(f"[red]Please enter a number between 1 and {len(messages)}[/red]")
        except ValueError:
            console.print("[red]Please enter a valid number[/red]")


def display_git_status() -> None:
    """Display current git status for context."""
    import subprocess
    
    try:
        # Get staged files
        result = subprocess.run(
            ["git", "status", "--porcelain", "--cached"],
            capture_output=True,
            text=True,
            check=True
        )
        
        staged_files = []
        for line in result.stdout.strip().split('\n'):
            if line and line[0] in 'AMDR':
                status = line[0]
                filename = line[3:].strip()
                staged_files.append((status, filename))
        
        if staged_files:
            console.print("\n[bold green]Staged changes:[/bold green]")
            for status, filename in staged_files:
                status_color = {
                    'A': 'green',
                    'M': 'yellow', 
                    'D': 'red',
                    'R': 'blue'
                }.get(status, 'white')
                
                status_symbol = {
                    'A': '+',
                    'M': '~',
                    'D': '-',
                    'R': '→'
                }.get(status, '?')
                
                console.print(f"  [{status_color}]{status_symbol}[/{status_color}] {filename}")
        else:
            console.print("\n[yellow]No staged changes found[/yellow]")
            
    except subprocess.CalledProcessError:
        console.print("[red]Error getting git status[/red]")
    except FileNotFoundError:
        console.print("[red]Git not found[/red]")


def confirm_commit(message: str) -> bool:
    """Ask user to confirm the commit with the selected message."""
    console.print(f"\n[bold]Commit message:[/bold]")
    console.print(Panel(message, border_style="blue"))
    
    return Confirm.ask("\n[bold]Proceed with this commit message?")


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
