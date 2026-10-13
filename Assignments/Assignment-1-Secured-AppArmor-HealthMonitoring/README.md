# Assignment 1 - Part 2: Secured Multi-Container Python Application with AppArmor and Automated Health Monitoring

## Overview
This project delivers a secured, containerized Flask user authentication application protected by AppArmor security profiles and backed by persistent storage. It features an automated self-healing health monitoring daemon that detects service failures, automatically restarts containers, logs incidents, and dispatches real-time alerts.

## Key Components

1. **Authentication Web Application (`app.py`)**:
   - User registration (`/register`) with hashed passwords using Werkzeug.
   - User authentication (`/login`) with credential validation.
   - Live health probe endpoint (`/health`).
   - Diagnostic failure trigger (`/simulate-failure`) to simulate real-world service crashes for self-healing verification.

2. **Database Persistence**:
   - SQLite user database stored under `/data/users.db`.
   - Persisted across container restarts via dedicated Docker named volume (`auth_user_data`).

3. **AppArmor Security Profile (`flask-security-profile`)**:
   - Enforces kernel-level mandatory access control (MAC).
   - Restricts access to sensitive system paths: `/etc/shadow`, `/etc/sudoers`, `/root/`, `/proc/sys/`.
   - Restricts unauthorized file modification while allowing application networking on port 5000.

4. **Automated Health Monitoring & Alerts (`health_monitor.py`)**:
   - Continuously tests `/health` and `/login` availability.
   - Restarts unhealthy containers automatically.
   - Dispatches visual console alerts with incident counts and timestamps.
   - Logs all events to `health_monitor.log`.

## File Structure
- `app.py`: Flask Authentication service.
- `requirements.txt`: Python package dependencies.
- `Dockerfile`: Container image build specification.
- `docker-compose.yml`: Multi-container configuration.
- `flask-security-profile`: AppArmor security profile.
- `apply_apparmor.py`: Automation script to load profile, start container, and verify enforcement.
- `health_monitor.py`: Daemon monitoring container health, restarting, and alerting.

## Usage Guide

### 1. Build and Run Container with AppArmor
```bash
python apply_apparmor.py
```
Or using Docker Compose:
```bash
docker-compose up --build -d
```

### 2. Run Health & Alert Monitor
```bash
python health_monitor.py
```

### 3. Test Authentication API
```bash
# Register a new user
curl -X POST http://localhost:5000/register \
  -H "Content-Type: application/json" \
  -d '{"username": "devops_student", "password": "SecurePassword123"}'

# Login with valid credentials
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "devops_student", "password": "SecurePassword123"}'

# Login with invalid credentials (returns 401)
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "devops_student", "password": "WrongPassword"}'
```

### 4. Test Automated Self-Healing
Trigger simulated failure:
```bash
curl -X POST http://localhost:5000/simulate-failure
```
Watch the running `health_monitor.py` process detect the unhealthy status, generate a critical alert, restart the container, and log the incident!
