import hashlib

def calculate_hashes(file_path):
    """
    Calculates MD5 and SHA-256 hashes of a file
    """
    md5 = hashlib.md5()
    sha256 = hashlib.sha256()

    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5.update(chunk)
            sha256.update(chunk)

    return {
        "md5": md5.hexdigest(),
        "sha256": sha256.hexdigest()
    }
