import subprocess
import time
import paramiko

# --- VM Config ---
VM_NAME = "SecurityTwin_Lab"
SNAPSHOT_NAME = "ReadyState"
SSH_HOST = "127.0.0.1"
SSH_PORT = 2222
SSH_USER = "ubuntu"
PASSWORD = "labpassword"
REMOTE_DIR = "/home/ubuntu/target_zone"

def restore_snapshot():
    print(" -  Restoring snapshot...")
    subprocess.run(["VBoxManage", "controlvm", VM_NAME, "poweroff"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1)
    subprocess.run(["VBoxManage", "snapshot", VM_NAME, "restore", SNAPSHOT_NAME], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def start_vm(cpu_limit_percent: int):
    print(" -  Starting VM...")
    subprocess.run(["VBoxManage", "modifyvm", VM_NAME, "--cpuexecutioncap", str(cpu_limit_percent)], check=True)
    subprocess.run(["VBoxManage", "startvm", VM_NAME, "--type", "headless"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def wait_for_ssh():
    print(" -  Waiting SSH connection...", end="", flush=True)
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    while True:
        try:
            client.connect(SSH_HOST, port=SSH_PORT, username=SSH_USER, password=PASSWORD, timeout=2)
            print("\n -  Connected to the VM")
            return client
        except:
            print(".", end="", flush=True)
            time.sleep(2)

def upload_and_prepare(ssh_client, local_file: str, remote_file: str):
    sftp = ssh_client.open_sftp()
    
    print(f" -  Uploading {local_file} -> {remote_file}")
    sftp.put(local_file, remote_file)
    sftp.close()
    
    print(" -  Setting executable permissions...")
    ssh_client.exec_command(f"chmod +x {remote_file}")