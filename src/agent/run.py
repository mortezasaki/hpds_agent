import json
import os
from datetime import datetime

import psutil
import requests

AGENT_ID = "ec72ffd7-c367-43df-baf4-82d9b535e30d"
SERVER_URL = "http://localhost:8000/v1/logs/"


def convert_bytes_to_megabytes(bytes):
    """Convert bytes to megabytes.

    Args:
        bytes (int): Bytes.

    Returns:
        int: Megabytes.
    """
    return bytes / (1024 * 1024)


def get_ram_info():
    """Get RAM information.

    Returns:
        dict: RAM information.
    """
    ram_info = psutil.virtual_memory()
    total_ram = ram_info.total
    used_ram = ram_info.used
    free_ram = ram_info.free

    return {
        'total_ram': convert_bytes_to_megabytes(total_ram),
        'used_ram': convert_bytes_to_megabytes(used_ram),
        'free_ram': convert_bytes_to_megabytes(free_ram),
    }


def collect_logs():
    """Collect logs.

    Returns:
        dict: Logs.
    """
    logs = {}
    logs['ram'] = get_ram_info()
    logs['timestamp'] = datetime.now().isoformat()

    return logs


def save_logs(logs):
    """Save logs in a file.

    Args:
        logs (dict): Logs.
    """
    with open('logs.json', 'w') as f:
        json.dump(logs, f)


def load_logs():
    """Load logs from a file."""
    with open('logs.json', 'r') as f:
        logs = json.load(f)
        return logs


def send_logs(logs):
    """Send logs to server.

    Args:
        logs (dict): Logs.
    """
    new_logs = logs.copy()
    timestamp = new_logs['timestamp']
    del new_logs['timestamp']

    data = {'agent_id': AGENT_ID, 'logs': new_logs, 'timestamp': timestamp}
    data = json.dumps(data)

    try:
        response = requests.post(SERVER_URL, data=data)
    except requests.exceptions.ConnectionError:
        print("Error connecting to server.")
        # Store logs in a file and send them later.
        return False

    if response.status_code == 200:
        print("Logs sent successfully.")
        return True

    print("Error sending logs.")
    # Store logs in a file and send them later.
    return False


def main():
    logs = []
    if os.path.exists('logs.json'):
        logs = load_logs()

    logs.append(collect_logs())

    unsent_logs = []

    for logs in logs:
        if not send_logs(logs):
            unsent_logs.append(logs)

    # Save unsent logs in a file.
    if len(unsent_logs) > 0:
        save_logs(unsent_logs)
    else:
        os.remove('logs.json')


if __name__ == "__main__":
    main()
