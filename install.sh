#!/bin/bash

# Installation script for commiter using uv

echo "Installing commiter with uv..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "Error: uv is required but not installed."
    echo "Please install uv first: https://docs.astral.sh/uv/getting-started/installation/"
    exit 1
fi

# Install the package as a tool
uv tool install --editable .

echo "Installation complete!"
echo ""
echo "You can now use the 'commit' command instead of 'git commit'"
echo ""
echo "Usage examples:"
echo "  commit                    # Interactive mode"
echo "  commit --auto            # Auto-commit"
echo "  commit --custom          # Custom message"
echo "  commit --help            # Show help"
echo ""
echo "Configuration is stored in ~/.commiter/config.json"
echo ""
echo "To uninstall: uv tool uninstall commiter"
