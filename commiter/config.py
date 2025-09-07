"""Configuration management for the commiter CLI."""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class CommiterConfig:
    """Configuration for the commiter CLI."""
    
    # Behavior settings
    interactive_mode: bool = True
    auto_commit: bool = False
    max_choices: int = 3
    
    # AI settings (for future use)
    ai_provider: str = "placeholder"
    ai_model: str = "placeholder"
    
    # Git settings
    git_editor: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CommiterConfig":
        """Create config from dictionary."""
        return cls(**data)


class ConfigManager:
    """Manages configuration for the commiter CLI."""
    
    def __init__(self):
        self.config_dir = Path.home() / ".commiter"
        self.config_file = self.config_dir / "config.json"
        self._config: Optional[CommiterConfig] = None
    
    def ensure_config_dir(self) -> None:
        """Ensure the config directory exists."""
        self.config_dir.mkdir(exist_ok=True)
    
    def load_config(self) -> CommiterConfig:
        """Load configuration from file or create default."""
        if self._config is not None:
            return self._config
        
        self.ensure_config_dir()
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                self._config = CommiterConfig.from_dict(data)
            except (json.JSONDecodeError, TypeError, KeyError):
                # If config is corrupted, create default
                self._config = CommiterConfig()
                self.save_config()
        else:
            self._config = CommiterConfig()
            self.save_config()
        
        return self._config
    
    def save_config(self) -> None:
        """Save current configuration to file."""
        if self._config is None:
            return
        
        self.ensure_config_dir()
        
        with open(self.config_file, 'w') as f:
            json.dump(self._config.to_dict(), f, indent=2)
    
    def update_config(self, **kwargs) -> None:
        """Update configuration with new values."""
        if self._config is None:
            self._config = self.load_config()
        
        for key, value in kwargs.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)
        
        self.save_config()
    
    def get_config(self) -> CommiterConfig:
        """Get current configuration."""
        if self._config is None:
            return self.load_config()
        return self._config


# Global config manager instance
config_manager = ConfigManager()
