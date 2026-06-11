import re
from typing import List, Dict, Any

UNSAFE_PATTERNS = [
    r"\bdiagnose\b",
    r"\bdiagnosis\b",
    r"\bdifferential diagnosis\b",
    r"\bprescribe\b",
    r"\bprescription\b",
    r"\bdosage\b",
    r"\bdose\b",
    r"\bmg\b",
    r"\bincrease medication\b",
    r"\bdecrease medication\b",
    r"\bstop medication\b",
    r"\bstart medication\b",
    r"\btreatment plan\b",
    r"\burgent triage\b",
    r"\bemergency recommendation\b"
]

def check_safety_violations(title: str, description: str) -> str:
    """
    Checks raw title and description against safety rules.
    Returns the first violation string if any, otherwise None.
    """
    text_to_check = f"{title} {description}".lower()
    
    for pattern in UNSAFE_PATTERNS:
        if re.search(pattern, text_to_check):
            return f"Task contains blocked clinical phrase matching: '{pattern}'"
    return None
