import hashlib
import os


def check_file_exists(path):
    return os.path.exists(path)


def sha1_str(input_str):
    m = hashlib.sha1()
    m.update(input_str)
    return m.hexdigest()


def sha1_file(input_filename):
    m = hashlib.sha1()
    with open(input_filename, "rb") as in_fd:
        for chunk in iter(lambda: in_fd.read(4096), b""):
            m.update(chunk)
    return m.hexdigest()
