# Kubernetes Deployment Guide - Assignment 3

Deploy a three-tier application to your Kubernetes cluster!

This folder contains everything you need to deploy:
- **Database**: PostgreSQL for data storage
- **Backend**: Flask API for business logic  
- **Frontend**: Nginx web server for the user interface

Pre-configured for the **ushakanth** namespace.

## What's Inside

```
assignment3/
├── README.md                   # This guide
│
├── postgres/                   # Database tier
│   ├── configmap.yaml         # Database credentials
│   ├── pvc.yaml               # Storage volume
│   ├── deployment.yaml        # How to run PostgreSQL
│   ├── init-sql-configmap.yaml # Database setup scripts
│   └── service.yaml           # How other services reach it
│
├── backend/                    # API tier  
│   ├── configmap.yaml         # Settings for Flask app
│   ├── deployment.yaml        # How to run the Flask API
│   └── service.yaml           # How frontend reaches it
│
└── frontend/                   # Web tier
    ├── configmap.yaml         # Settings for Nginx
    ├── deployment.yaml        # How to run Nginx
    └── service.yaml           # How to reach it from outside
```

---

## Deployment Instructions

### Prerequisites

- **kubectl** - Connected to your Kubernetes cluster
- **Namespace "ushakanth"** - Already created
- **Docker images** - Pushed to a registry

### Step 1: Build and Push Docker Images

```bash
cd ../assignment1

# Build the images
docker build -t backend:latest ./backend
docker build -t frontend:latest ./frontend

# Tag for your registry (example using Docker Hub)
docker tag backend:latest ushakanth24/backend:latest
docker tag frontend:latest ushakanth24/frontend:latest

# Push to registry
docker push ushakanth24/backend:latest
docker push ushakanth24/frontend:latest
```

**Registry examples:**
- Docker Hub: `ushakanth24/backend:latest`


### Step 2: Update Image References in Deployments

Edit both deployment files to use your pushed images:

```bash
# Open backend/deployment.yaml
# Find: image: backend:latest
# Replace with: image: your-username/backend:latest

# Open frontend/deployment.yaml
# Find: image: frontend:latest
# Replace with: image: your-username/frontend:latest
```

If using private registry, add this to both deployments under `image`:
```yaml
imagePullPolicy: IfNotPresent
```

### Step 3: Verify Cluster Connection

```bash
# Check current context
kubectl config current-context

# List nodes
kubectl get nodes

# Verify namespace exists
kubectl get namespaces | grep ushakanth
```

### Step 4: Deploy to Kubernetes

**Important:** kubectl cannot read README.md files, so use one of these methods:

**Option A: Deploy each layer separately (Recommended)**
```bash
cd ../assignment3

kubectl apply -f postgres/ -n ushakanth
kubectl apply -f backend/ -n ushakanth
kubectl apply -f frontend/ -n ushakanth
```

**Option B: Deploy all YAML files at once**
```bash
cd ../assignment3

kubectl apply -f backend/ -f frontend/ -f postgres/ -n ushakanth
```

**Option C: Deploy using find command**
```bash
cd ../assignment3

kubectl apply -f $(find . -name "*.yaml") -n ushakanth
```

### Step 5: Monitor Deployment

```bash
# Watch pods starting up
kubectl get pods -n ushakanth -w

# Once all pods are running, check services
kubectl get svc -n ushakanth

# View all resources
kubectl get all -n ushakanth
```

### Step 6: Access Your Application

**Option A: NodePort (External IP)**
```bash
kubectl get svc frontend -n ushakanth

# Get the EXTERNAL-IP and PORT
# Visit: http://EXTERNAL-IP:PORT
```

**Option B: Port Forwarding**
```bash
kubectl port-forward -n ushakanth svc/frontend 8080:80
# Visit: http://localhost:8080
```

**Option C: LoadBalancer (if available)**

Change frontend service type to LoadBalancer:
```yaml
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 80
```

Then deploy and check:
```bash
kubectl get svc frontend -n ushakanth
# Wait for EXTERNAL-IP to be assigned
```

---

## Configuration Management

All settings are in ConfigMaps and can be updated without rebuilding:

### Backend Configuration (backend/configmap.yaml)

```yaml
FLASK_ENV: development
DATABASE_HOST: postgres
DATABASE_USER: admin
DATABASE_PASSWORD: password123
SECRET_KEY: dev-secret-key
```

### Frontend Configuration (frontend/configmap.yaml)

```yaml
BACKEND_API_URL: http://backend:5000
APP_NAME: Python Docker App
APP_VERSION: "1.0.0"
```

### Database Configuration (postgres/configmap.yaml)

```yaml
POSTGRES_DB: python_app_db
POSTGRES_USER: admin
POSTGRES_PASSWORD: password123
```

### Update Configuration

1. Edit the ConfigMap file
2. Apply the change:
   ```bash
   kubectl apply -f backend/configmap.yaml -n ushakanth
   ```
3. Restart the deployment:
   ```bash
   kubectl rollout restart deployment/backend -n ushakanth
   ```

---

## Useful Commands

```bash
# See all pods
kubectl get pods -n ushakanth

# View pod logs
kubectl logs -n ushakanth -l app=backend

# Connect to a pod
kubectl exec -it -n ushakanth <pod-name> -- /bin/sh

# Check pod details
kubectl describe pod -n ushakanth <pod-name>

# Scale a deployment
kubectl scale deployment backend --replicas=3 -n ushakanth

# Restart a deployment
kubectl rollout restart deployment/backend -n ushakanth

# Port forward to a service
kubectl port-forward -n ushakanth svc/backend 5000:5000

# View recent events
kubectl get events -n ushakanth --sort-by='.lastTimestamp'

# Check resource usage
kubectl top pods -n ushakanth
```

---

## Troubleshooting

### Pods are in "Pending" or "CrashLoopBackOff"

```bash
kubectl describe pod -n ushakanth <pod-name>
# Check the Events section at the bottom
```

### Images not found

Verify images are pushed to your registry and the image path is correct in deployments.

### Backend can't connect to database

```bash
kubectl logs -n ushakanth -l app=backend
# Wait a minute - postgres may still be starting
```

### Port already in use

```bash
# Find process using port
lsof -i :8080

# Kill it if needed
kill -9 <PID>
```

---

## Switching to a Different Namespace

If you want to use a different namespace:

```bash
# Create new namespace
kubectl create namespace my-namespace

# Update all files
find . -name "*.yaml" -exec sed -i 's/namespace: ushakanth/namespace: my-namespace/g' {} \;

# Deploy
kubectl apply -f . -n my-namespace
```

---

## Clean Up

```bash
# Delete all resources in namespace
kubectl delete -f . -n ushakanth

# Delete entire namespace
kubectl delete namespace ushakanth
```

---

**Namespace:** ushakanth  
**Status:** Ready for production deployment
