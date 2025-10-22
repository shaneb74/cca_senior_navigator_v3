"""Path resolution helpers for static assets and configs."""
from pathlib import Path

# Repository root (parent of this file's directory)
REPO_ROOT = Path(__file__).parent.parent


def get_static(relpath: str) -> str:
    """
    Get absolute path to a static asset.
    
    Args:
        relpath: Relative path under static/ (e.g., "images/logo.png")
    
    Returns:
        Absolute path to the asset
    
    Example:
        >>> get_static("images/logo.png")
        "/path/to/repo/static/images/logo.png"
    """
    static_dir = REPO_ROOT / "static"
    asset_path = static_dir / relpath

    if not asset_path.exists():
        # Don't fail silently - warn but return path anyway
        print(f"⚠️ Static asset not found: {asset_path}")

    return str(asset_path)


def get_gcp_module_path() -> str:
    """
    Get path to the canonical GCP module.json.
    
    This is the single source of truth for GCP module configuration.
    
    Returns:
        Relative path to module.json from repo root
    
    Example:
        >>> get_gcp_module_path()
        "products/gcp_v4/modules/care_recommendation/module.json"
    """
    return "products/gcp_v4/modules/care_recommendation/module.json"


def get_gcp_module_absolute_path() -> Path:
    """
    Get absolute Path object to the canonical GCP module.json.
    
    Returns:
        Absolute Path to module.json
    """
    return REPO_ROOT / get_gcp_module_path()


def get_config_path(relpath: str) -> str:
    """
    Get absolute path to a config file.
    
    Args:
        relpath: Relative path under config/ (e.g., "nav.json")
    
    Returns:
        Absolute path to the config file
    
    Example:
        >>> get_config_path("nav.json")
        "/path/to/repo/config/nav.json"
    """
    config_dir = REPO_ROOT / "config"
    config_path = config_dir / relpath

    if not config_path.exists():
        print(f"⚠️ Config file not found: {config_path}")

    return str(config_path)


def get_data_path(relpath: str, create_dirs: bool = False) -> str:
    """
    Get absolute path to a data file.
    
    Args:
        relpath: Relative path under data/ (e.g., "users/demo/john.json")
        create_dirs: If True, create parent directories if they don't exist
    
    Returns:
        Absolute path to the data file
    
    Example:
        >>> get_data_path("users/demo/john.json")
        "/path/to/repo/data/users/demo/john.json"
    """
    data_dir = REPO_ROOT / "data"
    data_path = data_dir / relpath

    if create_dirs:
        data_path.parent.mkdir(parents=True, exist_ok=True)

    return str(data_path)


def ensure_data_dirs():
    """
    Ensure required data directories exist.
    
    Creates:
        - data/users/
        - data/users/demo/
    """
    (REPO_ROOT / "data" / "users").mkdir(parents=True, exist_ok=True)
    (REPO_ROOT / "data" / "users" / "demo").mkdir(parents=True, exist_ok=True)


def get_repo_root() -> Path:
    """
    Get the repository root directory.
    
    Returns:
        Path object pointing to repo root
    """
    return REPO_ROOT
