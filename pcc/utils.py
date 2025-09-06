def read_bytes(path):
    with open(path, "rb") as f:
        return f.read()

def write_bytes(path, data):
    with open(path, "wb") as f:
        f.write(data)

import datetime
def now_iso():
    return datetime.datetime.now().isoformat(timespec="seconds")