"""LLM provider component for commiter."""

import json
import subprocess
from typing import List, Optional, Dict, Any
from rich.console import Console

console = Console()


class OllamaProvider:
    """Ollama LLM provider for generating commit messages."""
    
    def __init__(self, model: str = "llama3.2", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url
    
    def _make_request(self, prompt: str) -> Optional[str]:
        """Make a request to Ollama API."""
        try:
            # Prepare the request data
            data = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 150
                }
            }
            
            # Make the request using curl
            cmd = [
                "curl", "-s", "-X", "POST",
                f"{self.base_url}/api/generate",
                "-H", "Content-Type: application/json",
                "-d", json.dumps(data)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            response = json.loads(result.stdout)
            
            if "response" in response:
                return response["response"].strip()
            else:
                console.print(f"[red]Ollama API error: {response.get('error', 'Unknown error')}[/red]")
                return None
                
        except subprocess.CalledProcessError as e:
            console.print(f"[red]Failed to connect to Ollama: {e.stderr}[/red]")
            return None
        except json.JSONDecodeError as e:
            console.print(f"[red]Failed to parse Ollama response: {e}[/red]")
            return None
        except FileNotFoundError:
            console.print("[red]curl not found. Please install curl to use Ollama provider.[/red]")
            return None
    
    def generate_commit_messages(self, diff_content: str, max_choices: int = 3) -> List[str]:
        """Generate commit messages based on git diff content."""
        if not diff_content.strip():
            return []
        
        # Create a focused prompt for commit message generation
        prompt = self._create_commit_prompt(diff_content, max_choices)
        
        response = self._make_request(prompt)
        if not response:
            return []
        
        # Parse the response to extract commit messages
        messages = self._parse_commit_messages(response, max_choices)
        return messages
    
    def _create_commit_prompt(self, diff_content: str, max_choices: int) -> str:
        """Create a prompt for commit message generation."""
        # Truncate diff if too long
        if len(diff_content) > 2000:
            diff_content = diff_content[:2000] + "\n... (truncated)"
        
        prompt = f"""You are an expert at writing clear, concise git commit messages.
Based on the following git diff, generate {max_choices} different commit message options.

Rules:
- Use conventional commit format when appropriate (feat:, fix:, docs:, style:, refactor:, test:, chore:)
- Keep messages under 50 characters for the subject line
- Be specific about what changed
- Use imperative mood (e.g., "Add feature" not "Added feature")
- Each message must be on a separate line
- Do not include any markdown, backticks, code fences, bullet points, numbering, or quotation marks
- Output must be plain text only: one commit message per line, nothing else

Git diff:
{diff_content}

Generate {max_choices} commit message options:"""
        
        return prompt
    
    def _parse_commit_messages(self, response: str, max_choices: int) -> List[str]:
        """Parse commit messages from the LLM response."""
        messages = []
        
        # Split by lines and clean up
        lines = response.split('\n')
        for line in lines:
            line = line.strip()
            # Skip empty lines and common prefixes
            if not line or line.startswith(('Here are', 'Based on', 'Options:', '1.', '2.', '3.', '4.', '5.')):
                continue
            # Skip code fence lines
            if line.startswith('```') or line.endswith('```'):
                continue
            
            # Remove numbering if present
            if line and line[0].isdigit() and ('.' in line or ')' in line):
                line = line.split('.', 1)[1].strip() if '.' in line else line.split(')', 1)[1].strip()
            
            # Clean up the message
            line = line.strip('\"\'`-*•')
            # Remove bold markers and inline code quotes
            if line.startswith('**') and line.endswith('**'):
                line = line[2:-2].strip()
            if line.startswith('`') and line.endswith('`'):
                line = line[1:-1].strip()
            # Remove common bullet prefixes
            for bullet in ("- ", "* ", "• "):
                if line.startswith(bullet):
                    line = line[len(bullet):].strip()
                    break
            
            if line and len(line) > 5:  # Basic validation
                messages.append(line)
                if len(messages) >= max_choices:
                    break
        
        return messages
    
    def test_connection(self) -> bool:
        """Test if Ollama is running and accessible."""
        try:
            cmd = ["curl", "-s", f"{self.base_url}/api/tags"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            response = json.loads(result.stdout)
            return "models" in response
        except (subprocess.CalledProcessError, json.JSONDecodeError, FileNotFoundError):
            return False


class LLMProvider:
    """Main LLM provider interface."""
    
    def __init__(self, provider: str = "ollama", model: str = "llama3.2", **kwargs):
        self.provider = provider
        self.model = model
        
        if provider == "ollama":
            self.client = OllamaProvider(
                model=model,
                base_url=kwargs.get("base_url", "http://localhost:11434")
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")
    
    def generate_commit_messages(self, diff_content: str, max_choices: int = 3) -> List[str]:
        """Generate commit messages using the configured provider."""
        return self.client.generate_commit_messages(diff_content, max_choices)
    
    def test_connection(self) -> bool:
        """Test connection to the LLM provider."""
        return self.client.test_connection()
    
    def get_available_models(self) -> List[str]:
        """Get list of available models for the provider."""
        if self.provider == "ollama":
            try:
                cmd = ["curl", "-s", f"{self.client.base_url}/api/tags"]
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                response = json.loads(result.stdout)
                return [model["name"] for model in response.get("models", [])]
            except (subprocess.CalledProcessError, json.JSONDecodeError, FileNotFoundError):
                return []
        return []
