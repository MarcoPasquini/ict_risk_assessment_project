import requests
import json
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

def send_task(task_type: TaskType, target: str, repeats: int):
    print(task_type, target, repeats)
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
        
        if not response.ok:
            # MODIFICA QUI: Leggi il JSON dell'errore
            try:
                error_json = response.json()
                print(f"[SERVER ERROR] {response.status_code}")
                print(f"MOTIVO: {error_json.get('reason')}")
            except:
                # Se il server è morto male e non ha mandato JSON
                print(f"[SERVER ERROR] {response.status_code} - {response.text}")
            return
        response.raise_for_status()
        
        print("[CONTROLLER] Risposta ricevuta:")
        print(json.dumps(response.json(), indent=4))
        
    except requests.exceptions.SSLError as ssl_err:
        print(f"[ERROR] Unauthorized comunication.\n{ssl_err}")
    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    send_task(TaskType.SCAN, "logging_system", 3)