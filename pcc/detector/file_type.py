# -*- coding: utf-8 -*-
"""
File type detection utility for Pied Piper Compression.
"""

import mimetypes
from pathlib import Path

def detect_file_type(file_path: str) -> dict:
    """
    Detects the type and MIME of a file based on its extension.
    Returns a dictionary with 'type', 'category', and 'mime_type'.
    """
    path = Path(file_path)
    ext = path.suffix.lower()

    # Try mimetypes first
    mime, _ = mimetypes.guess_type(file_path)

    # Simple extension-based categorization
    if ext in [".txt", ".md", ".rtf", ".log"]:
        ftype = "text"
    elif ext in [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"]:
        ftype = "image"
    elif ext in [".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a"]:
        ftype = "audio"
    elif ext in [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm"]:
        ftype = "video"
    elif ext in [".pdf"]:
        ftype = "pdf"
    elif ext in [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"]:
        ftype = "archive"
    elif ext in [".csv", ".xls", ".xlsx"]:
        ftype = "spreadsheet"
    elif ext in [".json", ".xml", ".yaml", ".yml"]:
        ftype = "data"
    elif ext in [".py", ".java", ".cpp", ".c", ".js", ".ts", ".html", ".css"]:
        ftype = "code"
    else:
        ftype = "binary"

    return {
        "type": ftype,
        "category": ftype,  # Same as type for compatibility
        "mime": mime if mime else "application/octet-stream",
        "mime_type": mime if mime else "application/octet-stream"  # Alternative key
    }
