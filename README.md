# Commiter

A CLI tool that acts as an alias to `git commit` with AI-generated commit messages. Choose from multiple generated options or provide your own custom message.

## Features

- 🤖 **AI-Generated Messages**: Get intelligent commit message suggestions based on your staged changes
- 🎯 **Interactive Mode**: Choose from multiple commit message options with a beautiful CLI interface
- ⚡ **Auto-Commit**: Option to automatically commit with the first generated message
- 🛠️ **Custom Messages**: Enter your own commit message when needed
- ⚙️ **Configurable**: Customize behavior through a simple config file
- 🔧 **Git Integration**: Seamlessly integrates with existing git workflows

## Installation

### Prerequisites

This project uses [uv](https://docs.astral.sh/uv/) for dependency management and tool installation. Install uv first:

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Quick Install

```bash
git clone https://github.com/yourusername/commiter.git
cd commiter
./install.sh
```

### Manual Install

```bash
git clone https://github.com/yourusername/commiter.git
cd commiter
uv tool install --editable .
```

### Development Setup

```bash
git clone https://github.com/yourusername/commiter.git
cd commiter
./dev-setup.sh
```

## Usage

### Basic Usage

```bash
# Interactive mode (default)
commit

# Auto-commit with first generated message
commit --auto

# Enter custom commit message
commit --custom

# Show help
commit --help
```

### Advanced Usage

```bash
# Pass additional git arguments
commit --amend
commit --no-verify
commit --interactive --amend

# Configure behavior
commit config --show
commit config --interactive-mode false
commit config --auto-commit true
commit config --max-choices 5
```

## Configuration

The tool uses `~/.commiter/config.json` for configuration:

```json
{
  "interactive_mode": true,
  "auto_commit": false,
  "max_choices": 3,
  "ai_provider": "placeholder",
  "ai_model": "placeholder",
  "git_editor": null
}
```

### Configuration Options

- `interactive_mode`: Use interactive mode by default (true/false)
- `auto_commit`: Auto-commit with first message (true/false)
- `max_choices`: Number of commit message options to show (default: 3)
- `ai_provider`: AI service provider (for future AI integration)
- `ai_model`: AI model to use (for future AI integration)
- `git_editor`: Custom git editor (null for default)

## Examples

### Interactive Mode

```bash
$ commit

Staged changes:
  ~ src/main.py
  + tests/test_main.py

Choose a commit message:

┌────────┬─────────────────────────────────┐
│ Option │ Message                         │
├────────┼─────────────────────────────────┤
│ 1      │ Update src/main.py              │
│ 2      │ Update 1 Python files           │
│ 3      │ Update 2 files                  │
└────────┴─────────────────────────────────┘

Select option (1-3): 1

Commit message:
┌─────────────────────────────────────────┐
│ Update src/main.py                      │
└─────────────────────────────────────────┘

Proceed with this commit message? [Y/n]: y
✓ Commit successful!
```

### Auto-Commit Mode

```bash
$ commit --auto
Auto-committing with message: Update src/main.py
✓ Commit successful!
```

### Custom Message Mode

```bash
$ commit --custom

Enter custom commit message: Message: Fix critical bug in authentication

Commit message:
┌─────────────────────────────────────────┐
│ Fix critical bug in authentication     │
└─────────────────────────────────────────┘

Proceed with this commit message? [Y/n]: y
✓ Commit successful!
```

## Development

### Project Structure

```
commiter/
├── commiter/
│   ├── __init__.py
│   ├── main.py              # Main CLI application
│   ├── config.py            # Configuration management
│   ├── commit_generator.py  # Commit message generation
│   └── interactive.py       # Interactive CLI components
├── pyproject.toml           # Project configuration and dependencies
├── install.sh               # Installation script
├── dev-setup.sh             # Development setup script
└── README.md
```

### Dependencies

- `typer[all]`: CLI framework
- `rich`: Beautiful terminal output and interactive components

### Running from Source

```bash
# Set up development environment
./dev-setup.sh

# Run directly with uv
uv run commit

# Or install as a tool and use globally
uv tool install --editable .
commit
```

### Development Commands

```bash
# Run tests
uv run pytest

# Format code
uv run black .

# Sort imports
uv run isort .

# Lint code
uv run flake8 .

# Install as tool
uv tool install --editable .

# Uninstall tool
uv tool uninstall commiter
```

## Future Enhancements

- [ ] Real AI integration for commit message generation
- [ ] Support for different AI providers (OpenAI, Anthropic, etc.)
- [ ] Commit message templates
- [ ] Integration with conventional commits
- [ ] Git hooks integration
- [ ] Commit message history and learning

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
