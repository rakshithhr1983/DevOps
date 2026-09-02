# Exercise 1: Kubernetes Getting Started - Hello Pod (Zepto Storefront)

## Scenario: Zepto 10-Minute Delivery Storefront
As a DevOps engineer at Zepto, you are tasked with deploying a lightweight web application that serves the customer storefront and real-time delivery status page. This exercise demonstrates how to deploy, manage, and expose your first containerized application using Kubernetes and Minikube.

---

## Architecture Overview

```
                      +------------------------------------------+
                      |         Developer / Web Browser          |
                      +--------------------+---------------------+
                                           | http://<NodeIP>:30080
                                           v
    +--------------------------------------------------------------------+
    | Minikube Cluster                                                   |
    |                                                                    |
    |   +------------------------------------------------------------+   |
    |   | NodePort Service: hello-k8s (Port 80 -> NodePort 30080)     |   |
    |   +------------------------------+-----------------------------+   |
    |                                  |                                 |
    |                                  v                                 |
    |   +------------------------------------------------------------+   |
    |   | Pod: hello-k8s                                             |   |
    |   | Container: nginx:latest (Port 80)                          |   |
    |   | Volume Mount: /usr/share/nginx/html                        |   |
    |   |   from ConfigMap: zepto-storefront-html                    |   |
    |   +------------------------------------------------------------+   |
    +--------------------------------------------------------------------+
```

---

## File Deliverables

- `pod.yaml`: Declarative Pod specification for `hello-k8s` running Nginx on port 80.
- `service.yaml`: Declarative NodePort Service exposing port 80 to nodePort 30080.
- `configmap.yaml`: ConfigMap mounting a custom Zepto storefront & delivery tracking web page into Nginx.
- `deploy.sh`: Automated deployment script for Bash / Linux / macOS / WSL.
- `deploy.ps1`: Automated deployment script for Windows PowerShell.

---

## Step-by-Step Execution Guide

### Method 1: Imperative CLI Approach (Quick Run)
As described in the lab instructions:
```bash
# 1. Start Minikube
minikube start

# 2. Run the Nginx Pod
kubectl run hello-k8s --image=nginx --port=80

# 3. Verify Pod Status
kubectl get pods

# 4. Expose the Pod as a NodePort Service
kubectl expose pod hello-k8s --type=NodePort --port=80

# 5. Access the Service
minikube service hello-k8s
```

### Method 2: Declarative Manifest Approach (Production Best Practice)
```bash
# Apply ConfigMap, Pod, and Service
kubectl apply -f configmap.yaml
kubectl apply -f pod.yaml
kubectl apply -f service.yaml

# Verify resources
kubectl get pods -l app=zepto-storefront
kubectl get svc hello-k8s

# Launch browser
minikube service hello-k8s
```

### Method 3: One-Click Automated Script
- **Linux / macOS / WSL**:
  ```bash
  chmod +x deploy.sh
  ./deploy.sh
  ```
- **Windows PowerShell**:
  ```powershell
  .\deploy.ps1
  ```

---

## Verification & Diagnostic Commands
```bash
# View detailed Pod metadata and lifecycle events
kubectl describe pod hello-k8s

# View Nginx access logs
kubectl logs hello-k8s

# Port-forward directly to localhost (alternative access)
kubectl port-forward pod/hello-k8s 8080:80
```
