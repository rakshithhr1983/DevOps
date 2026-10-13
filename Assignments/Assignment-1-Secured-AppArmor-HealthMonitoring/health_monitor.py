"""
Automated Health Monitor and Alerting System
Periodically verifies health and authentication endpoints of the Flask container.
If the service is unhealthy, automatically restarts the container, logs the incident,
and dispatches high-priority alert notifications.
"""

import docker
import requests
import time
import logging
import os
import sys

# Setup incident logger
LOG_FILE = "health_monitor.log"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def send_alert_notification(container_name, reason, restart_count):
    """Dispatches console alert and alert event notification."""
    alert_banner = f"""
    ╔════════════════════════════════════════════════════════════════╗
    ║                     🚨 CRITICAL ALERT 🚨                      ║
    ╠════════════════════════════════════════════════════════════════╣
    ║ Target Container : {container_name:<43}║
    ║ Timestamp        : {time.strftime('%Y-%m-%d %H:%M:%S'):<43}║
    ║ Incident Reason  : {reason[:43]:<43}║
    ║ Action Taken     : Automatic Container Restart Initiated       ║
    ║ Incident Count   : {restart_count:<43}║
    ║ Status           : Self-Healing Recovery Executed              ║
    ╚════════════════════════════════════════════════════════════════╝
    """
    print(alert_banner)
    logging.warning(f"ALERT DISPATCHED: Container '{container_name}' restarted due to '{reason}'. Total restarts: {restart_count}")

def check_service_health(base_url="http://localhost:5000"):
    # 1. Check health endpoint
    try:
        health_resp = requests.get(f"{base_url}/health", timeout=3)
        if health_resp.status_code != 200:
            return False, f"Health check failed with status code {health_resp.status_code}"
    except requests.exceptions.RequestException as e:
        return False, f"Health endpoint unreachable: {e}"

    # 2. Check login service endpoint responsiveness
    try:
        login_resp = requests.post(f"{base_url}/login", json={"username": "probe_user", "password": "wrong_password"}, timeout=3)
        # Expected status: 401 Unauthorized (service is active and responding)
        if login_resp.status_code not in [200, 401, 404]:
            return False, f"Login service returned unexpected status {login_resp.status_code}"
    except requests.exceptions.RequestException as e:
        return False, f"Login service endpoint unreachable: {e}"

    return True, "Service is healthy and fully responsive"

def run_monitor(container_name="secured-auth-app", interval=5, max_cycles=6):
    client = docker.from_env()
    print("=" * 65)
    print(f"🛡️  Automated Health & Incident Monitor started for: {container_name}")
    print(f"Logging events to: {os.path.abspath(LOG_FILE)}")
    print("=" * 65)

    restarts = 0
    cycle = 0

    while cycle < max_cycles:
        cycle += 1
        print(f"\n[Cycle #{cycle}/{max_cycles}] Checking container health...")

        try:
            container = client.containers.get(container_name)
        except docker.errors.NotFound:
            print(f"[-] Container '{container_name}' not found. Waiting...")
            time.sleep(interval)
            continue

        is_healthy, message = check_service_health()

        if is_healthy:
            print(f"  [+] Healthy: {message}")
            logging.info(f"Health check OK: {message}")
        else:
            restarts += 1
            print(f"  [-] UNHEALTHY: {message}")
            send_alert_notification(container_name, message, restarts)

            print(f"  [🔄] Restarting container '{container_name}'...")
            try:
                container.restart(timeout=10)
                print(f"  [+] Container restarted successfully.")
                logging.info(f"Container '{container_name}' successfully restarted.")
                time.sleep(3) # allow app to rebind port
            except Exception as e:
                print(f"  [-] Failed to restart container: {e}")
                logging.error(f"Restart failed: {e}")

        time.sleep(interval)

    print("\n[✔] Automated Health Monitor session finished.")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "secured-auth-app"
    run_monitor(container_name=target)
