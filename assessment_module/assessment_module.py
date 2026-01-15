import os
import json
from pwn import *
from host_state import get_host_state
from exploits import run_exploits


def start_engine(dir):
    host_state = get_host_state()
    report = {
        "host_info": get_host_state(),
        "binaries_report": analyze_directory(dir)
    }
    return json.dumps(report, indent=4)


def analyze_directory(dir="."):
    binaries_report = []
    for filename in os.listdir(dir):
        filepath = os.path.join(dir, filename)

        if is_elf_file(filepath):

            binary_report = {
                "filename": filepath,
                "protections": get_binary_protections(filepath),
                "test_result": run_exploits(filepath)
            }

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

if len(sys.argv) != 2:
    print("Invalid command.")
    print("Usage: python assessment_module.py [directory]")
    exit(1)
else:
    directory = sys.argv[1]

print(start_engine(directory))

#Funziona per linux e file eseguibili elf.
