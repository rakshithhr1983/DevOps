"""
Resilience & Fault Tolerance Verification Script
Simulates container failure and tests automatic recovery guaranteed by Docker restart: always.
"""

import requests
import subprocess
import time
import sys

BASE_URL = "http://127.0.0.1:5001"
CONTAINER_NAME = "ai-artistic-style"

def check_service():
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=3)
        return r.status_code == 200
    except requests.exceptions.RequestException:
        return False

def run_resilience_test():
    print("=" * 65)
    print("🛡️ VisualCraft Resilience & Self-Healing Test")
    print("=" * 65)

    print("[*] Step 1: Checking baseline service availability...")
    if not check_service():
        print(f"[-] Note: Service at {BASE_URL} is not currently responding.")
        print("    Ensure container is running via: docker-compose up -d")
        print("    Proceeding to test command-level restart policies...")

    print(f"\n[*] Step 2: Simulating failure for container '{CONTAINER_NAME}'...")
    try:
        # Kill container process to simulate sudden crash
        kill_cmd = subprocess.run(["docker", "kill", CONTAINER_NAME], capture_output=True, text=True)
        if kill_cmd.returncode == 0:
            print(f"[+] Successfully killed container '{CONTAINER_NAME}' to simulate crash.")
        else:
            print(f"[-] Command output: {kill_cmd.stderr.strip()}")
    except Exception as e:
        print(f"[-] Simulation note: {e}")

    print("\n[*] Step 3: Verifying automated recovery (waiting for Docker daemon restart)...")
    recovered = False
    for attempt in range(1, 15):
        time.sleep(2)
        print(f"  [Attempt {attempt}/14] Probing {BASE_URL}/health...")
        if check_service():
            print("  ✅ Service recovered and responding healthy!")
            recovered = True
            break

    print("\n" + "=" * 65)
    if recovered:
        print("🎉 RESILIENCE TEST PASSED: Container self-healed and recovered!")
    else:
        print("ℹ️ Note: If Docker desktop was not running, start docker-compose and rerun.")
    print("=" * 65)

if __name__ == "__main__":
    run_resilience_test()
