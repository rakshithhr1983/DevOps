# Assignment 1: Dockerized Multi-Container Web Application with Networking and Container Management

## Overview
This project implements a complete, containerized Python Flask CRUD web application with a MongoDB backend, custom Docker bridge networking, and programmatic container and network management using the Docker SDK for Python.

## Architecture

```
                      +---------------------------------------+
                      |       Host Machine / Web Browser      |
                      +-------------------+-------------------+
                                          | http://localhost:5000
                                          v
      +-----------------------------------------------------------------------+
      | Custom Bridge Network: devops_bridge_net (172.28.0.0/16)              |
      |                                                                       |
      |  +---------------------------+        +----------------------------+  |
      |  | Flask Web Application     |        | MongoDB Database Container |  |
      |  | Container: devops-crud-app|=======>| Container: devops-mongo-db |  |
      |  | Port: 5000:5000           |        | Port: 27017:27017          |  |
      |  +---------------------------+        +-------------+--------------+  |
      |                                                     |                 |
      +-----------------------------------------------------|-----------------+
                                                            v
                                              +----------------------------+
                                              | Persistent Docker Volume   |
                                              | Name: devops_mongo_data    |
                                              | Mount: /data/db            |
                                              +----------------------------+
```

## Features
- **Flask CRUD Web App**: RESTful JSON API and web dashboard supporting Create, Read, Update, and Delete operations.
- **Data Persistence**: MongoDB running in an isolated container with data persisted using a dedicated named Docker volume (`devops_mongo_data`).
- **Custom Docker Bridge Network**: Programmatic network creation with custom IPAM (subnets, gateways) via Docker SDK for Python.
- **Automated Health Monitoring**: Periodic health-checking daemon that inspects container and app health (`/health`), restarting the service if unhealthy.
- **Docker SDK for Python**: All deployment, networking, and container management can be executed via pure Python scripts.

## File Structure
- `app.py`: Flask web application with CRUD endpoints and health check.
- `requirements.txt`: Python dependencies (`flask`, `pymongo`).
- `Dockerfile`: Multi-stage, production-ready container definition with built-in health check.
- `docker-compose.yml`: Compose specification for declarative service and network management.
- `manage_network.py`: Python script using Docker SDK to create and inspect custom bridge networks.
- `container_manager.py`: Python script monitoring container health with automatic self-healing/restart.
- `deploy_with_sdk.py`: Automated orchestration script using Docker Python SDK.

## How to Run

### Method 1: Using Docker Compose
```bash
# Build and start services in the background
docker-compose up --build -d

# Check running services
docker-compose ps

# View logs
docker-compose logs -f
```

### Method 2: Using the Python Docker SDK
```bash
python deploy_with_sdk.py
```

### Network Inspection & Management
```bash
python manage_network.py
```

### Automated Container Health Monitoring
```bash
python container_manager.py
```

## Testing CRUD Endpoints

### 1. Health Check
```bash
curl -X GET http://localhost:5000/health
```

### 2. Create an Item
```bash
curl -X POST http://localhost:5000/api/items \
  -H "Content-Type: application/json" \
  -d '{"title": "DevOps Lab Item 1", "description": "Persistent storage test"}'
```

### 3. List All Items
```bash
curl -X GET http://localhost:5000/api/items
```

### 4. Update an Item
```bash
curl -X PUT http://localhost:5000/api/items/<ITEM_ID> \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated Item Title"}'
```

### 5. Delete an Item
```bash
curl -X DELETE http://localhost:5000/api/items/<ITEM_ID>
```
