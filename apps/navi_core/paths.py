"""
Path helpers for NAVI Core configuration files.
"""

from pathlib import Path


def get_config_path(filename: str) -> Path:
    """
    Get path to a configuration file.
    
    Args:
        filename: Config filename (e.g., "personas.yaml")
    
    Returns:
        Path to config file
    """
    base_dir = Path(__file__).parent
    return base_dir / "config" / filename


def get_config_dir() -> Path:
    """
    Get path to config directory.
    
    Returns:
        Path to config directory
    """
    return Path(__file__).parent / "config"
