
import os
import json
import psutil


def get_drive_info():
    """Detect drives and collect storage information."""
    drives = []
    seen_mounts = set()

    for partition in psutil.disk_partitions(all=False):
        try:
            mount_point = os.path.normpath(partition.mountpoint)

            # Avoid duplicate mount-point formats
            if mount_point in seen_mounts:
                continue

            seen_mounts.add(mount_point)
            usage = psutil.disk_usage(partition.mountpoint)

            drives.append({
                "mount_point": mount_point,
                "filesystem": partition.fstype or "Unknown",
                "total_bytes": usage.total,
                "used_bytes": usage.used,
                "free_bytes": usage.free,
                "utilization_percent": round(usage.percent, 2),
            })

        except (PermissionError, OSError) as error:
            print(f"Skipping {partition.mountpoint}: {error}")

    return drives


if __name__ == "__main__":
    print(json.dumps(get_drive_info(), indent=4))
