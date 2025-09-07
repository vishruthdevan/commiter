"""Commit message generation functionality."""

import subprocess
from typing import List, Optional
from rich.console import Console

console = Console()


def get_git_diff() -> str:
    """Get the git diff for staged changes."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Error getting git diff: {e}[/red]")
        return ""
    except FileNotFoundError:
        console.print("[red]Git not found. Please ensure git is installed.[/red]")
        return ""


def get_git_status() -> str:
    """Get the git status for staged files."""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain", "--cached"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Error getting git status: {e}[/red]")
        return ""


def generate_commit_messages(count: int = 3) -> List[str]:
    """
    Generate commit messages based on staged changes.
    
    For now, this returns placeholder messages. In the future,
    this will integrate with AI services to generate actual messages.
    """
    diff = get_git_diff()
    status = get_git_status()
    
    if not diff and not status:
        return ["No staged changes found"]
    
    # Parse staged files from status
    staged_files = []
    for line in status.strip().split('\n'):
        if line and line[0] in 'AMDR':
            staged_files.append(line[3:].strip())
    
    # Generate placeholder messages based on file changes
    messages = []
    
    if staged_files:
        # Group files by type
        py_files = [f for f in staged_files if f.endswith('.py')]
        js_files = [f for f in staged_files if f.endswith(('.js', '.ts', '.jsx', '.tsx'))]
        config_files = [f for f in staged_files if f.endswith(('.json', '.yaml', '.yml', '.toml', '.ini'))]
        doc_files = [f for f in staged_files if f.endswith(('.md', '.txt', '.rst'))]
        
        # Generate messages based on file types
        if py_files:
            if len(py_files) == 1:
                messages.append(f"Update {py_files[0]}")
            else:
                messages.append(f"Update {len(py_files)} Python files")
        
        if js_files:
            if len(js_files) == 1:
                messages.append(f"Update {js_files[0]}")
            else:
                messages.append(f"Update {len(js_files)} JavaScript/TypeScript files")
        
        if config_files:
            messages.append(f"Update configuration files")
        
        if doc_files:
            messages.append(f"Update documentation")
        
        # Generic messages
        if len(staged_files) == 1:
            messages.append(f"Modify {staged_files[0]}")
        else:
            messages.append(f"Update {len(staged_files)} files")
    
    # Ensure we have at least the requested number of messages
    while len(messages) < count:
        messages.append(f"Commit staged changes ({len(messages) + 1})")
    
    return messages[:count]


def get_commit_message_from_user() -> Optional[str]:
    """Get commit message from user input."""
    try:
        result = subprocess.run(
            ["git", "var", "GIT_EDITOR"],
            capture_output=True,
            text=True,
            check=True
        )
        editor = result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        editor = "nano"  # Default fallback
    
    # Create a temporary file for the commit message
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("# Please enter your commit message above this line\n")
        f.write("# Lines starting with # will be ignored\n")
        temp_file = f.name
    
    try:
        # Open editor
        subprocess.run([editor, temp_file], check=True)
        
        # Read the commit message
        with open(temp_file, 'r') as f:
            lines = f.readlines()
        
        # Extract non-comment lines
        message_lines = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                message_lines.append(line)
        
        return '\n'.join(message_lines) if message_lines else None
    
    except subprocess.CalledProcessError:
        console.print("[red]Failed to open editor for commit message[/red]")
        return None
    finally:
        # Clean up temp file
        import os
        try:
            os.unlink(temp_file)
        except OSError:
            pass
