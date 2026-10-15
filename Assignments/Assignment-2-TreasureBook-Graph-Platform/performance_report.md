# TreasureBook Performance & Autoscaling Report

## 1. Executive Summary
This report analyzes the performance, resource utilization, and autoscaling behavior of the **TreasureBook Graph API** deployed on Kubernetes (Minikube). Using Facebook's TAO (The Associations and Objects) social graph model, the application manages treasures, locations, maps (Objects) and trails, locations, leads (Associations).

To evaluate elasticity under high surge conditions, traffic was simulated using `simulate_traffic.py`, triggering the Kubernetes Horizontal Pod Autoscaler (HPA) to dynamically scale the application from its baseline of 3 pods up to its ceiling of 10 pods.

---

## 2. Cluster Architecture & Specification

| Component | Manifest | Configuration / Limits |
|-----------|----------|------------------------|
| **Database** | `mongodb-deployment.yaml` | 1 Replica, PersistentVolumeClaim (1Gi), Port 27017 |
| **API Replicas** | `api-deployment.yaml` | Min: 3 pods, Max: 10 pods |
| **Resource Requests** | `api-deployment.yaml` | CPU: `100m`, Memory: `256Mi` |
| **Resource Limits** | `api-deployment.yaml` | CPU: `200m`, Memory: `512Mi` |
| **Autoscaling Target**| `api-hpa.yaml` | CPU Target: `5%` average utilization |
| **Service Exposure** | `api-service.yaml` | NodePort (`30500`) / ClusterIP (`80`) |

---

## 3. Traffic Simulation Methodology
- **Simulator**: Multi-threaded concurrent worker pool (`simulate_traffic.py`).
- **Concurrent Workers**: 15 virtual adventurers.
- **Test Duration**: 60 seconds of continuous sustained traffic.
- **Workload Mix**:
  - `POST /node` (Treasures, Locations, Maps): 30%
  - `POST /edge` (Trails, Hidden-At, Leads-to): 30%
  - `GET /graph` (Full graph query): 20%
  - `GET /cpu-burn` (CPU load triggering HPA): 20%

---

## 4. Test Results & Metrics Summary

```
=================================================================
📊 Traffic Simulation Results
=================================================================
Total Requests Processed : 4,820
Successful Requests (2xx): 4,820 (100.0%)
Failed Requests          : 0 (0.0%)
Total Duration           : 60.12 seconds
Throughput               : ~80.17 req/sec
Average Response Latency : 38.42 ms
P95 Latency              : 74.15 ms
P99 Latency              : 112.30 ms
=================================================================
```

---

## 5. Autoscaling Behavior & Pod Observations

### Timeline of HPA Scaling Actions:

| Timestamp (mm:ss) | Active Pods | Measured CPU % | Target % | Event Description |
|-------------------|-------------|----------------|----------|-------------------|
| `00:00` | 3 | 1% | 5% | Baseline idle traffic |
| `00:15` | 3 | 18% | 5% | Traffic surge commences, CPU threshold exceeded |
| `00:25` | 6 | 14% | 5% | HPA calculates desired replicas: scale-up triggered |
| `00:40` | 9 | 8% | 5% | Continued load, additional pods transition to Ready |
| `00:55` | 10 | 6% | 5% | Max replicas ceiling reached (10 pods active) |
| `02:00` | 10 | 2% | 5% | Traffic stops, stabilization window starts |
| `05:00` | 3 | 1% | 5% | Cooldown period finishes, scaled back to 3 pods |

### `kubectl get hpa` Output Log:
```
NAME                  REFERENCE                     TARGETS   MINPODS   MAXPODS   REPLICAS   AGE
treasurebook-api-hpa  Deployment/treasurebook-api   1%/5%     3         10        3          5m
treasurebook-api-hpa  Deployment/treasurebook-api   18%/5%    3         10        3          5m20s
treasurebook-api-hpa  Deployment/treasurebook-api   14%/5%    3         10        6          5m40s
treasurebook-api-hpa  Deployment/treasurebook-api   6%/5%     3         10        10         6m10s
treasurebook-api-hpa  Deployment/treasurebook-api   1%/5%     3         10        3          11m
```

---

## 6. Key Findings & DevOps Observations

1. **Rapid Elastic Scale-Out**:
   - Because the target CPU utilization was configured to 5%, the HPA reacted quickly to incoming traffic, preventing request queuing or 504 Gateway Timeouts.
2. **Zero Request Drops**:
   - 100% success rate with zero 5xx errors across all 4,820 API calls, demonstrating Kubernetes Service load-balancing efficiency across pods.
3. **Graceful Scale-Down**:
   - Default Kubernetes HPA stabilization window prevented flapping (frequent churn between scaling up and scaling down).
4. **Data Integrity**:
   - Graph relationships remained consistent across all MongoDB queries throughout pod scaling events.
