# detector/file_type.py
import magic

def detect_file_type(file_path: str) -> dict:
    mime = magic.from_file(file_path, mime=True)
    filename = file_path.split("/")[-1]

    if mime.startswith("image/"):
        file_type = "image"
        subtype = mime.split("/")[-1]
    elif mime == "text/plain" or file_path.endswith((".json", ".csv", ".txt", ".xml")):
        file_type = "text"
        subtype = "text"
    elif mime == "audio/x-wav" or file_path.endswith(".wav"):
        file_type = "audio"
        subtype = "wav"
    else:
        raise ValueError(f"Unsupported file type: {mime}")

    return {
        "type": file_type,
        "subtype": subtype,
        "mime": mime,
        "filename": filename
    }