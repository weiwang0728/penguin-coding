"""Shared constants and utilities — no intra-package imports, so other modules can safely import from here."""
from pathlib import Path
import re

ALLOWED_BASE_DIR = Path(__file__).resolve().parent.parent / "workspace"

MAX_OUTPUT_LENGTH = 30_000
MAX_READ_SIZE = 100 * 1024  # 100KB
MAX_TOOL_RESULT_CHARS = 10_000

DANGEROUS_COMMANDS = [
    r"\brm\s+-rf\s+/",
    r"\brm\s+-rf\s+~",
    r"\brm\s+-rf\s+\$HOME",
    r"\bmkfs\.",
    r"\bdd\s+if=.*of=/dev/",
    r">\s*/etc/passwd",
    r">\s*/etc/shadow",
    r">\s+/dev/(sda|nvme|hd)",
    r"\b:(){ :|:& };:",
    r"\bchmod\s+-R\s+777\s+/",
    r"\bchown\s+-R\s+.*\s+/",
    r"\bsudo\s+rm\s+-rf",
    r"\bsu\s+-",
    r"\bpasswd\b",
    r"\buseradd\b",
    r"\busermod\b",
    r"\bgroupadd\b",
    r"\bshutdown\b",
    r"\breboot\b",
    r"\binit\s+0",
    r"\bsystemctl\s+(stop|restart)\s+(ssh|network|systemd)",
    r"\bkubectl\s+delete\s+.*--all",
    r"\bdocker\s+(rm|kill)\s+.*\*",
    r"\bcurl\s+.*\|\s*sh",
    r"\bwget\s+.*\|\s*sh",
    r"\beval\s*\$",
    r"\bexec\s*\$",
    r"\$\(",
    r"`",
    r"\|\s*(ba)?sh\b",
    r"\bexport\s+\w*(KEY|TOKEN|SECRET|PASSWORD|CREDENTIAL)",
    r"\btee\s+/etc/(passwd|shadow|sudoers|hosts)",
    r"\bkill\s+-9\s+1\b",
    r"\bkillall\s+(init|systemd|sshd)",
]

SHELL_INJECTION_PATTERNS = [re.compile(p, re.IGNORECASE) for p in [r"\$\(", r"`"]]
DANGEROUS_PATTERNS = [
    re.compile(p, re.IGNORECASE) for p in DANGEROUS_COMMANDS if p not in [r"\$\(", r"`"]
]


def check_dangerous_command(command: str) -> str | None:
    for pattern in SHELL_INJECTION_PATTERNS:
        if pattern.search(command):
            return f"Shell command substitution blocked for safety (matched '{pattern.pattern}'). Use direct commands instead of $() or backtick substitution."
    for pattern in DANGEROUS_PATTERNS:
        if pattern.search(command):
            return f"Dangerous command detected and blocked: pattern '{pattern.pattern}'"
    return None


def _truncate_output(output: str, max_length: int = MAX_OUTPUT_LENGTH) -> str:
    if len(output) <= max_length:
        return output
    half = max_length // 2
    return (
        output[:half]
        + f"\n\n... [Output truncated: {len(output)} chars total, showing first and last {half} chars] ...\n\n"
        + output[-half:]
    )


def _truncate_for_context(text: str, max_chars: int = MAX_TOOL_RESULT_CHARS) -> str:
    if len(text) <= max_chars:
        return text
    half = max_chars // 2
    return (
        text[:half]
        + f"\n... [Result truncated for context: {len(text)} chars total] ...\n"
        + text[-half:]
    )
