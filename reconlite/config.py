"""
Configuration loader module for ReconLite.

Loads configuration from YAML/JSON files, environment variables, and defaults.
Supports user-defined site lists and persistent settings.
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


# Default configuration values
DEFAULT_CONFIG: Dict[str, Any] = {
    "general": {
        "reports_dir": "./reports",
        "timeout": 10,
        "max_workers": 5,
        "log_level": "INFO",
    },
    "username_check": {
        "sites_file": None,  # None = use built-in sites
        "rate_limit_delay": 0.0,
        "follow_redirects": True,
        "max_workers": 5,
        "timeout": 10,
    },
    "dns": {
        "use_dnspython": False,
        "timeout": 5,
        "servers": [],  # Use system DNS
    },
    "reporting": {
        "formats": ["json", "markdown"],
        "include_raw": False,
    },
}


def get_config_dir() -> Path:
    """
    Get the configuration directory path.

    On Windows: %APPDATA%/reconlite
    On Unix-like: ~/.config/reconlite

    Returns:
        Path object pointing to the configuration directory.
    """
    if sys.platform == "win32":
        app_data = os.environ.get("APPDATA", "")
        if app_data:
            return Path(app_data) / "reconlite"
    return Path.home() / ".config" / "reconlite"


def get_config() -> Dict[str, Any]:
    """
    Load the full configuration by merging:
    1. Default values
    2. User config file (if exists)
    3. Environment variables (highest priority)

    Returns:
        Merged configuration dictionary.
    """
    config = _deep_copy(DEFAULT_CONFIG)

    # Load user config file
    config_path = _find_config_file()
    if config_path and config_path.exists():
        file_config = _load_config_file(config_path)
        if file_config:
            config = _deep_merge(config, file_config)

    # Apply environment variable overrides
    _apply_env_overrides(config)

    return config


def _find_config_file() -> Optional[Path]:
    """
    Find the configuration file in standard locations.

    Checks:
    1. ~/.config/reconlite/config.yaml
    2. ~/.config/reconlite/config.json
    3. ./config/config.yaml (project-local)
    4. ./config/config.json (project-local)

    Returns:
        Path to config file, or None if not found.
    """
    config_dir = get_config_dir()
    for filename in ["config.yaml", "config.yml", "config.json"]:
        config_path = config_dir / filename
        if config_path.exists():
            return config_path

    # Check project-local config
    project_config_dir = Path(__file__).parent / "config"
    for filename in ["config.yaml", "config.yml", "config.json"]:
        config_path = project_config_dir / filename
        if config_path.exists():
            return config_path

    return None


def _load_config_file(path: Path) -> Optional[Dict[str, Any]]:
    """
    Load configuration from a YAML or JSON file.

    Args:
        path: Path to the configuration file.

    Returns:
        Configuration dictionary, or None if loading fails.
    """
    try:
        if path.suffix in (".yaml", ".yml"):
            return _load_yaml(path)
        elif path.suffix == ".json":
            return _load_json(path)
    except Exception:
        pass
    return None


def _load_json(path: Path) -> Dict[str, Any]:
    """Load a JSON configuration file."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_yaml(path: Path) -> Dict[str, Any]:
    """
    Load a YAML configuration file.

    Uses pyyaml if available, otherwise falls back to simple JSON-like parsing.
    """
    try:
        import yaml
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except ImportError:
        # Fallback: if pyyaml not available, try simple parsing
        # For basic configs, JSON format is recommended without pyyaml
        return {}


def _apply_env_overrides(config: Dict[str, Any]) -> None:
    """
    Apply environment variable overrides to the configuration.

    Environment variables follow the pattern: RECONLITE_<SECTION>_<KEY>
    Example: RECONLITE_GENERAL_TIMEOUT=30

    Args:
        config: Configuration dictionary to modify in place.
    """
    env_prefix = "RECONLITE_"

    for section_key, section in config.items():
        if not isinstance(section, dict):
            continue
        for key in section:
            env_var = f"{env_prefix}{section_key.upper()}_{key.upper()}"
            env_value = os.environ.get(env_var)
            if env_value is not None:
                # Parse the value based on type
                config[section_key][key] = _parse_env_value(env_value, section[key])


def _parse_env_value(value: str, default: Any) -> Any:
    """
    Parse an environment variable value to the appropriate type.

    Args:
        value: The string value from the environment variable.
        default: The default value (used to determine expected type).

    Returns:
        Parsed value with appropriate type.
    """
    if isinstance(default, bool):
        return value.lower() in ("true", "1", "yes", "on")
    elif isinstance(default, int):
        try:
            return int(value)
        except ValueError:
            return default
    elif isinstance(default, float):
        try:
            return float(value)
        except ValueError:
            return default
    elif isinstance(default, list):
        # Parse comma-separated values
        return [v.strip() for v in value.split(",") if v.strip()]
    return value


def load_sites(sites_file: Optional[str] = None) -> Dict[str, str]:
    """
    Load custom site list from a YAML/JSON file.

    If sites_file is None or doesn't exist, returns the built-in SITES dict.

    The sites file format:
        SiteName: "https://example.com/{username}"
        AnotherSite: "https://example2.com/u/{username}"

    Args:
        sites_file: Path to the sites configuration file.

    Returns:
        Dictionary mapping site names to URL templates.
    """
    if sites_file is None:
        # Import here to avoid circular imports
        from modules.username import SITES
        return SITES

    sites_path = Path(sites_file)
    if not sites_path.exists():
        # Fall back to built-in sites
        from modules.username import SITES
        return SITES

    try:
        if sites_path.suffix == ".json":
            with open(sites_path, "r", encoding="utf-8") as f:
                return json.load(f)
        elif sites_path.suffix in (".yaml", ".yml"):
            data = _load_yaml(sites_path)
            if data:
                return {k: str(v) for k, v in data.items() if isinstance(v, str)}
    except Exception:
        pass

    # Fall back to built-in sites
    from modules.username import SITES
    return SITES


def save_config(config: Dict[str, Any], path: Optional[Path] = None) -> bool:
    """
    Save configuration to a file.

    Args:
        config: Configuration dictionary to save.
        path: Target path. If None, saves to default config directory.

    Returns:
        True if saved successfully, False otherwise.
    """
    if path is None:
        config_dir = get_config_dir()
        config_dir.mkdir(parents=True, exist_ok=True)
        path = config_dir / "config.json"

    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        return True
    except OSError:
        return False


def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep merge two dictionaries. Override values take precedence.

    Args:
        base: Base dictionary.
        override: Override dictionary.

    Returns:
        Merged dictionary.
    """
    result = _deep_copy(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def _deep_copy(obj: Any) -> Any:
    """Create a deep copy of a dictionary."""
    if isinstance(obj, dict):
        return {k: _deep_copy(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_deep_copy(item) for item in obj]
    return obj
