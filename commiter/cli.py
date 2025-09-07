"""Simple CLI entry point for commiter."""

import sys
from .main import app

def main():
    """Main entry point for the commit command."""
    return app()

if __name__ == "__main__":
    sys.exit(main())
