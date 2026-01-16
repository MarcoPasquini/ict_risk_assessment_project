import os
import json
import yaml
from enum import Enum
from pwn import *
from host_state import get_host_state
from exploits import run_exploits

class TaskType(str, Enum):
    SCAN = "SCAN"
    EXPLOIT = "EXPLOIT"
    COMPLETE = "SCAN_AND_EXPLOIT"

class AgentMode(str, Enum):
    ACTIVE = "active_defense"
    PASSIVE = "passive_monitoring"

CONFIG_FILE = Path("agent_config.yaml")

def start_engine(task_type: str, target_dir: str = "."):
    try:
        task = TaskType(task_type)
    except ValueError:
        return {"status": "FORBIDDEN", "reason": f"Invalid task type: {task_type}"}

    try:
        with open(CONFIG_FILE, "r") as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        return {"status": "ERROR", "reason": "Config file missing"}

    if not is_permitted_operation(task, config.get('permissions', {})):
        print(f"[SECURITY] Task {task.value} blocked by local policy.")
        return {"status": "FORBIDDEN", "reason": "Consensus rules prevented execution"}

    try:
        report = {
            "status": "SUCCESS",
            "task": task.value,
            "host_info": get_host_state(),
            "binaries_report": analyze_directory(task, Path(target_dir))
        }
        return report
    except Exception as e:
        return {"status": "ERROR", "reason": str(e)}

def is_permitted_operation(task: TaskType, permissions: dict) -> bool:
    can_scan = permissions.get("allow_scanning", False)
    can_exploit = permissions.get("allow_exploitation", False)

    if task == TaskType.SCAN:
        return can_scan
    
    if task == TaskType.EXPLOIT:
        return can_exploit
    
    if task == TaskType.COMPLETE:
        return can_scan and can_exploit
    
    return False

def analyze_directory(task: TaskType, target_dir: Path):
    binaries_report = []
    
    if not target_dir.exists():
        return []

    for item in target_dir.iterdir():
        filepath = str(item)
        if is_elf_file(filepath):
            
            binary_report = {
                "filename": filepath,
            }

            if task == TaskType.SCAN or task == TaskType.COMPLETE:
                binary_report["protections"] = get_binary_protections(filepath)
            
            if task == TaskType.EXPLOIT or task == TaskType.COMPLETE:
                binary_report["test_result"] = run_exploits(filepath) 
            
            binaries_report.append(binary_report)
            
    return binaries_report

def get_binary_protections(binary_path):
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
def is_elf_file(filepath):
    if os.path.isfile(filepath): 
        try:
            with open(filepath, 'rb') as f:
                header = f.read(4)
                return header == b'\x7fELF'
        except:
            return False


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Invalid command.")
        print("Usage: python assessment_module.py [directory]")
        exit(1)
    else:
        directory = sys.argv[1]

    task_type = "SCAN_AND_EXPLOIT"

    print(json.dumps(start_engine(task_type, directory), indent=4))

#Works for Linux and elf files