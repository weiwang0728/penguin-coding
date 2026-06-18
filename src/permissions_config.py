"""Permission configuration loading and profile definitions."""

from pathlib import Path

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


CONFIG_PATH = Path.home() / ".penguin_permissions.yaml"

DEFAULT_CONFIG = {
    "profile": "standard",
    "profiles": {
        "permissive": {
            "defaults": {
                "write_file": "allow",
                "edit_file": "allow",
                "run_command": "allow",
                "background_run": "allow",
                "team_spawn": "allow",
                "team_shutdown": "allow",
                "delegate": "confirm",
            },
            "run_command_overrides": {},
        },
        "standard": {
            "defaults": {
                "write_file": "confirm",
                "edit_file": "confirm",
                "run_command": "confirm",
                "background_run": "confirm",
                "team_spawn": "confirm",
                "team_shutdown": "confirm",
                "delegate": "confirm",
            },
            "run_command_overrides": {
                r"^(ls|cat|echo|pwd|which|whoami|git status|git diff|git log|git branch|python|pip install|npm install|node)\b": "allow",
            },
        },
        "strict": {
            "defaults": {
                "write_file": "deny",
                "edit_file": "confirm",
                "run_command": "deny",
                "background_run": "deny",
                "team_spawn": "deny",
                "team_shutdown": "deny",
                "delegate": "deny",
            },
            "run_command_overrides": {
                r"^(ls|cat|echo|pwd|git status|git diff|git log)\b": "confirm",
            },
        },
    },
}


def load_permissions_config() -> dict:
    """Load permission configuration from YAML file, or return defaults."""
    if CONFIG_PATH.exists() and HAS_YAML:
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                user_config = yaml.safe_load(f) or {}
            # Merge user config with defaults (user config takes precedence)
            return _merge_config(DEFAULT_CONFIG, user_config)
        except Exception:
            pass
    return DEFAULT_CONFIG.copy()


def _merge_config(base: dict, override: dict) -> dict:
    """Deep merge override into base. Override values take precedence."""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _merge_config(result[key], value)
        else:
            result[key] = value
    return result
