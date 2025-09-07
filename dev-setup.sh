#!/bin/bash

# Development setup script for commiter using uv

echo "Setting up commiter development environment..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "Error: uv is required but not installed."
    echo "Please install uv first: https://docs.astral.sh/uv/getting-started/installation/"
    exit 1
fi

# Sync dependencies
echo "Syncing dependencies..."
uv sync

# Install pre-commit hooks if available
if command -v pre-commit &> /dev/null; then
    echo "Installing pre-commit hooks..."
    uv run pre-commit install
fi

echo "Development setup complete!"
echo ""
echo "Available commands:"
echo "  uv run commit                    # Run the CLI"
echo "  uv run pytest                   # Run tests"
echo "  uv run black .                  # Format code"
echo "  uv run isort .                  # Sort imports"
echo "  uv run flake8 .                 # Lint code"
echo ""
echo "To install as a tool: uv tool install --editable ."
