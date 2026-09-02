# Exercise 1: Kubernetes Getting Started - Automated Deployment Script (PowerShell)

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "🚀 Exercise 1: Deploying Zepto Storefront Pod on Minikube" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Check Minikube
Write-Host "[*] Step 1: Checking Minikube status..." -ForegroundColor Yellow
$minikubeStatus = minikube status 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[+] Starting Minikube cluster..." -ForegroundColor Yellow
    minikube start
} else {
    Write-Host "[+] Minikube is already running." -ForegroundColor Green
}

# 2. Deploy Manifests
Write-Host "[*] Step 2: Applying ConfigMap, Pod, and Service manifests..." -ForegroundColor Yellow
kubectl apply -f configmap.yaml
kubectl apply -f pod.yaml
kubectl apply -f service.yaml

# 3. Wait for readiness
Write-Host "[*] Step 3: Waiting for Pod 'hello-k8s' to become Ready..." -ForegroundColor Yellow
kubectl wait --for=condition=Ready pod/hello-k8s --timeout=60s

Write-Host "`n✅ Pod and Service Deployed Successfully!" -ForegroundColor Green
kubectl get pods -l app=zepto-storefront -o wide
kubectl get service hello-k8s

Write-Host "`nTo open the storefront in your default browser, run:" -ForegroundColor Cyan
Write-Host "  minikube service hello-k8s" -ForegroundColor White
