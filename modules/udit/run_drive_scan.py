

from .drive_monitor import get_drive_info
from .drive_repository import save_drive_scan


def main():
    drives = get_drive_info()

    if not drives:
        print("No accessible drives detected.")
        return

    print(f"Detected {len(drives)} drive(s).")

    try:
        scan_id = save_drive_scan(drives)
        print(f"Scan saved successfully! Scan ID: {scan_id}")

        for drive in drives:
            print(
                f"{drive['mount_point']} | "
                f"Used: {drive['used_bytes']} bytes | "
                f"Free: {drive['free_bytes']} bytes | "
                f"Utilization: {drive['utilization_percent']}%"
            )

    except Exception as error:
        print(f"Failed to save scan: {error}")


if __name__ == "__main__":
    main()
