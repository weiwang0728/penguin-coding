"""Permission control: three-tier system (ALLOW / CONFIRM / DENY)."""

import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from ._constants import check_dangerous_command, check_risky_command
from .tools.utils import resolve_and_validate_path


class PermissionLevel(Enum):
    ALLOW = "allow"
    CONFIRM = "confirm"
    DENY = "deny"


@dataclass
class PermissionResult:
    level: PermissionLevel
    reason: str
    tool_name: str
    args: dict = field(default_factory=dict)


class PermissionManager:
    def __init__(self, config: dict | None = None):
        self.config = config or {}
        self.profile = self.config.get("profile", "standard")
        self._session_allowlist: set[str] = set()
        self._registry: dict | None = None  # set later via set_registry()

    def set_registry(self, registry: dict) -> None:
        self._registry = registry

    def allow_for_session(self, tool_name: str) -> None:
        self._session_allowlist.add(tool_name)

    def reset_session_allowlist(self) -> None:
        self._session_allowlist.clear()

    def check(self, tool_name: str, args: dict) -> PermissionResult:
        # Step 1: Pre-validation (hard validation, no popup)
        validation_error = self._validate_tool_input(tool_name, args)
        if validation_error:
            return PermissionResult(
                level=PermissionLevel.DENY,
                reason=validation_error,
                tool_name=tool_name,
                args=args,
            )

        # Step 2: Determine permission level
        level = self._resolve_level(tool_name, args)
        reason = self._describe_reason(tool_name, args, level)

        return PermissionResult(
            level=level,
            reason=reason,
            tool_name=tool_name,
            args=args,
        )

    def _validate_tool_input(self, tool_name: str, args: dict) -> str | None:
        """Pre-validation: catch invalid inputs before confirmation popup."""
        if tool_name == "edit_file":
            path = args.get("path", "")
            if not path:
                return "Missing required field 'path'"
            try:
                resolved = resolve_and_validate_path(path)
                if not resolved.is_file():
                    return f"File not found: {path}"
            except PermissionError as e:
                return str(e)

        if tool_name in ("run_command", "background_run"):
            command = args.get("command", "")
            danger = check_dangerous_command(command)
            if danger:
                return danger

        return None

    def _resolve_level(self, tool_name: str, args: dict) -> PermissionLevel:
        # Session allowlist takes highest priority
        if tool_name in self._session_allowlist:
            return PermissionLevel.ALLOW

        # Dynamic tools (delegate) — hard-code as CONFIRM
        if tool_name == "delegate":
            return PermissionLevel.CONFIRM

        # run_command / background_run: three-tier logic
        if tool_name in ("run_command", "background_run"):
            return self._resolve_command_level(tool_name, args)

        # File tools: check profile config
        config_level = self._get_profile_level(tool_name)
        if config_level:
            return config_level

        # Fallback to tool's default
        if self._registry and tool_name in self._registry:
            tool = self._registry[tool_name]
            default = getattr(tool, "default_permission_level", "confirm")
            return PermissionLevel(default)

        return PermissionLevel.CONFIRM

    def _resolve_command_level(self, tool_name: str, args: dict) -> PermissionLevel:
        command = args.get("command", "")

        # 1. Dangerous patterns → DENY (always, regardless of profile)
        if check_dangerous_command(command):
            return PermissionLevel.DENY

        # 2. Check profile overrides first (regex patterns — override profile default)
        profile_config = self._get_profile_config()
        overrides = profile_config.get("run_command_overrides", {})
        for pattern, level_str in overrides.items():
            if re.search(pattern, command, re.IGNORECASE):
                resolved = PermissionLevel(level_str)
                # Risky patterns raise to at least CONFIRM, even if override says ALLOW
                if check_risky_command(command) and resolved == PermissionLevel.ALLOW:
                    resolved = PermissionLevel.CONFIRM
                return resolved

        # 3. Risky patterns → at least CONFIRM
        if check_risky_command(command):
            return PermissionLevel.CONFIRM

        # 4. Profile default for run_command
        defaults = profile_config.get("defaults", {})
        default_level = defaults.get("run_command", "confirm")
        return PermissionLevel(default_level)
        overrides = profile_config.get("run_command_overrides", {})
        for pattern, level_str in overrides.items():
            if re.search(pattern, command, re.IGNORECASE):
                return PermissionLevel(level_str)

        # 4. Profile default for run_command
        defaults = profile_config.get("defaults", {})
        default_level = defaults.get("run_command", "confirm")
        return PermissionLevel(default_level)

    def _get_profile_config(self) -> dict:
        return self.config.get("profiles", {}).get(self.profile, {})

    def _get_profile_level(self, tool_name: str) -> PermissionLevel | None:
        profile_config = self._get_profile_config()
        defaults = profile_config.get("defaults", {})
        level_str = defaults.get(tool_name)
        if level_str:
            return PermissionLevel(level_str)
        return None

    def _describe_reason(self, tool_name: str, args: dict, level: PermissionLevel) -> str:
        if level == PermissionLevel.ALLOW:
            return ""
        if level == PermissionLevel.DENY:
            if tool_name in ("run_command", "background_run"):
                return f"Dangerous command blocked: {args.get('command', '')}"
            return f"Operation denied for {tool_name}"
        if level == PermissionLevel.CONFIRM:
            if tool_name in ("run_command", "background_run"):
                command = args.get("command", "")
                if check_risky_command(command):
                    return f"Risky command requires confirmation: {command}"
                return f"Command requires confirmation: {command}"
            if tool_name in ("write_file", "edit_file"):
                return f"File modification requires confirmation: {args.get('path', '')}"
            if tool_name == "background_run":
                return "Background command requires confirmation"
            if tool_name == "delegate":
                return "Sub-agent delegation requires confirmation"
            if tool_name.startswith("team_"):
                return f"Team operation requires confirmation: {tool_name}"
            return f"Operation requires confirmation: {tool_name}"
        return ""
