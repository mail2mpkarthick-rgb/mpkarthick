import re

from app.logging_conf import get_logger

log = get_logger(__name__)

# Patterns that have no legitimate place in generated Playwright specs.
FORBIDDEN_PATTERNS = [
    (r"\brequire\s*\(\s*['\"]child_process['\"]", "spawns OS processes"),
    (r"\brequire\s*\(\s*['\"]fs['\"]", "direct filesystem access"),
    (r"\brequire\s*\(\s*['\"](net|http|https|dgram)['\"]", "raw network access"),
    (r"\bimport\s+.*\bfrom\s+['\"]child_process['\"]", "spawns OS processes"),
    (r"\beval\s*\(", "dynamic code evaluation"),
    (r"\bnew\s+Function\s*\(", "dynamic code construction"),
    (r"\bprocess\.(exit|kill|abort)\s*\(", "terminates the process"),
    (r"\bexecSync\b|\bspawnSync\b|\bexecFile\b", "shell execution"),
    (r"rm\s+-rf\s+/", "destructive filesystem command"),
]


class UnsafeGeneratedCode(ValueError):
    """Raised when model-generated code contains a forbidden construct."""


def scan(code: str) -> list[str]:
    findings = []
    for pattern, reason in FORBIDDEN_PATTERNS:
        if re.search(pattern, code, re.IGNORECASE):
            findings.append(reason)
    return findings


def validate(code: str, label: str = "generated code") -> str:
    """Reject model output containing constructs a Playwright test never needs."""
    findings = scan(code)
    if findings:
        log.error("Blocked unsafe %s: %s", label, "; ".join(findings))
        raise UnsafeGeneratedCode(
            f"Refusing to save {label}: contains {', '.join(sorted(set(findings)))}."
        )
    return code
