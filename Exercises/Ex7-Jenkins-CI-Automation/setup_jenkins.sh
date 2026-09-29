#!/bin/bash
# Exercise 7: Jenkins CI Automation Setup Script

set -e

echo "=========================================================="
echo "🚀 Exercise 7: Launching Jenkins Automation Server"
echo "=========================================================="

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "[-] Error: Docker daemon is not running. Please start Docker."
    exit 1
fi

echo "[*] Step 1: Starting Jenkins container via Docker Compose..."
docker-compose up -d

echo "[*] Step 2: Waiting for Jenkins to start up and generate secrets..."
sleep 10

echo "[*] Step 3: Extracting initial admin password..."
python3 get_admin_password.py || python get_admin_password.py || docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword

echo ""
echo "=========================================================="
echo "✅ Jenkins is accessible at: http://localhost:8080"
echo "=========================================================="
