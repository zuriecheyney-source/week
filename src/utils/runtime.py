import sys
from typing import Optional


def configure_stdio(encoding: str = "utf-8", errors: str = "replace") -> None:
    """Best-effort Windows console encoding setup.

    Avoids UnicodeEncodeError on GBK consoles by forcing stdout/stderr
    to utf-8 with replacement.
    """
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding=encoding, errors=errors)
    except Exception:
        pass

    try:
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding=encoding, errors=errors)
    except Exception:
        pass


def safe_str(obj: object) -> str:
    try:
        return str(obj)
    except Exception:
        return repr(obj)
