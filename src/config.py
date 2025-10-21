"""
Configuration management for Pixverse MCP.
"""

import os
import json
import yaml
from pathlib import Path
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from loguru import logger


class PixverseConfig(BaseModel):
    """Pixverse MCP configuration model."""
    
    # API Configuration
    api_key: Optional[str] = Field(default=None, description="Pixverse API key (must be provided via PIXVERSE_API_KEY environment variable)")
    base_url: str = Field(default="https://app-api.pixverse.ai", description="API base URL")


class ConfigManager:
    """Configuration manager for Pixverse MCP."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path
        self._config: Optional[PixverseConfig] = None
        
    def load_config(self, config_path: Optional[str] = None) -> PixverseConfig:
        """Load configuration from file or environment variables."""
        if config_path:
            self.config_path = config_path
            
        # Try to load from file first (optional)
        if self.config_path and Path(self.config_path).exists():
            config_data = self._load_from_file(self.config_path)
            logger.info(f"Configuration file loaded: {self.config_path}")
        else:
            config_data = {}
            if self.config_path:
                logger.info(f"Configuration file not found: {self.config_path}, using defaults and environment variables")
            else:
                logger.info("No configuration file specified, using defaults and environment variables")
            
        # Override with environment variables
        config_data.update(self._load_from_env())
        
        # Validate required fields
        if not config_data.get("api_key"):
            raise ValueError("API key is required. Please set PIXVERSE_API_KEY environment variable in your ~/.cursor/mcp.json configuration.")
            
        self._config = PixverseConfig(**config_data)
        logger.info(f"Configuration loaded successfully")
        return self._config
        
    def _load_from_file(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from file."""
        path = Path(config_path)
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                if path.suffix.lower() in ['.yaml', '.yml']:
                    data = yaml.safe_load(f)
                elif path.suffix.lower() == '.json':
                    data = json.load(f)
                else:
                    raise ValueError(f"Unsupported config file format: {path.suffix}")
                    
            logger.info(f"Configuration loaded from file: {config_path}")
            return data or {}
            
        except Exception as e:
            logger.warning(f"Failed to load config file {config_path}: {e}")
            return {}
            
    def _load_from_env(self) -> Dict[str, Any]:
        """Load configuration from environment variables.
        
        Only load user-specific configurations from environment variables.
        MCP program configurations should be in config.yaml file.
        """
        # Only allow user-specific environment variables
        env_mapping = {
            "PIXVERSE_API_KEY": "api_key",
            # Note: PIXVERSE_BASE_URL is intentionally excluded for normal users
            # It should be configured in config.yaml, not by users
        }
        
        # Advanced users can still override program configs with these env vars
        advanced_env_mapping = {
            "PIXVERSE_BASE_URL": "base_url",
        }
        
        # Combine both mappings for backward compatibility
        env_mapping.update(advanced_env_mapping)
        
        config_data = {}
        for env_key, config_key in env_mapping.items():
            value = os.getenv(env_key)
            if value is not None:
                config_data[config_key] = value
                
        return config_data
        
    @property
    def config(self) -> PixverseConfig:
        """Get current configuration."""
        if self._config is None:
            self._config = self.load_config()
        return self._config
        
    def save_config(self, config_path: Optional[str] = None) -> None:
        """Save current configuration to file."""
        if not self._config:
            raise ValueError("No configuration to save")
            
        path = config_path or self.config_path
        if not path:
            raise ValueError("No config path specified")
            
        path = Path(path)
        config_dict = self._config.model_dump()
        
        try:
            with open(path, 'w', encoding='utf-8') as f:
                if path.suffix.lower() in ['.yaml', '.yml']:
                    yaml.safe_dump(config_dict, f, default_flow_style=False, indent=2)
                elif path.suffix.lower() == '.json':
                    json.dump(config_dict, f, indent=2, ensure_ascii=False)
                else:
                    raise ValueError(f"Unsupported config file format: {path.suffix}")
                    
            logger.info(f"Configuration saved to: {path}")
            
        except Exception as e:
            logger.error(f"Failed to save config to {path}: {e}")
            raise


# Global config manager instance
_config_manager: Optional[ConfigManager] = None


def get_config_manager(config_path: Optional[str] = None) -> ConfigManager:
    """Get global configuration manager instance."""
    global _config_manager
    if _config_manager is None or config_path:
        _config_manager = ConfigManager(config_path)
    return _config_manager


def get_config(config_path: Optional[str] = None) -> PixverseConfig:
    """Get configuration instance."""
    manager = get_config_manager(config_path)
    return manager.config
