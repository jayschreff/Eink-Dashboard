import requests


def get_data(module_config):
    ip = module_config.get("192.168.1.109")
    access_code = module_config.get("E9f74e79")

    if not ip or not access_code:
        return {
            "id": "bambu",
            "title": "Printer",
            "data": {
                "status": "Missing config",
                "progress": 0,
                "file": "--",
                "remaining": "--",
                "nozzle": "--",
                "bed": "--"
            }
        }

    url = f"http://{ip}/api/v1/status"

    headers = {
        "X-Access-Code": access_code
    }

    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()

        # 🔍 Handle multiple possible key names
        status = (
            data.get("print_status")
            or data.get("status")
            or "Idle"
        )

        progress = int(
            data.get("progress")
            or data.get("print_progress")
            or 0
        )

        file_name = (
            data.get("file_name")
            or data.get("job_name")
            or data.get("gcode_file")
            or "No file"
        )

        remaining = (
            data.get("remaining_time")
            or data.get("time_remaining")
            or "--"
        )

        nozzle = (
            data.get("nozzle_temp")
            or data.get("extruder_temp")
            or "--"
        )

        bed = (
            data.get("bed_temp")
            or data.get("bed_temperature")
            or "--"
        )

        return {
            "id": "bambu",
            "title": "Printer",
            "data": {
                "status": status,
                "progress": progress,
                "file": file_name,
                "remaining": remaining,
                "nozzle": nozzle,
                "bed": bed
            }
        }

    except Exception as e:
        print(f"[Bambu Error] {e}")

        return {
            "id": "bambu",
            "title": "Printer",
            "data": {
                "status": "Offline",
                "progress": 0,
                "file": "--",
                "remaining": "--",
                "nozzle": "--",
                "bed": "--"
            }
        }