"""Git operations component for commiter."""

import subprocess
from typing import List, Optional, Tuple
from rich.console import Console

console = Console()


class GitOperations:
    """Handles all git-related operations."""
    
    @staticmethod
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
    
    @staticmethod
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
    
    @staticmethod
    def get_git_status() -> str:
        """Get git status output."""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except (subprocess.CalledProcessError, FileNotFoundError):
            return ""
    
    @staticmethod
    def get_staged_files() -> List[str]:
        """Get list of staged files."""
        try:
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only"],
                capture_output=True,
                text=True,
                check=True
            )
            return [line.strip() for line in result.stdout.split('\n') if line.strip()]
        except (subprocess.CalledProcessError, FileNotFoundError):
            return []
    
    @staticmethod
    def get_diff_content() -> str:
        """Get diff content for staged changes."""
        try:
            result = subprocess.run(
                ["git", "diff", "--cached"],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except (subprocess.CalledProcessError, FileNotFoundError):
            return ""
    
    @staticmethod
    def commit(message: str, git_args: Optional[List[str]] = None) -> Tuple[int, str]:
        """Run git commit with the given message and arguments.
        
        Returns:
            Tuple of (return_code, output_message)
        """
        if git_args is None:
            git_args = []
            
        cmd = ["git", "commit", "-m", message] + git_args
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return result.returncode, result.stdout
        except subprocess.CalledProcessError as e:
            error_msg = f"Git commit failed: {e.stderr if e.stderr else str(e)}"
            return e.returncode, error_msg
        except FileNotFoundError:
            error_msg = "Git not found. Please ensure git is installed."
            return 1, error_msg
    
    @staticmethod
    def validate_git_environment() -> Tuple[bool, str]:
        """Validate git environment and return status.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not GitOperations.check_git_repo():
            return False, "Not in a git repository. Please run this command from within a git repository."
        
        if not GitOperations.check_staged_changes():
            return False, "No staged changes found. Use 'git add <file>' to stage changes before committing."
        
        return True, ""
