import paho.mqtt.client as mqtt
import json
import threading
import ssl

_bambu_data = {
    "status": "Connecting...",
    "progress": 0,
    "file": "--",
    "remaining": "--",
    "nozzle": "--",
    "bed": "--"
}

_client_started = False


def format_remaining(seconds):
    try:
        seconds = int(seconds)

        if seconds <= 0:
            return "--"

        minutes = seconds // 60
        hours = minutes // 60
        minutes = minutes % 60

        if hours > 0:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"
    except:
        return "--"


def clean_filename(name):
    if not name:
        return "--"

    # remove extensions
    name = name.replace(".gcode", "").replace(".3mf", "")

    # shorten long names
    if len(name) > 25:
        return name[:22] + "..."

    return name


def start_mqtt(ip, access_code):
    global _client_started

    if _client_started:
        return

    def on_connect(client, userdata, flags, rc):
        print("Bambu MQTT Connected:", rc)
        if rc == 0:
            client.subscribe("device/+/report")

    def on_message(client, userdata, msg):
        global _bambu_data

        try:
            payload = json.loads(msg.payload.decode())

            print_data = payload.get("print")

            if print_data:
                status = print_data.get("gcode_state", "Printing")

                progress = int(
                    print_data.get("mc_percent")
                    or print_data.get("progress")
                    or 0
                )

                # 🔥 FIXED — smarter file detection
                raw_name = (
                    print_data.get("subtask_name")
                    or print_data.get("gcode_file")
                    or print_data.get("project_name")
                    or payload.get("project_name")
                    or payload.get("task_name")
                    or payload.get("gcode_file")
                )

                file_name = clean_filename(raw_name)

                # 🔥 FIXED — better time detection
                remaining_raw = (
                    print_data.get("mc_remaining_time")
                    or print_data.get("remaining_time")
                    or print_data.get("remain_time")
                    or payload.get("mc_remaining_time")
                    or payload.get("remaining_time")
                    or payload.get("remain_time")
                )

                remaining = format_remaining(remaining_raw)

                nozzle = (
                    print_data.get("nozzle_temper")
                    or print_data.get("nozzle_temp")
                    or "--"
                )

                bed = (
                    print_data.get("bed_temper")
                    or print_data.get("bed_temp")
                    or "--"
                )

            else:
                status = payload.get("gcode_state") or payload.get("status") or "Idle"
                progress = 0
                file_name = "No active print"
                remaining = "--"
                nozzle = "--"
                bed = "--"

            _bambu_data = {
                "status": status,
                "progress": progress,
                "file": file_name,
                "remaining": remaining,
                "nozzle": nozzle,
                "bed": bed
            }

        except Exception as e:
            print("[MQTT Parse Error]", e)

    try:
        client = mqtt.Client()

        client.username_pw_set("bblp", access_code)

        client.tls_set(cert_reqs=ssl.CERT_NONE)
        client.tls_insecure_set(True)

        client.on_connect = on_connect
        client.on_message = on_message

        client.connect(ip, 8883, 60)

        thread = threading.Thread(target=client.loop_forever)
        thread.daemon = True
        thread.start()

        _client_started = True

    except Exception as e:
        print("[Bambu MQTT Error]", e)


def get_data(module_config):
    ip = module_config.get("ip")
    access_code = module_config.get("access_code")

    if not ip or not access_code:
        return {
            "id": "bambu",
            "title": "Printer",
            "data": _bambu_data
        }

    start_mqtt(ip, access_code)

    return {
        "id": "bambu",
        "title": "Printer",
        "data": _bambu_data
    }