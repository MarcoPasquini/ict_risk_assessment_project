import requests
import json
import sys
from pathlib import Path
from enum import Enum
from twin_statistics import evaluate_statistics

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

hosts_path = {
    "pc-dev-00": "https://192.168.50.11:5000/command",
    "pc-dev-01": "https://192.168.50.12:5000/command",
    "PC-SPC-00": "https://192.168.50.18:5000/command",
    "PC-SPC-01": "https://192.168.50.19:5000/command",
    "PC-SPC-02": "https://192.168.50.20:5000/command",
    "PC-SPC-03": "https://192.168.50.21:5000/command",
    "PC-SPC-04": "https://192.168.50.22:5000/command",
    "PC-AT2-00": "https://192.168.50.25:5000/command",
    "PC-AT2-01": "https://192.168.50.26:5000/command",
    "PC-AT2-02": "https://192.168.50.27:5000/command",
}

def send_task(host: str, task_type: TaskType, target: str, repeats: int):
    task = {
        "type": task_type.value,
        "target_directory": target,
        "repeat_exploit": repeats
    }
    
    try:
        response = requests.post(
            HOST_URL, 
            json=task, 
            verify=str(CA_CERT), 
            cert=CLIENT_CERT
        )

        response.raise_for_status()
        
        return response.json()
        
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
        response = send_task(HOST_URL, TaskType(task_type), target, int(repetitions))
        print("Agent response:")
        print(json.dumps(response, indent=4))
        evaluate_statistics(response)

# Update risk score based on the result of the active module
def process_notline_paths(json_file_path, repetitions=5):
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        print(f"Loaded {len(data['vulnerable_paths'])} potentials paths from NotLine.")

        for path in data['vulnerable_paths']:
            path_id = path['id']
            risk_score = path['risk_score']

            print(f"Analyzing path: {path_id} (Initial risk: {risk_score})")

            for step in path['steps_details']:
                host = step["host"]
                if host == "Attacker": continue

                program = step["vulnerable_program"]

                print(f"Checking protections on binary {program} of {host}...")

                task_result = send_task(hosts_path[host], TaskType.COMPLETE, program, int(repetitions))
                
                new_risk = calculate_new_risk(risk_score, task_result, program)
                print(f"New risk is: {new_risk}")

    except FileNotFoundError:
        print(f"Error: file {json_file_path} not found.")

def calculate_new_risk(risk_score, report, program_name):
    binary_report = retrive_binary_report(report, binary, program_name)
    if not binary_report:
        return risk_score
    static_result = get_static_risk(binary_report)
    p_hat = report["test_result"]["p_hat"]
    new_risk = risk_score * static_result
    if p_hat > 0:
        return new_risk
    return new_risk * 0.5

def retrive_binary_report(report_result, binary, program_name):
    try:
        binaries_report = report_result["binaries_report"]
        for report in binaries_report:
            if program_name in report["filename"]:
                return report

    except Exception as e:
        print(f"An unexpected error occurred while retriving the binary report: {e}")

def get_static_risk(report):
    keys_to_check = ["aslr", "pie", "nx", "relro", "canary"]
    
    protections = report.get("protections", {})

    count = sum(protections.get(key, False) for key in keys_to_check)

    return count * 0.1