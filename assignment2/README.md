# Kubernetes Deployment Guide - Assignment 2

This folder contains the Kubernetes manifests to deploy the three-tier application (PostgreSQL, Flask backend, and Nginx frontend) to Minikube.

## What's Inside

```
assignment2/
├── namespace.yaml              # Sets up app-deployment namespace
├── README.md                   # This file
├── postgres/
│   ├── configmap.yaml         # DB credentials and config
│   ├── pvc.yaml               # Storage for postgres data
│   ├── deployment.yaml        # Postgres container setup
│   ├── init-sql-configmap.yaml # SQL initialization scripts
│   └── service.yaml           # Internal service for postgres
├── backend/
│   ├── deployment.yaml        # Flask API with 2 replicas
│   └── service.yaml           # Internal service for backend
└── frontend/
    ├── deployment.yaml        # Nginx web server with 2 replicas
    └── service.yaml           # NodePort service (port 30080)
```

---

## Quick Start (TL;DR)

### Prerequisites

- Minikube ([get it here](https://minikube.sigs.k8s.io/docs/start/))
- kubectl CLI
- Docker (for building images)

### Deploy in 6 Steps

```powershell
# 1. Start minikube
minikube start

# 2. Use Minikube's docker
@minikube docker-env | Invoke-Expression

# 3. Build images (from assignment1 folder)
cd ../assignment1
docker build -t backend:latest ./backend
docker build -t frontend:latest ./frontend

# 4. Deploy everything
cd ../assignment2
kubectl apply -f .

# 5. Wait for startup
kubectl get pods -n app-deployment -w

# 6. Open the app
minikube service frontend -n app-deployment
```

That's it. Your app is running.

---

## The Full Walkthrough

### Step 1: Fire up Minikube

```powershell
minikube start
```

This spins up a single-node Kubernetes cluster. Takes a minute or so the first time.

### Step 2: Tell Docker to Use Minikube's Docker

This is important - we want to build images inside Minikube, not on your host:

```powershell
@minikube docker-env | Invoke-Expression
```

You'll need to run this in every new PowerShell terminal. If you want it automatic, add it to your PowerShell profile.

### Step 3: Build Your Container Images

Go into the assignment1 folder and build:

```powershell
cd ../assignment1

# Build the Flask backend
docker build -t backend:latest ./backend

# Build the Nginx frontend
docker build -t frontend:latest ./frontend
```

Check they're there:
```powershell
docker images
# Should show backend:latest and frontend:latest
```

### Step 4: Create the Namespace

Think of a namespace like a folder - it keeps all your stuff organized and separate from other projects:

```powershell
cd ../assignment2
kubectl apply -f namespace.yaml
```

### Step 5: Deploy the Database

PostgreSQL needs a place to store data that survives pod restarts:

```powershell
kubectl apply -f postgres/
```

Wait for it to actually start:
```powershell
kubectl rollout status deployment/postgres -n app-deployment
```

This will watch and wait until Postgres is up. Takes maybe 30 seconds.

**What just happened:**
- The ConfigMap set up the database credentials
- The PVC created a storage volume
- The Deployment started the postgres container
- The Service made postgres accessible to other pods

### Step 6: Deploy the Backend

Now the Flask API:

```powershell
kubectl apply -f backend/
```

Wait for rollout:
```powershell
kubectl rollout status deployment/backend -n app-deployment
```

### Step 7: Deploy the Frontend

Finally, the web server:

```powershell
kubectl apply -f frontend/
```

Wait for it:
```powershell
kubectl rollout status deployment/frontend -n app-deployment
```

### Step 8: See What You've Built

```powershell
kubectl get pods -n app-deployment
```

You should see 5 pods running:
- 1 postgres
- 2 backend (replicas)
- 2 frontend (replicas)

---

## How to Use It

### Get the App URL

```powershell
minikube service frontend -n app-deployment
```

This opens your browser to the app. Magic.

Or manually forward ports:

```powershell
# Terminal 1: Frontend
kubectl port-forward -n app-deployment svc/frontend 3000:80

# Terminal 2: Backend
kubectl port-forward -n app-deployment svc/backend 5000:5000
```

Then visit http://localhost:3000

### Accessing Individual Services

**Frontend (Nginx)**
```powershell
minikube service frontend -n app-deployment
# Or manually forward:
kubectl port-forward -n app-deployment svc/frontend 3000:80
# Then visit: http://localhost:3000
```

**Backend API**
```powershell
kubectl port-forward -n app-deployment svc/backend 5000:5000
# Test health endpoint:
Invoke-WebRequest http://localhost:5000/api/health
```

**Database**
```powershell
kubectl port-forward -n app-deployment svc/postgres 5432:5432
# Connect with psql or your DB client
psql -h localhost -U admin -d python_app_db
```

### Check What's Happening

```powershell
# See all the pods
kubectl get pods -n app-deployment

# See what's exposed
kubectl get svc -n app-deployment

# See the deployments
kubectl get deployments -n app-deployment
```

### Look at Logs

```powershell
# Watch backend logs in real-time
kubectl logs -n app-deployment -l app=backend -f

# See logs from a specific pod
kubectl logs -n app-deployment <pod-name>

# Get the last 100 lines
kubectl logs -n app-deployment -l app=backend --tail=100
```

### Get Into a Pod

Sometimes you need to poke around inside:

```powershell
# Connect to a backend pod
kubectl exec -it -n app-deployment <pod-name> -- /bin/sh

# Or run a command without staying in
kubectl exec -n app-deployment <pod-name> -- ps aux
```

### Scale Things Up or Down

```powershell
# Run 5 backend pods instead of 2
kubectl scale deployment backend --replicas=5 -n app-deployment

# Scale back down
kubectl scale deployment backend --replicas=1 -n app-deployment

# Check the status
kubectl get pods -n app-deployment
```

### See Everything that Happened

```powershell
# Events in order
kubectl get events -n app-deployment --sort-by='.lastTimestamp'

# More details about a pod
kubectl describe pod -n app-deployment <pod-name>
```

### Deploy Changes

```powershell
# Deploy only postgres changes
kubectl apply -f postgres/

# Deploy everything and watch
kubectl apply -f . && kubectl get pods -n app-deployment -w
```

### Deploy Everything in One Shot

```powershell
kubectl apply -f .
```

This applies all the YAML files in this folder.

---

## How It All Works

**PostgreSQL**: Runs in a single pod, keeps data in a persistent volume so it doesn't disappear when the pod restarts.

**Backend**: Two pods running Flask, each connected to the same database. The Kubernetes service load-balances requests between them.

**Frontend**: Two Nginx pods serving static files. They talk to the backend service for API calls.

All three layers talk to each other using Kubernetes service names (postgres, backend, frontend) instead of IP addresses. The frontend is exposed outside the cluster on port 30080, while backend and postgres are internal-only.

---

## Quick Reference: Common Tasks

| What | Command |
|------|---------|
| See all pods | `kubectl get pods -n app-deployment` |
| See pod logs | `kubectl logs -n app-deployment <pod-name>` |
| Connect to pod | `kubectl exec -it -n app-deployment <pod-name> -- /bin/sh` |
| Port-forward | `kubectl port-forward -n app-deployment svc/frontend 3000:80` |
| Get pod details | `kubectl describe pod -n app-deployment <pod-name>` |
| Scale deployment | `kubectl scale deployment backend --replicas=3 -n app-deployment` |
| Check all resources | `kubectl get all -n app-deployment` |
| Restart deployment | `kubectl rollout restart deployment/backend -n app-deployment` |
| See recent events | `kubectl get events -n app-deployment --sort-by='.lastTimestamp'` |

---

## Troubleshooting

### Pods are stuck in "Pending" or "CrashLoopBackOff"

```powershell
kubectl describe pod -n app-deployment <pod-name>
```

The Events section at the bottom usually tells you what's wrong.

### Images aren't found

Did you forget to build them in Minikube's Docker?

```powershell
@minikube docker-env | Invoke-Expression
docker build -t backend:latest ../assignment1/backend
docker build -t frontend:latest ../assignment1/frontend
```

### Can't connect to the app

```powershell
# Are the pods actually running?
kubectl get pods -n app-deployment

# Is the service there?
kubectl get svc -n app-deployment

# Try to reach it directly
kubectl exec -n app-deployment -it <frontend-pod-name> -- curl http://localhost
```

### Backend can't talk to the database

Backend logs will show connection errors:

```powershell
kubectl logs -n app-deployment -l app=backend
```

The postgres pod might still be starting. Give it a minute and try again.

### Port already in use when port-forwarding

Something else is using that port:

```powershell
netstat -ano | findstr :3000

# Kill it if needed
taskkill /PID <PID> /F
```

---

## Clean Up

### Just restart everything
```powershell
kubectl delete -f .
kubectl apply -f .
```

### Keep the namespace but reload everything
```powershell
kubectl delete -f . && kubectl apply -f .
```

### Remove the whole namespace
```powershell
kubectl delete namespace app-deployment
```

### Stop Minikube (keeps your VM)
```powershell
minikube stop
```

### Delete everything (can't undo)
```powershell
minikube delete
```

---

## Key Concepts

**Deployment**: Describes how many pods you want and how to create them. If a pod dies, the Deployment makes a new one.

**Pod**: A container (or group of containers). In our case, one container per pod.

**Service**: How pods talk to each other and how the outside world reaches them. Uses DNS names instead of IP addresses.

**ConfigMap**: A place to store configuration that isn't secrets.

**PersistentVolumeClaim**: A request for storage. The data survives even if the pod is deleted.

**Namespace**: A way to organize and isolate resources. Like a folder.

---

## Configuration Notes

- Database password is `password123` (change in `postgres/configmap.yaml` for production)
- Database name is `python_app_db`
- Backend uses `imagePullPolicy: Never` so it uses your local Docker images
- Each pod has resource limits to not hog the Minikube VM
- Health checks are configured so bad pods get restarted automatically

---

## Environment Variables

The backend uses these variables (in `backend/deployment.yaml`):
- `DATABASE_URL` - Connection string to postgres
- `FLASK_ENV` - Set to `development`
- `FLASK_APP` - Points to `app.py`

The database (in `postgres/configmap.yaml`):
- `POSTGRES_DB` - `python_app_db`
- `POSTGRES_USER` - `admin`
- `POSTGRES_PASSWORD` - `password123` (change this in production!)

---

## Important Notes

- We use `imagePullPolicy: Never` so Kubernetes doesn't try to download the images
- Each pod requests CPU and memory - this keeps things from crashing due to resource hunger
- Health checks restart pods that aren't responding
- The frontend is on NodePort (accessible from outside the cluster)
- Backend and postgres are ClusterIP (only accessible from inside Kubernetes)
- Everything runs in the `app-deployment` namespace so you can have other projects running without conflict

---

## Pro Tips

- Use `kubectl get events -n app-deployment --sort-by='.lastTimestamp'` to see a timeline of what happened
- Port-forward is handy for debugging: `kubectl port-forward -n app-deployment pod/<name> 5000:5000`
- Check resource usage: `kubectl top pods -n app-deployment` (requires metrics server)
- Use `kubectx` and `kubens` tools to switch between clusters and namespaces faster
- Add this to your PowerShell profile to auto-set docker env: `@minikube docker-env | Invoke-Expression`

---

Good luck! Let me know if you hit any snags.
