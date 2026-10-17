# VisualCraft AI Artistic Style Service - API Testing & Monitoring Report

## 1. Executive Summary
This report documents the containerization, deployment, resilience verification, and telemetry monitoring of the **VisualCraft AI Artistic Style Service** (`urmsandeep/ai-artistic-style-service:latest`). The system was deployed using Docker Compose alongside Prometheus and Grafana for full observability.

---

## 2. API Testing Results

### Test Execution: `POST /styleTransfer`
- **Method**: `POST`
- **Endpoint**: `http://127.0.0.1:5001/styleTransfer`
- **Headers**: `Content-Type: multipart/form-data`
- **Payload**: `image=@bmsce.jpg`

### Curl Request & Console Output
```bash
curl -X POST http://127.0.0.1:5001/styleTransfer \
  -F "image=@bmsce.jpg" \
  --output styled_output.jpg
```

```
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100 59829  100 25217  100 34612  89548   120k --:--:-- --:--:-- --:--:--  207k
```

### Response Verification
```bash
file styled_output.jpg
# Output: styled_output.jpg: JPEG image data, JFIF standard 1.01, aspect ratio, density 1x1, 400x300, components 3
```

- **HTTP Status Code**: `200 OK`
- **Content-Type**: `image/jpeg`
- **Input Image**: `bmsce.jpg` (400x300 JPEG)
- **Output Image**: `styled_output.jpg` (Transformed artistic style rendered)

---

## 3. Resilience & Self-Healing Testing

### Objective
Verify that the service maintains high availability and automatically restarts upon process termination or sudden failure.

### Simulation Command & Log
```bash
python resilience_test.py
```

```
=================================================================
🛡️ VisualCraft Resilience & Self-Healing Test
=================================================================
[*] Step 1: Checking baseline service availability...
  ✅ Baseline service responding at http://127.0.0.1:5001/health

[*] Step 2: Simulating failure for container 'ai-artistic-style'...
  [+] Successfully killed container 'ai-artistic-style' via docker kill.

[*] Step 3: Verifying automated recovery (waiting for Docker daemon restart)...
  [Attempt 1/14] Probing http://127.0.0.1:5001/health... (Connection refused)
  [Attempt 2/14] Probing http://127.0.0.1:5001/health...
  ✅ Service recovered and responding healthy!

=================================================================
🎉 RESILIENCE TEST PASSED: Container self-healed and recovered!
=================================================================
```

---

## 4. Observability & Monitoring Dashboards

Telemetry is captured via Prometheus at `http://localhost:9090` and displayed on Grafana at `http://localhost:3000`.

### Dashboard Overview: `VisualCraft - API Performance` (`visualcraft-api-perf`)

| Panel Name | Metric / PromQL Query | Description |
|------------|------------------------|-------------|
| **Panel 1: Total API Requests** | `sum by (status_code) (api_requests_total)` | Total calls to `/styleTransfer` broken down by status codes (200, 400, 500) |
| **Panel 2: Request Rate** | `sum(rate(api_requests_total[1m]))` | Throughput rate in requests per second |
| **Panel 3: API Response Latency** | `histogram_quantile(0.95, sum(rate(api_request_duration_seconds_bucket[1m])) by (le))` | P95 and Average latency for transformation pipeline |
| **Panel 4: CPU Usage** | `sum(rate(container_cpu_usage_seconds_total{name=~"ai-artistic-style.*"}[1m])) * 100` | Percentage CPU utilization of the AI container |
| **Panel 5: Memory Usage** | `sum(container_memory_usage_bytes{name=~"ai-artistic-style.*"}) / 1024 / 1024` | Real-time RAM consumption in Megabytes |

---

## 5. Automated CI/CD Pipeline Summary

- **Trigger**: Code push or PR to `main` branch.
- **Stage 1**: Pull latest image from Docker Hub (`urmsandeep/ai-artistic-style-service:latest`).
- **Stage 2**: Run automated pytest unit & integration tests (`pytest tests/`).
- **Stage 3**: Deploy stack with Docker Compose (`docker-compose up -d`).
- **Stage 4**: Verify deployment readiness via health probes and smoke test image transformation.
- **Post Cleanup**: Automatic prune of dangling containers and build artifacts.
