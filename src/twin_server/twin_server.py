import requests
import json
import sys
from pathlib import Path
from enum import Enum

CERTS_DIR = Path("certs")
CA_CERT = CERTS_DIR / "ca.crt" 
CLIENT_CERT = (
    str(CERTS_DIR / "client.crt"), 
    str(CERTS_DIR / "client.key")
)

class TaskType(str, Enum):
    SCAN = "SCAN"
    EXPLOIT = "EXPLOIT"
    COMPLETE = "SCAN_AND_EXPLOIT"

HOST_URL = "https://localhost:5000/command"

def send_task(host: str, task_type: TaskType, target: str, repeats: int):
    task = {
        "type": task_type.value,
        "target_directory": target,
        "repeat_exploit": 3
    }
    
    try:
        response = requests.post(
            HOST_URL, 
            json=task, 
            verify=str(CA_CERT), 
            cert=CLIENT_CERT
        )

        response.raise_for_status()
        
        return json.dumps(response.json(), indent=4)
        
    except requests.exceptions.SSLError as ssl_err:
        print(f"[ERROR] Unauthorized comunication.\n{ssl_err}")
    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":

    if len(sys.argv) != 4:
        print("Invalid command.")
        print("Usage: python3 twin_server.py [TASK_TYPE] [TARGET_DIR] [REPETITIONS]")
        exit(1)
    else:
        task_type = sys.argv[1]
        target = sys.argv[2]
        repetitions = sys.argv[3]
        response = send_task(HOST_URL, TaskType(task_type), target, repetitions)
        print("Agent response:")
        print(response)