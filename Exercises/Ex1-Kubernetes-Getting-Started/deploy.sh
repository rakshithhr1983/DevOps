#!/bin/bash
# Exercise 1: Kubernetes Getting Started - Automated Deployment Script

set -e

echo "=========================================================="
echo "🚀 Exercise 1: Deploying Zepto Storefront Pod on Minikube"
echo "=========================================================="

# 1. Check Minikube Status
echo "[*] Step 1: Checking Minikube status..."
if ! minikube status >/dev/null 2>&1; then
    echo "[+] Starting Minikube cluster..."
    minikube start
else
    echo "[+] Minikube is already running."
fi

# 2. Deploy ConfigMap (Custom Zepto Storefront HTML)
echo "[*] Step 2: Applying ConfigMap..."
kubectl apply -f configmap.yaml

# 3. Deploy Pod
echo "[*] Step 3: Deploying Pod 'hello-k8s'..."
kubectl apply -f pod.yaml

# 4. Deploy Service
echo "[*] Step 4: Exposing Pod via NodePort Service..."
kubectl apply -f service.yaml

# 5. Wait for Pod to become Ready
echo "[*] Step 5: Waiting for Pod to enter Running state..."
kubectl wait --for=condition=Ready pod/hello-k8s --timeout=60s

echo ""
echo "=========================================================="
echo "✅ Pod and Service Deployed Successfully!"
echo "=========================================================="
kubectl get pods -l app=zepto-storefront -o wide
kubectl get service hello-k8s

echo ""
echo "Access the app in your browser using:"
echo "  minikube service hello-k8s"
