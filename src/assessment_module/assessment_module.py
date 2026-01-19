import os
import json
import yaml
from enum import Enum
from pwn import ELF, context
from host_state import get_host_state
from exploits import run_exploits
import ssl
from flask import Flask, request, jsonify
from pathlib import Path

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent

PROGRAMS_DIR = (PROJECT_ROOT / "programs").resolve()
CONFIG_FILE = (BASE_DIR / "config" / "agent_config.yaml").resolve()
CERTS_DIR = (PROJECT_ROOT.parent / "certs").resolve()

CA_CERT = CERTS_DIR / "ca.crt"
SERVER_CERT = CERTS_DIR / "server.crt"
SERVER_KEY = CERTS_DIR / "server.key"

class TaskType(str, Enum):
    SCAN = "SCAN"
    EXPLOIT = "EXPLOIT"
    COMPLETE = "SCAN_AND_EXPLOIT"

class AgentMode(str, Enum):
    ACTIVE = "active_defense"
    PASSIVE = "passive_monitoring"

@app.route('/command', methods=['POST'])
def handle_command():
    try:
        data = request.json

        result_data = start_engine(data)

        return jsonify(result_data)

    except Exception as e:
        return jsonify({"status": "ERROR", "reason": str(e)}), 500

def start_engine(task: dict):
    try:
        task_type = TaskType(task["type"])
        target_dir = task["target_directory"]
        repetitions = task["repeat_exploit"]
    except ValueError:
        return {"status": "FORBIDDEN", "reason": f"Invalid task: {task}"}

    try:
        target_directory = get_safe_path(PROGRAMS_DIR, target_dir)
    except Exception as e:
        return {"status": "FORBIDDEN", "reason": f"{e}"}

    try:
        with open(CONFIG_FILE, "r") as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        return {"status": "ERROR", "reason": "Config file missing"}

    if not is_permitted_operation(task_type, config.get("permissions", {})):
        print(f"[SECURITY] Task {task_type} blocked by local policy.")
        return {"status": "FORBIDDEN", "reason": "Consensus rules prevented execution"}

    try:
        report = {
            "status": "SUCCESS",
            "task": task_type,
            "host_info": get_host_state(),
            "binaries_report": analyze_directory(task_type, target_directory, repetitions, config["permissions"].get("max_cpu_usage_per_exploit", "0"))
        }
        return report
    except Exception as e:
        return {"status": "ERROR", "reason": str(e)}

def is_permitted_operation(task: TaskType, permissions: dict):
    can_scan = permissions.get("allow_scanning", False)
    can_exploit = permissions.get("allow_exploitation", False)

    if task == TaskType.SCAN:
        return can_scan
    
    if task == TaskType.EXPLOIT:
        return can_exploit
    
    if task == TaskType.COMPLETE:
        return can_scan and can_exploit
    
    return False

def analyze_directory(task: TaskType, target_dir: Path, repetitions: int, max_cpu_usage_per_exploit: int):
    binaries_report = []
    if not target_dir.exists():
        return []

    for item in target_dir.rglob('*'):
        filepath = Path(item).resolve()
        if is_elf_file(filepath):
            binary_report = {
                "filename": str(Path(filepath).resolve()),
            }

            if task == TaskType.SCAN or task == TaskType.COMPLETE:
                binary_report["protections"] = get_binary_protections(filepath)
            
            if task == TaskType.EXPLOIT or task == TaskType.COMPLETE:
                binary_report["test_result"] = run_exploits(str(filepath), repetitions, max_cpu_usage_per_exploit)
            
            binaries_report.append(binary_report)
            
    return binaries_report

def get_binary_protections(binary_path: str):
    try:
        elf = ELF(binary_path, checksec=False)
        
        file_protections = {
            "aslr": elf.aslr,
            "pie": elf.pie,
            "nx": elf.nx,
            "relro": elf.relro,
            "canary": elf.canary,
        }
        
        return file_protections

    except Exception as e:
        return {"error": str(e)}

# Magic bytes to know if it's a binary file
def is_elf_file(filepath: str):
    if os.path.isfile(filepath): 
        try:
            with open(filepath, 'rb') as f:
                header = f.read(4)
                return header == b'\x7fELF'
        except:
            return False

def get_safe_path(base_directory: str, unsafe_input: str):
    base_path = Path(base_directory).resolve()
    
    clean_input = unsafe_input.lstrip("/")
    
    full_path = (base_path / clean_input).resolve()
    
    if not full_path.is_relative_to(base_path):
        raise PermissionError(f"Blocked access to directory: {unsafe_input}")
    
    return full_path

if __name__ == '__main__':
    # Setup SSL for mTLS
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    
    # Load credentials
    context.load_cert_chain(certfile=SERVER_CERT, keyfile=SERVER_KEY)
    
    # Load CA to verify the requester
    context.load_verify_locations(cafile=CA_CERT)
    
    # Requester must provide a certificate
    context.verify_mode = ssl.CERT_REQUIRED 

    print("[AGENT] Listening on port 5000 (mTLS Enabled)...")
    app.run(host='0.0.0.0', port=5000, ssl_context=context)

#Works for Linux and elf files
