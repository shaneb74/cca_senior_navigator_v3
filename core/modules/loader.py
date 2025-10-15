"""Utilities for discovering and loading product modules.

Provides standardized functions for:
- Discovering available modules in a product
- Loading module configurations
- Loading module manifests
"""

import importlib
import json
from pathlib import Path
from typing import Dict, List, Optional

from core.modules.schema import ModuleConfig


def discover_product_modules(product: str) -> List[str]:
    """Discover available module names for a product.
    
    Scans the products/{product}/modules/ directory for subdirectories
    containing module definitions.
    
    Args:
        product: Product identifier (e.g., "cost_planner_v2", "gcp")
    
    Returns:
        List of module directory names (e.g., ["income", "assets", "va_benefits"])
        Returns empty list if modules directory doesn't exist
    
    Example:
        modules = discover_product_modules("cost_planner_v2")
        # => ["income", "assets", "insurance", "va_benefits", ...]
    """
    # Get path to modules directory
    modules_dir = Path(__file__).parent.parent.parent / "products" / product / "modules"
    
    if not modules_dir.exists() or not modules_dir.is_dir():
        return []
    
    # Find all subdirectories (excluding hidden and __pycache__)
    return [
        d.name for d in modules_dir.iterdir()
        if d.is_dir() 
        and not d.name.startswith("_")
        and not d.name.startswith(".")
        and d.name != "__pycache__"
    ]


def load_product_module_config(product: str, module: str) -> ModuleConfig:
    """Load configuration for a product sub-module.
    
    Imports the module's config.py file and calls get_config() to obtain
    the ModuleConfig instance.
    
    Args:
        product: Product identifier (e.g., "cost_planner_v2")
        module: Module identifier (e.g., "income")
    
    Returns:
        ModuleConfig instance for the module
    
    Raises:
        ImportError: If module config file cannot be imported
        AttributeError: If config module doesn't have get_config() function
    
    Example:
        config = load_product_module_config("cost_planner_v2", "income")
        run_module(config)
    """
    # Import config module
    module_path = f"products.{product}.modules.{module}.config"
    
    try:
        config_module = importlib.import_module(module_path)
    except ImportError as e:
        raise ImportError(
            f"Cannot import module config: {module_path}\n"
            f"Make sure products/{product}/modules/{module}/config.py exists.\n"
            f"Original error: {e}"
        )
    
    # Get config factory function
    if not hasattr(config_module, "get_config"):
        raise AttributeError(
            f"Module {module_path} must define get_config() -> ModuleConfig\n"
            f"Expected: def get_config() -> ModuleConfig: ..."
        )
    
    get_config = getattr(config_module, "get_config")
    
    # Call factory and return config
    try:
        config = get_config()
    except Exception as e:
        raise RuntimeError(
            f"Error calling {module_path}.get_config(): {e}"
        ) from e
    
    if not isinstance(config, ModuleConfig):
        raise TypeError(
            f"{module_path}.get_config() must return ModuleConfig instance, "
            f"got {type(config).__name__}"
        )
    
    return config


def load_product_module_manifest(product: str, module: str) -> Dict:
    """Load JSON manifest for a product sub-module.
    
    Reads the module.json file from the module directory.
    
    Args:
        product: Product identifier (e.g., "cost_planner_v2")
        module: Module identifier (e.g., "income")
    
    Returns:
        Dict with module manifest data
    
    Raises:
        FileNotFoundError: If module.json doesn't exist
        json.JSONDecodeError: If module.json is invalid JSON
    
    Example:
        manifest = load_product_module_manifest("cost_planner_v2", "income")
        print(manifest["module"]["name"])  # => "Income Sources"
    """
    # Build path to manifest file
    manifest_path = (
        Path(__file__).parent.parent.parent
        / "products" / product / "modules" / module / "module.json"
    )
    
    if not manifest_path.exists():
        raise FileNotFoundError(
            f"Module manifest not found: {manifest_path}\n"
            f"Expected file: products/{product}/modules/{module}/module.json"
        )
    
    # Load and parse JSON
    try:
        with manifest_path.open() as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(
            f"Invalid JSON in {manifest_path}: {e.msg}",
            e.doc,
            e.pos
        )


def module_exists(product: str, module: str) -> bool:
    """Check if a module exists for a product.
    
    Args:
        product: Product identifier
        module: Module identifier
    
    Returns:
        True if module directory exists, False otherwise
    """
    module_dir = (
        Path(__file__).parent.parent.parent
        / "products" / product / "modules" / module
    )
    return module_dir.exists() and module_dir.is_dir()


def get_module_path(product: str, module: str) -> Path:
    """Get absolute path to a module directory.
    
    Args:
        product: Product identifier
        module: Module identifier
    
    Returns:
        Path object pointing to module directory
    """
    return (
        Path(__file__).parent.parent.parent
        / "products" / product / "modules" / module
    )


def get_module_state_key(product: str, module: str) -> str:
    """Get standardized state key for a module.
    
    Args:
        product: Product identifier
        module: Module identifier
    
    Returns:
        State key string (e.g., "cost_planner_v2.income")
    """
    return f"{product}.{module}"


__all__ = [
    "discover_product_modules",
    "load_product_module_config",
    "load_product_module_manifest",
    "module_exists",
    "get_module_path",
    "get_module_state_key",
]
