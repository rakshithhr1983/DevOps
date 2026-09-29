"""
Helper Script to Automatically Retrieve Jenkins Initial Admin Password
Inspects the running 'jenkins' Docker container and reads the secret key.
"""

import subprocess
import time
import sys

CONTAINER_NAME = "jenkins"

def get_jenkins_password():
    print(f"[*] Querying container '{CONTAINER_NAME}' for initial admin password...")
    cmd = ["docker", "exec", CONTAINER_NAME, "cat", "/var/jenkins_home/secrets/initialAdminPassword"]

    for attempt in range(1, 20):
        try:
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode == 0 and res.stdout.strip():
                pwd = res.stdout.strip()
                print("\n" + "=" * 65)
                print("🔑 JENKINS INITIAL ADMIN PASSWORD")
                print("=" * 65)
                print(f"  Password : {pwd}")
                print("  URL      : http://localhost:8080")
                print("=" * 65)
                return pwd
        except Exception:
            pass

        print(f"  [Attempt {attempt}/20] Jenkins is initializing, waiting 3 seconds...")
        time.sleep(3)

    print("[-] Could not retrieve password automatically. Ensure the Jenkins container is running:")
    print("    docker ps -a")
    return None

if __name__ == "__main__":
    get_jenkins_password()
