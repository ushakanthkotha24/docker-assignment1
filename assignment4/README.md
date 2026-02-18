# Kubernetes Deployment Guide - Assignment 4

Deploy a three-tier application to a **3-node Kubernetes cluster** with high availability and pod distribution!

This folder contains everything you need to deploy:
- **Database**: PostgreSQL for data storage (1 replica on control plane)
- **Backend**: Flask API for business logic (2 replicas distributed across workers)
- **Frontend**: Nginx web server for the user interface (2 replicas distributed across workers)

Pre-configured for the **ushakanth** namespace.

## What's Inside

```
assignment4/
├── README.md                   # This guide
│
├── postgres/                   # Database tier
│   ├── configmap.yaml         # Database credentials
│   ├── pvc.yaml               # Storage volume
│   ├── deployment.yaml        # PostgreSQL deployment with node affinity
│   ├── init-sql-configmap.yaml # Database setup scripts
│   └── service.yaml           # How other services reach it
│
├── backend/                    # API tier
│   ├── configmap.yaml         # Settings for Flask app
│   ├── deployment.yaml        # Flask API with pod affinity (spread across workers)
│   ├── service.yaml           # How frontend reaches it
│   └── pdb.yaml               # Pod Disruption Budget for high availability
│
└── frontend/                   # Web tier
    ├── configmap.yaml         # Settings for Nginx
    ├── deployment.yaml        # Nginx with pod affinity (spread across workers)
    ├── service.yaml           # How to reach it from outside
    └── pdb.yaml               # Pod Disruption Budget for high availability
```

---

## Cluster Architecture

**Your 3-Node Cluster:**
```
┌─────────────────────────────────────────┐
│         kmaster (control-plane)         │
│  ┌──────────────────────────────────┐   │
│  │  PostgreSQL Pod                  │   │
│  │  (Single instance, node-pinned)  │   │
│  └──────────────────────────────────┘   │
└─────────────────────────────────────────┘
           ↓          ↓
    ┌────────────┬─────────────┐
    │            │             │
    │            │             │
┌───────────┐ ┌──────────┐ ┌──────────┐
│ kworker1  │ │ kworker2 │ │ kworker1 │
│           │ │          │ │          │
│ Backend-1 │ │ Frontend │ │ Backend-2│
│ Frontend-1│ │ (or vice │ │ Frontend │
│           │ │  versa)  │ │  (spread)│
└───────────┘ └──────────┘ └──────────┘
```

**Key Differences from Assignment 3 (Minikube):**

1. **Pod Anti-Affinity** - Backends and Frontends spread across worker nodes for resilience
2. **Node Affinity** - PostgreSQL pinned to control plane to preserve data
3. **Pod Disruption Budgets** - Ensure minimum replicas during cluster maintenance
4. **Resource Limits** - Increased memory/CPU for multi-node environment
5. **Service Type** - LoadBalancer for external access (if supported) or NodePort
6. **Namespace** - Production-ready configuration with explicit namespace

---

## Quick Deployment

### Prerequisites

- **kubectl** - Connected to your 3-node cluster
- **Namespace "ushakanth"** - Already created ✓
- **Docker registry secret "dockerhub-secret"** - Already created ✓
- **Docker images** - Pushed to Docker Hub (ushakanth24/backend:latest, ushakanth24/frontend:latest)

### Step 1: Deploy PostgreSQL Database

```bash
# Apply all PostgreSQL configurations (order matters)
kubectl apply -f postgres/configmap.yaml
kubectl apply -f postgres/init-sql-configmap.yaml
kubectl apply -f postgres/pvc.yaml
kubectl apply -f postgres/deployment.yaml
kubectl apply -f postgres/service.yaml

# Wait for postgres to be ready (1/1 replicas)
kubectl rollout status deployment/postgres -n ushakanth
```

### Step 2: Deploy Backend API

```bash
# Apply backend configurations
kubectl apply -f backend/configmap.yaml
kubectl apply -f backend/deployment.yaml
kubectl apply -f backend/service.yaml
kubectl apply -f backend/pdb.yaml

# Wait for backend to be ready (2/2 replicas)
kubectl rollout status deployment/backend -n ushakanth
```

### Step 3: Deploy Frontend Web Server

```bash
# Apply frontend configurations
kubectl apply -f frontend/configmap.yaml
kubectl apply -f frontend/deployment.yaml
kubectl apply -f frontend/service.yaml
kubectl apply -f frontend/pdb.yaml

# Wait for frontend to be ready (2/2 replicas)
kubectl rollout status deployment/frontend -n ushakanth
```

### One-Command Deployment (After namespace setup)

```bash
# Deploy everything at once
kubectl apply -f postgres/ -f backend/ -f frontend/ -n ushakanth

# Monitor the deployment
kubectl get pods -n ushakanth -w
```

---

## Verify Deployment

### Check all pods are running

```bash
kubectl get pods -n ushakanth -o wide
```

