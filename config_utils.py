"""Utility functions for loading TOML configuration files"""
import logging
from pathlib import Path
from typing import Optional, Dict, Any

try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        raise ImportError(
            "TOML support requires Python 3.11+ (with tomllib) or tomli package. "
            "Install with: pip install tomli"
        )

logger = logging.getLogger(__name__)


def load_config(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Load TOML configuration file.
    
    Args:
        config_path: Path to config file. If None, looks for 'beatcharter.toml' in current directory.
    
    Returns:
        Dictionary containing the parsed TOML configuration
    """
    if config_path is None:
        config_path = Path("beatcharter.toml")
    
    if not config_path.exists():
        logger.warning(f"Config file not found: {config_path}. Using defaults.")
        return {}
    
    with open(config_path, "rb") as f:
        config = tomllib.load(f)
    
    logger.info(f"Loaded config from: {config_path}")
    return config


def get_config_value(config: Dict[str, Any], section: str, key: str, default: Any = None) -> Any:
    """
    Get a value from config with optional default.
    
    Args:
        config: Configuration dictionary
        section: Section name (e.g., 'course_creator')
        key: Key name within the section
        default: Default value if not found
    
    Returns:
        Config value or default
    """
    return config.get(section, {}).get(key, default)
