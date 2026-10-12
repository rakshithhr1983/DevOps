"""
Container Management and Automated Health Monitor Script
Lists all active containers, monitors health of the Flask application,
and automatically restarts it if unhealthy.
"""

import docker
import time
import requests
import sys

def list_active_containers(client):
    print("\n📋 --- Active Docker Containers ---")
    containers = client.containers.list()
    if not containers:
        print("  No running containers found.")
        return []
    for c in containers:
        print(f"  - [{c.short_id}] {c.name:<25} Image: {c.image.tags[0] if c.image.tags else c.image.short_id:<25} Status: {c.status}")
    return containers

def check_flask_health(app_url="http://localhost:5000/health"):
    try:
        response = requests.get(app_url, timeout=3)
        if response.status_code == 200:
            data = response.json()
            return True, f"HTTP 200 OK - DB Status: {data.get('database')}"
        return False, f"HTTP Status {response.status_code}"
    except requests.exceptions.RequestException as e:
        return False, f"Connection Failed: {e}"

def monitor_and_manage_container(container_name="devops-crud-app", check_interval=5, max_checks=6):
    client = docker.from_env()

    print("=" * 60)
    print("🛡️ Docker Container Health Monitor & Auto-Recovery")
    print("=" * 60)

    # 1. List active containers
    list_active_containers(client)

    # 2. Check health loop
    print(f"\n🔍 Monitoring container '{container_name}' every {check_interval}s...")
    checks_performed = 0

    while checks_performed < max_checks:
        checks_performed += 1
        print(f"\n[Check #{checks_performed}/{max_checks}] Checking health at {time.strftime('%Y-%m-%d %H:%M:%S')}...")

        try:
            container = client.containers.get(container_name)
        except docker.errors.NotFound:
            print(f"❌ Container '{container_name}' not found!")
            time.sleep(check_interval)
            continue

        is_healthy, reason = check_flask_health()

        if is_healthy:
            print(f"  ✅ Container is HEALTHY. ({reason})")
        else:
            print(f"  ⚠️ Container is UNHEALTHY! Reason: {reason}")
            print(f"  🔄 Initiating automatic restart for container '{container.name}'...")
            try:
                container.restart(timeout=10)
                print(f"  ✅ Container '{container.name}' restarted successfully!")
            except Exception as e:
                print(f"  ❌ Failed to restart container: {e}")

        time.sleep(check_interval)

    print("\n🏁 Health monitoring session completed.")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "devops-crud-app"
    monitor_and_manage_container(container_name=target)