**Expected output:**
```
NAME                        READY   STATUS    RESTARTS   AGE     IP           NODE       
postgres-xxxxxxxxxx-xxxxx   1/1     Running   0          2m      10.244.0.x   kmaster    
backend-xxxxxxxxxx-xxxxx    1/1     Running   0          1m      10.244.1.x   kworker1   
backend-xxxxxxxxxx-xxxxy    1/1     Running   0          1m      10.244.2.x   kworker2   
frontend-xxxxxxxxxx-xxxxx   1/1     Running   0          30s     10.244.1.x   kworker1   
frontend-xxxxxxxxxx-xxxxy   1/1     Running   0          30s     10.244.2.x   kworker2
```

### Check services

```bash
kubectl get svc -n ushakanth
```

### Access the application

**Get the Frontend NodePort:**
```bash
kubectl get svc frontend -n ushakanth
```

Then access via: `http://<any-node-ip>:<NODE_PORT>`

### Check PostgreSQL data

```bash
kubectl exec -it postgres-xxxxxxxxxx-xxxxx -n ushakanth -- psql -U admin -d python_app_db -c "SELECT * FROM users;"
```

### View logs

```bash
# Backend logs
kubectl logs deployment/backend -n ushakanth -f

# Frontend logs
kubectl logs deployment/frontend -n ushakanth -f

# PostgreSQL logs
kubectl logs deployment/postgres -n ushakanth -f
```

---

## High Availability Features

### 1. Pod Anti-Affinity (Backend & Frontend)
Ensures that multiple replicas of the same service don't run on the same node:
```yaml
affinity:
  podAntiAffinity:
    preferredDuringSchedulingIgnoredDuringExecution:
    - weight: 100
      podAffinityTerm:
        labelSelector:
          matchExpressions:
          - key: app
            operator: In
            values:
            - backend  # or frontend
        topologyKey: kubernetes.io/hostname
```

### 2. Node Affinity (PostgreSQL)
Pins PostgreSQL to the control plane for data consistency:
```yaml
affinity:
  nodeAffinity:
    preferredDuringSchedulingIgnoredDuringExecution:
    - weight: 100
      preference:
        matchExpressions:
        - key: node-role.kubernetes.io/control-plane
          operator: Exists
```

### 3. Pod Disruption Budgets
Ensures minimum replicas during maintenance:
```yaml
spec:
  minAvailable: 1  # Always keep at least 1 pod running
  selector:
    matchLabels:
      app: backend
```

---

## Troubleshooting

### Pods stuck in Pending

```bash
# Check why pods can't be scheduled
kubectl describe pod <pod-name> -n ushakanth

# Common issues:
# - Node affinity can't be satisfied
# - Insufficient resources on worker nodes
# - Storage provisioning issues (PVC)
```

### Database connection failures

```bash
# Verify PostgreSQL service
kubectl get svc postgres -n ushakanth
kubectl exec -it <backend-pod> -n ushakanth -- ping postgres

# Check PostgreSQL logs
kubectl logs deployment/postgres -n ushakanth
```

### Frontend can't reach backend

```bash
# Verify backend service
kubectl get svc backend -n ushakanth

# Test from frontend pod
kubectl exec -it <frontend-pod> -n ushakanth -- curl backend:5000/health
```

### Image pull errors

```bash
# Verify Docker registry secret exists
kubectl get secrets -n ushakanth

# Check the secret is correctly configured
kubectl describe secret dockerhub-secret -n ushakanth
```

---

## Key Differences from Assignment 3

| Feature | Assignment 3 (Minikube) | Assignment 4 (3-Node Cluster) |
|---------|------------------------|------------------------------|
| Database Replicas | 1 (single node) | 1 (node-pinned to control plane) |
| Backend Replicas | 2 (same node) | 2 (spread across workers) |
| Frontend Replicas | 2 (same node) | 2 (spread across workers) |
| Pod Anti-Affinity | None | Preferred (spread replicas) |
| Node Affinity | None | Required for PostgreSQL |
| Pod Disruption Budget | None | Enabled (min 1 available) |
| Storage Class | minikube-hostpath | cluster-default (multi-node safe) |
| Service Type | ClusterIP/NodePort | NodePort or LoadBalancer |

---

## Scaling Recommendations

### Scale Backend to 3 replicas

```bash
kubectl scale deployment backend --replicas=3 -n ushakanth
```

**Note:** With 3-node cluster, if all 3 workers have 3 backend pods, they'll be evenly distributed: 1 per node.

### Scale Frontend to 3 replicas

```bash
kubectl scale deployment frontend --replicas=3 -n ushakanth
```

### Monitor pod distribution

```bash
kubectl get pods -n ushakanth -o wide | grep -E "backend|frontend"
```

---

## Cleanup

```bash
# Delete all resources in the namespace
kubectl delete namespace ushakanth

# Or selectively delete components
kubectl delete deployment,svc,pvc,configmap,secret -n ushakanth --all
```

---

## Next Steps

1. Monitor cluster metrics with `kubectl top nodes` and `kubectl top pods -n ushakanth`
2. Set up persistent storage properly (EBS, NFS, etc.)
3. Configure Ingress for external access instead of NodePort
4. Implement health checks and autoscaling
5. Set up logging and monitoring (ELK, Prometheus, etc.)
