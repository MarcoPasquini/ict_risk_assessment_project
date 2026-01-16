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

## Installation & Prerequisites

### Requirements
* **OS:** Linux (Tested on Debian/Ubuntu)
* **Python:** 3.8+
* **Privileges:** Root access is required to read protected configs and manage processes.

### Dependencies
Install the required Python packages:

```bash
pip install -r requirements.txt
```

## Configuration
The Agent's behavior is governed by the configuration file `agent_config.yaml`. To ensure security and anti-reconnaissance, this file must be owned by root and set to mode 600.

```bash
sudo chown root:root agent_config.yaml
sudo chmod 600 agent_config.yaml
```

## Calculation of p_hat
To calculate `p_hat` (empirical probability), the Agent orchestrates the following loop:

* **Request**: The Twin sends the command to the local module, which can be only the static scan, the active exploitation or both. The command includes the directory where the binary to test are located.
* **Check**: The module verifies `agent_config.yaml` locally.
* **Execute**: For every binary in the directory, the module finds and runs the valid exploits N times (as requested by the Twin). Before every exploit run, the snapshot is restored to reset the VM to a clean state.
* **Report**: JSON result is sent to the Twin.
* **Update**: The twin updates the probabilities.

#### Report Example
In the `output_example.json` file is an example of the JSON transmitted to the Twin.

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


## to-do:
* **Virtual Environment**: Setting up the virtual environment, with snapshot, in which to have vulnerable programs and exploits.
* **Twin module**: Implement the twin module that receives the JSON report.
* **Secure Communication**: Create a secure communiaction channel with **Mutual TLS (mTLS)**, ensuring that only the authenticated Twin Server can command the Agent.
* **CPU usage limitation**: The VM must limit the usage of CPU to prevent DoS.
* **Updating probabilities**: The Twin must update the probabilities based on the result of the local module report.





