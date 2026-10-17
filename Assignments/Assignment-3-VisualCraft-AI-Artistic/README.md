# Assignment 3: VisualCraft - AI Artistic Style Service Deployment & Monitoring

## Overview
**VisualCraft** is an AI-powered art platform that transforms digital images into artistic styles. This project delivers a production-grade DevOps solution to deploy, scale, monitor, and automate the **AI Artistic Style Service** (`urmsandeep/ai-artistic-style-service`) using Docker Compose, Prometheus, Grafana, and CI/CD pipelines (Jenkins & GitHub Actions).

---

## Architecture

```
                       +---------------------------------------+
                       |           User / Client               |
                       +-------------------+-------------------+
                                           | POST /styleTransfer (Port 5001)
                                           v
    +-------------------------------------------------------------------------+
    | Docker Network: visualcraft-net                                         |
    |                                                                         |
    |  +-----------------------------+         +---------------------------+  |
    |  | AI Artistic Style Service   |<--------| Prometheus Server         |  |
    |  | Container: ai-artistic-style| Metrics | Container: prometheus     |  |
    |  | Port: 5001                  |         | Port: 9090                |  |
    |  +-----------------------------+         +-------------+-------------+  |
    |                |                                       |                |
    |                | cAdvisor/Node-Exporter                v                |
    |                +-----------------------> +---------------------------+  |
    |                                          | Grafana Dashboard         |  |
    |                                          | Container: grafana        |  |
    |                                          | Port: 3000                |  |
    |                                          +---------------------------+  |
    +-------------------------------------------------------------------------+
```

---

## File Structure

- `service.py`: AI style transfer application with Prometheus `/metrics` instrumentation.
- `requirements.txt`: Python package requirements.
- `Dockerfile`: Container image build definition with automated health checks.
- `docker-compose.yml`: Multi-container stack (AI Service, Prometheus, Grafana, cAdvisor, Node Exporter).
- `Jenkinsfile`: Multi-stage Jenkins pipeline (Pull Image, Run Tests, Deploy Service, Smoke Test Verification).
- `.github/workflows/deploy.yml`: GitHub Actions CI/CD automation workflow.
- `prometheus/prometheus.yml`: Scrape configurations for AI service and container exporters.
- `grafana/`:
  - `provisioning/datasources/datasource.yml`: Automatic Prometheus datasource provisioning.
  - `provisioning/dashboards/dashboards.yml`: Automatic dashboard loader.
  - `dashboards/api-performance.json`: Preconfigured Grafana dashboard covering API requests, error rates, latency, and CPU/memory.
- `tests/test_api.py`: Pytest automated test suite.
- `resilience_test.py`: Automated fault-injection and self-healing test.
- `load_test.py`: Load generation script to populate Prometheus & Grafana metrics.
- `API-Testing-Report.md`: Full documentation of test results, metrics, and recovery tests.

---

## Quickstart Guide

### 1. Run Automated Test Suite
```bash
pytest tests/ -v
```

### 2. Deploy Entire Stack with Docker Compose
```bash
docker-compose up --build -d
```
Verify running containers:
```bash
docker-compose ps
```

### 3. Test Style Transfer API
Using curl with a sample JPEG image:
```bash
curl -X POST http://127.0.0.1:5001/styleTransfer \
  -F "image=@test.jpg" \
  --output styled_output.jpg
```

### 4. Run Fault-Tolerance Resilience Test
```bash
python resilience_test.py
```

### 5. Generate Load for Grafana Dashboards
```bash
python load_test.py
```

### 6. View Observability Dashboards
- **Grafana**: Open [http://localhost:3000](http://localhost:3000) (Login: `admin` / `admin`).
  - Navigate to Dashboards -> **VisualCraft - AI Artistic Style Service Performance**.
- **Prometheus**: Open [http://localhost:9090](http://localhost:9090) to query PromQL metrics.
