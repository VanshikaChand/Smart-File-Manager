
import os
from datetime import datetime

def scan_folder(folder_path):
    """Collect metadata for files directly inside a folder."""

    if not os.path.isdir(folder_path):
        print("Error: Folder does not exist.")
        return []

    scanned_files = []

    try:
        with os.scandir(folder_path) as entries:
            for entry in entries:
                try:
                    if not entry.is_file(follow_symlinks=False):
                        continue

                    info = entry.stat(follow_symlinks=False)

                    file_data = {
                        "file_name": entry.name,
                        "file_path": os.path.abspath(entry.path),
                        "file_extension": os.path.splitext(entry.name)[1] or None,
                        "file_size": info.st_size,
                        "last_modified": datetime.fromtimestamp(
                            info.st_mtime
                        ),
                    }

                    scanned_files.append(file_data)

                except OSError as error:
                    print(f"Could not read {entry.path}: {error}")

    except OSError as error:
        print(f"Could not access folder: {error}")
        return []

    return scanned_files



if __name__ == "__main__":
    from file_repository import save_files

    folder = r"D:\SmartFileManagerTest"

    files = scan_folder(folder)

    print(f"\nFolder scanned: {folder}")
    print(f"Files found: {len(files)}\n")

    for file in files:
        print("-" * 40)
        for key, value in file.items():
            print(f"{key}: {value}")

    save_files(files)
