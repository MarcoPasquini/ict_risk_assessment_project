# ICT Risk Assessment Project

## Security Digital Twin: Active Monitoring Agent

Extension of the ICT Infrastructure Security Twin

## Overview

This software is the **Active Monitoring Module** designed for the Security Digital Twin framework. While the original Twin architecture focused on passive network monitoring to model ICT infrastructure, this extension introduces **host-level active verification**.

The Agent is designed to run on authorized target hosts (inside specific VM snapshots). It performs two critical tasks to refine the Twin's probabilistic models:

1.  **Static Analysis:** Scans binaries to extract Control-Flow Integrity (CFI) protections (ASLR, DEP/NX, PIE, Canary, RelRO).
2.  **Active Exploitation:** Executes controlled exploits against local binaries to empirically measure the probability of success (`p_hat`).

The data collected is sent securely to the Central Twin to update Bayesian priors regarding the system's resilience.

---

## Key Features

* **Static Detector:** Automatically parses ELF headers using `checksec` function of the module `pwntools` to detect security mitigations (`RELRO`, `Stack Canary`, `NX`, `PIE`).
* **Active & Safe Exploitation:** Supports controlled execution of exploit scripts to validate theoretical vulnerabilities.
* **Local Consensus Rules:** Implements a strict **"Opt-in" policy**. The Agent refuses to execute invasive tasks unless explicitly authorized via a local, root-protected configuration file (`agent_config.yaml`).
* **Secure Communication:** Telemetry and commands are transmitted over a secure channel to ensure authenticity.
* **Resource Control:** The usage of the CPU in the execution of exploit scripts can be limited in the configuration file to prevent experimental exploits from causing Denial of Service (DoS) on the host.

---



## Architecture

The system operates in a closed loop to calculate the empirical probability of success (`p_hat`).

### The Assessment Loop
1.  **Request:** The Twin Server sends a secure command (static scan, active exploit or both) to the local module targeting a specific directory where the binary to test are located.
2.  **Validation:** The Agent verifies the signature and checks `agent_config.yaml` for authorization.
3.  **Execution:** For every binary in the directory, the module finds and runs the valid exploits N times (as requested by the Twin). Before every exploit run, the snapshot is restored to reset the VM to a clean state.
4.  **Report:** JSON result is sent to the Twin to update the probabilities. It is provided a possible function to update the risk_score.

#### Report Example
In the `output_example.json` file is an example of the JSON transmitted to the Twin.

---
## Installation & Setup

### 1. Requirements
* **Host OS:** Linux (Debian/Ubuntu)
* **Hypervisor:** VirtualBox
* **Python:** 3.8+
* **Privileges:** Root access is required to read protected configs and manage processes.

### 2. Quick Start

Clone the repository and set up the environment:

```bash
git clone https://github.com/MarcoPasquini/ict_risk_assessment_project.git
cd ict_risk_assessment_project

# Create Virtual Environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Security Configuration (mTLS)
Generate the Certificate Authority (CA) and sign keys for both the Host Agent and the Twin Server.

```bash
chmod +x scripts/generate_certs.sh
./scripts/generate_certs.sh
```
Artifacts will be stored in the certs/ directory.

### 4. Agent Configuration
The behavior is governed by agent_config.yaml. For security, restrict access to root only.

```bash
sudo chown root:root agent_config.yaml
sudo chmod 600 agent_config.yaml
```

## Usage

### Step 1: Start the Host Agent (Server)
This service runs on the host machine, listening for commands.

```bash
python3 src/assessment_module/assessment_module.py
```

### Step 2: Trigger a Task
Send a command from the controller to the agent.

```bash
# Syntax: python3 twin_server.py [TASK_TYPE] [TARGET_DIR] [REPETITIONS]
python3 src/twin_server/twin_server.py SCAN_AND_EXPLOIT logging_system 3
```

## Experimental Environment Setup

To validate the active monitoring module and the impact of protections on exploit success rates (`p_hat`), a specific experimental setup has been designed.

### 1. Target Vulnerabilities
**4 custom vulnerable programs**, each exhibiting a different class of weakness (documented in the source code comments).
* **Memory Corruption:** Three programs contain standard memory safety issues (e.g., Buffer Overflow, Format String).
* **Logic Vulnerability:** One program contains a design flaw (logic error). This specific test case was included to demonstrate that standard memory mitigations (ASLR, DEP, Canary) are ineffective against non-memory-related programming errors.

### 2. Success Criterion (The Marker)
To automate the verification of exploits, each target program includes a specific `marker()` function.
* A successful exploit must hijack the control flow to execute this function.
* The `marker()` function terminates the process with a specific **exit code: 11**.
* The experiment runner monitors this exit code to count a "Success" trial.

### 3. Compilation Variants (Protection Tiers)
To measure the efficacy of system hardening, each vulnerable program is compiled in three distinct variations representing different security postures.

| Tier | Description | Compilation Flags (GCC) |
| :--- | :--- | :--- |
| **Low** | No protections active. Vulnerable to classic stack smashing and code injection. | `gcc -z execstack -fno-stack-protector -no-pie -z norelro bin.c -o bin-low` |
| **Medium** | **Stack protection** enabled. Prevents simple linear stack overflows and executable stack. | `gcc -fstack-protector-all -no-pie -z norelro bin.c -o bin-medium` |
| **High** | **Stack protection + PIE + RELRO**. Randomized binary address space and read-only relocation table. | `gcc -fstack-protector-all -pie -z relro bin.c -o bin-high` |

### 4. Virtual Machine Setup

* **Install & Setup VirtualBox**: After installing VirtualBox an Ubuntu Server machine is created.
* **Setup Machine**: All necessary packets and libraries are installed, port forwarding is setted up to enable SSH connection.
* **Snapshot creation**: Creating a snapshot "ReadyState".
