# Exercise 7: Jenkins CI Automation - Setup and Quickstart

## Overview
Continuous Integration (CI) is a foundational DevOps practice where developers frequently merge code changes into a central repository, triggering automated builds, tests, and checks to catch errors early.

This exercise covers:
- Core CI concepts, architecture, and tool comparisons.
- Containerized Jenkins LTS server deployment with persistent storage.
- Automating initial admin password retrieval and web console unlock.

---

## File Deliverables

- `docker-compose.yml`: Multi-container specification running Jenkins LTS with persistent volume (`jenkins_home`) and Docker socket access.
- `setup_jenkins.sh`: Automated deployment script for Linux/macOS/WSL.
- `setup_jenkins.ps1`: Automated deployment script for Windows PowerShell.
- `get_admin_password.py`: Automation script to query Docker and extract the initial admin unlock password.
- `ci_tools_comparison.md`: Detailed feature and architectural comparison of 10 modern CI tools.

---

## Deployment & Setup Instructions

### 1. Launch Jenkins Container

#### Option A: Using Docker Compose (Recommended)
```bash
docker-compose up -d
```

#### Option B: Using Standalone Docker CLI
```bash
docker run -d \
  --name jenkins \
  -p 8080:8080 \
  -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  jenkins/jenkins:lts
```

---

### 2. Retrieve Initial Admin Password

Run the automated helper:
```bash
python get_admin_password.py
```
Or directly inspect the container:
```bash
docker exec -it jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

---

### 3. Complete Initial Jenkins Web Setup

1. Open your browser and navigate to: **[http://localhost:8080](http://localhost:8080)**.
2. In the **Unlock Jenkins** screen, paste the password retrieved in Step 2.
3. Click **Install Suggested Plugins** to install Git, Pipeline, and standard build plugins.
4. Create your primary Admin User (or continue as admin).
5. Confirm the Jenkins URL and click **Start using Jenkins**!
