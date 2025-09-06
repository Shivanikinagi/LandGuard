from __future__ import annotations
import mimetypes

try:
    import magic  # from python-magic-bin (Windows)
    _HAVE_MAGIC = True
except Exception:
    _HAVE_MAGIC = False

_DEF_BIN = "application/octet-stream"


def detect_mime(path: str) -> str:
    if _HAVE_MAGIC:
        try:
            m = magic.Magic(mime=True)
            return m.from_file(path)
        except Exception:
            pass
    mime, _ = mimetypes.guess_type(path)
    return mime or _DEF_BIN