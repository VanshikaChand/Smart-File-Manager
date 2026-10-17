"""Safe file movement helpers. Test only with temporary sample files."""
import hashlib
import os
import shutil
import tempfile


def calculate_checksum(file_path: str) -> str:
    digest = hashlib.sha256()
    with open(file_path, "rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_move(source: str, destination: str) -> bool:
    """Move a file, verifying cross-filesystem copies before deleting source."""
    source = os.path.abspath(source)
    destination = os.path.abspath(destination)

    try:
        if not os.path.isfile(source) or os.path.islink(source):
            return False
        if os.path.exists(destination):
            return False
        if os.path.realpath(os.path.dirname(destination)) == os.path.realpath(source):
            return False
        os.makedirs(os.path.dirname(destination), exist_ok=True)

        # Try an atomic rename first (usually same filesystem).
        try:
            os.replace(source, destination)
            return True
        except OSError:
            pass

        # Cross-filesystem fallback: copy to a temporary file beside destination.
        source_hash = calculate_checksum(source)
        fd, temp_path = tempfile.mkstemp(
            prefix=".smartfm-", suffix=".tmp",
            dir=os.path.dirname(destination)
        )
        os.close(fd)
        try:
            shutil.copy2(source, temp_path)
            if calculate_checksum(temp_path) != source_hash:
                os.remove(temp_path)
                return False
            # Do not overwrite an existing destination.
            if os.path.exists(destination):
                os.remove(temp_path)
                return False
            os.rename(temp_path, destination)
            os.remove(source)
            return True
        except Exception:
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except OSError:
                    pass
            return False
    except (OSError, ValueError):
        return False
