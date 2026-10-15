# Assignment 2: TreasureBook - Graph-Based Adventure Platform

## Overview
**TreasureBook** is a dynamic, graph-based treasure hunt platform inspired by Facebook's TAO (The Associations and Objects) social graph architecture. The platform connects treasures, hidden locations, and mysterious maps as **Nodes** (Objects) and trails, hiding spots, and map leads as **Edges** (Associations).

This project implements the containerized API, Kubernetes manifests with Horizontal Pod Autoscaler (HPA), persistent MongoDB deployment, and traffic simulation scripts.

---

## Architecture & Facebook TAO Analogy

```
   Facebook TAO Concept    =====>   TreasureBook Implementation
   ------------------------------------------------------------
   User                    =====>   Treasure (e.g., "Golden Crown")
   Page                    =====>   Location (e.g., "Cave of Wonders")
   Message                 =====>   Map (e.g., "Mystic Map")
   Friendship              =====>   Trail (connecting Locations)
   Likes                   =====>   Hidden-At (mapping Treasure -> Location)
   Comments                =====>   Leads-to (linking Map -> Treasure)
```

```
                        +---------------------------------------------+
                        |      Kubernetes Service (NodePort 30500)     |
                        +----------------------+----------------------+
                                               |
                  +----------------------------+----------------------------+
                  |                            |                            |
                  v                            v                            v
          +---------------+            +---------------+            +---------------+
          |  Pod Replica  |            |  Pod Replica  |            |  Pod Replica  |
          | treasurebook  |            | treasurebook  | ... up to  | treasurebook  |
          |   (Pod #1)    |            |   (Pod #2)    |  10 pods   |   (Pod #10)   |
          +-------+-------+            +-------+-------+            +-------+-------+
                  |                            |                            |
                  +----------------------------+----------------------------+
                                               |
                                               v
                        +---------------------------------------------+
                        |       MongoDB Deployment & Persistent PVC   |
                        +---------------------------------------------+
```

---

## File Structure

- `app.py`: Flask API implementing Node, Edge, and Graph endpoints.
- `requirements.txt`: Python package requirements.
- `Dockerfile`: Container image build definition.
- `docker-compose.yml`: Local multi-container Docker Compose setup.
- `k8s/`:
  - `mongodb-pvc.yaml` & `mongodb-deployment.yaml`: Persistent MongoDB deployment.
  - `api-deployment.yaml`: TreasureBook API deployment with 3 initial replicas, 100m CPU/256Mi memory requests, 200m CPU/512Mi memory limits.
  - `api-service.yaml`: NodePort Kubernetes Service (port 30500).
  - `api-hpa.yaml`: Kubernetes HPA configuration scaling up to 10 pods when CPU exceeds 5%.
- `simulate_traffic.py`: Multi-threaded load testing script for HPA testing.
- `performance_report.md`: Detailed performance report documenting traffic simulation and scaling metrics.

---

## Deployment Instructions

### 1. Local Testing with Docker Compose
```bash
docker-compose up --build -d
# Access dashboard at http://localhost:5000
```

### 2. Deploy to Minikube / Kubernetes

```bash
# Start Minikube & Enable Metrics Server (Required for HPA)
minikube start
minikube addons enable metrics-server

# Build Docker image inside Minikube's Docker daemon
eval $(minikube docker-env)
docker build -t treasurebook-api:latest .

# Apply Kubernetes Manifests
kubectl apply -f k8s/mongodb-deployment.yaml
kubectl apply -f k8s/api-deployment.yaml
kubectl apply -f k8s/api-service.yaml
kubectl apply -f k8s/api-hpa.yaml

# Verify Deployments & Pods
kubectl get deployments
kubectl get pods -o wide
kubectl get hpa
```

### 3. Expose & Access the API
```bash
minikube service treasurebook-api-service
```

---

## API Usage & Verification

### 1. Create Nodes
```bash
# Create Treasure
curl -X POST http://localhost:5000/node \
  -H "Content-Type: application/json" \
  -d '{"Type": "Treasures", "name": "Golden Crown", "details": "Encrusted with ancient rubies"}'

# Create Location
curl -X POST http://localhost:5000/node \
  -H "Content-Type: application/json" \
  -d '{"Type": "Location", "name": "Cave of Wonders", "details": "Deep inside the desert"}'

# Create Map
curl -X POST http://localhost:5000/node \
  -H "Content-Type: application/json" \
  -d '{"Type": "Map", "name": "Mystic Map", "details": "Glowing parchment"}'
```

### 2. Create Edges
```bash
# Link Treasure to Location (Hidden-At)
curl -X POST http://localhost:5000/edge \
  -H "Content-Type: application/json" \
  -d '{"Type": "Hidden-At", "from_node": "Golden Crown", "to_node": "Cave of Wonders"}'

# Link Locations (Trail)
curl -X POST http://localhost:5000/edge \
  -H "Content-Type: application/json" \
  -d '{"Type": "Trail", "from_node": "Forest of Secrets", "to_node": "Mystic Lake"}'

# Link Map to Treasure (Leads-to)
curl -X POST http://localhost:5000/edge \
  -H "Content-Type: application/json" \
  -d '{"Type": "Leads-to", "from_node": "Mystic Map", "to_node": "Cursed Diamond"}'
```

### 3. Query Graph
```bash
curl -X GET http://localhost:5000/graph
```

---

## Running Traffic Simulation & Observing HPA Autoscaling
```bash
# In terminal 1: Watch HPA and pods scale
kubectl get hpa treasurebook-api-hpa --watch

# In terminal 2: Run the simulation
python simulate_traffic.py http://<MINIKUBE_IP>:30500
```
Review `performance_report.md` for full scaling analysis and graphs!
