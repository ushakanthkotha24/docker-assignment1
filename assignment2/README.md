# Kubernetes Deployment Guide - Assignment 2

Get your full-stack application running on Kubernetes with Minikube!

This folder contains everything you need to deploy a three-tier application:
- **Database**: PostgreSQL for data storage
- **Backend**: Flask API for business logic  
- **Frontend**: Nginx web server for the user interface

All running nicely in containers, managed by Kubernetes.

## What's Inside

```
assignment2/
├── namespace.yaml              # Where everything lives (namespace)
├── setup-custom-namespace.sh   # Smart helper script (use this!)
├── README.md                   # This guide
│
├── postgres/                   # Database tier
│   ├── configmap.yaml         # Database credentials
│   ├── pvc.yaml               # Storage volume (so data doesn't disappear)
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

## Quick Start (5 Minutes)

### You'll Need

- **Minikube** - A mini Kubernetes cluster on your computer ([install it](https://minikube.sigs.k8s.io/docs/start/))
- **kubectl** - The command-line tool to talk to Kubernetes
- **Docker** - For building the container images

### Deploy in 6 Steps

```bash
# 1. Fire up Minikube
minikube start

# 2. Point Docker to Minikube (important!)
eval $(minikube docker-env)

# 3. Build your app images
cd ../assignment1
docker build -t backend:latest ./backend
docker build -t frontend:latest ./frontend

# 4. Deploy everything
cd ../assignment2
kubectl apply -f .

# 5. Wait for it to start
kubectl get pods -n app-deployment -w

# 6. Open it in your browser
minikube service frontend -n app-deployment
```

Done! Your app is live.

---

## Using Your Own Namespace

By default, everything lives in the `app-deployment` namespace. Want to use your own? Super easy!

### Option 1: Automated Setup (Easiest - Do This!)

Use our smart helper script - it does everything for you:

```bash
# Make it executable
chmod +x setup-custom-namespace.sh

# Run it
./setup-custom-namespace.sh

# It will ask you for your namespace name
# Then it automatically updates everything and deploys!
```

The script handles:
- Creating your namespace
- Updating all config files
- Deploying the app
- Showing you how to access it

### Option 2: Manual Setup (More Control)

Want to do it yourself? Here's how:

1. **Edit your namespace name:**
   ```bash
   nano namespace.yaml
   # Change: name: app-deployment to name: my-namespace
   ```

2. **Update all config files:**
   ```bash
   # Replace in all YAML files (one command!)
   find . -name "*.yaml" -exec sed -i 's/namespace: app-deployment/namespace: my-namespace/g' {} \;
   ```

3. **Deploy:**
   ```bash
   kubectl apply -f namespace.yaml
   kubectl apply -f .
   ```

### Option 3: Skip namespace.yaml Entirely

```bash
# Create your custom namespace
kubectl create namespace my-custom-namespace

# Then deploy everything else (update all YAML files with your namespace name first)
kubectl apply -f backend/ -n my-custom-namespace
kubectl apply -f frontend/ -n my-custom-namespace
kubectl apply -f postgres/ -n my-custom-namespace
```

### Verify Your Namespace

```bash
# List all namespaces
kubectl get namespaces

# Check resources in your namespace
kubectl get all -n my-custom-namespace
```

---

## The Full Walkthrough

### Step 1: Fire up Minikube

```bash
minikube start
```

This spins up a lightweight Kubernetes cluster on your machine. Takes a minute the first time.

### Step 2: Point Docker to Minikube

We want to build images inside Minikube, not on your computer:

```bash
eval $(minikube docker-env)
```

Run this in every new terminal. To make it automatic, add it to your `~/.bashrc` or `~/.zshrc`.

### Step 3: Build Your App Images

Navigate to assignment1 and build the Docker images:

```bash
cd ../assignment1

# Build the Flask backend API
docker build -t backend:latest ./backend

# Build the Nginx frontend
docker build -t frontend:latest ./frontend
```

Verify they built:
```bash
docker images | grep -E "backend|frontend"
# Should show both backend:latest and frontend:latest
```

### Step 4: Set Up Your Namespace

A namespace is like a folder in Kubernetes - keeps everything organized:

```bash
cd ../assignment2
kubectl apply -f namespace.yaml
```

### Step 5: Deploy the Database

PostgreSQL stores all the data:

```bash
kubectl apply -f postgres/
```

Wait for it to be ready:
```bash
kubectl rollout status deployment/postgres -n app-deployment
```

You'll see something like: "deployment 'postgres' successfully rolled out" when ready.

### Step 6: Deploy the Backend

The Flask API - the brains of the app:

```bash
kubectl apply -f backend/
kubectl rollout status deployment/backend -n app-deployment
```

### Step 7: Deploy the Frontend

The Nginx web server - what users see:

```bash
kubectl apply -f frontend/
kubectl rollout status deployment/frontend -n app-deployment
```

### Step 8: See What You Built

```bash
kubectl get pods -n app-deployment
```

You should see 5 pods running:
- 1 x PostgreSQL database
- 2 x Flask backend (for redundancy)
- 2 x Nginx frontend (for redundancy)

---

## Configuration Management with ConfigMaps

All your app settings live in ConfigMaps - separate from your code. Want to change a setting? No need to rebuild. Just update the ConfigMap and restart.

### Backend Configuration

Your Flask app settings (found in `backend/configmap.yaml`):

The `backend/configmap.yaml` contains all Flask application settings:

```yaml
FLASK_ENV: development           # Flask environment
FLASK_APP: app.py               # Flask app entry point
DATABASE_USER: admin            # Database user
DATABASE_PASSWORD: password123  # Database password
DATABASE_HOST: postgres         # Database service name
DATABASE_PORT: "5432"           # Database port
DATABASE_NAME: python_app_db    # Database name
SECRET_KEY: dev-secret-key      # Flask secret key
CORS_ORIGINS: http://localhost:3000,http://frontend:80
```

These are automatically injected into backend pods via `envFrom` in the deployment.

### Frontend Configuration

Your Nginx settings (`frontend/configmap.yaml`):

```yaml
BACKEND_API_URL: http://backend:5000  # Where frontend finds the API
APP_NAME: Python Docker App           # Your app's name
APP_VERSION: "1.0.0"                  # Version number
NGINX_WORKER_PROCESSES: "auto"        # Let Nginx figure it out
NGINX_WORKER_CONNECTIONS: "1024"      # Max simultaneous connections
```

### Database Configuration

PostgreSQL settings (`postgres/configmap.yaml`):

```yaml
POSTGRES_DB: python_app_db      # Database name
POSTGRES_USER: admin            # Admin username
POSTGRES_PASSWORD: password123  # Admin password (change for production!)
```

### Updating Configuration

Want to change something?

1. Edit the ConfigMap file:
   ```bash
   nano backend/configmap.yaml
   # Make your changes...
   ```

2. Deploy the changes:
   ```bash
   kubectl apply -f backend/configmap.yaml
   ```

3. Restart the deployment so it picks up new values:
   ```bash
   kubectl rollout restart deployment/backend -n app-deployment
   ```

WARNING: Changing a ConfigMap doesn't automatically restart pods. You have to restart them manually.

---

## Get the App URL

```bash
minikube service frontend -n app-deployment
```

This opens your browser to the app. Magic.

Or manually forward ports:

```bash
# Terminal 1: Frontend
kubectl port-forward -n app-deployment svc/frontend 3000:80

# Terminal 2: Backend
kubectl port-forward -n app-deployment svc/backend 5000:5000
```

Then visit http://localhost:3000

### Accessing Individual Services

**Frontend** - Your web app:
```bash
# Option 1: Let Minikube open it
minikube service frontend -n app-deployment

# Option 2: Forward manually
kubectl port-forward -n app-deployment svc/frontend 3000:80
# Then visit http://localhost:3000
```

**Backend API** - The logic:
```bash
kubectl port-forward -n app-deployment svc/backend 5000:5000
# Test it: curl http://localhost:5000/api/health
```

**Database** - The storage:
```bash
kubectl port-forward -n app-deployment svc/postgres 5432:5432
# Connect: psql -h localhost -U admin -d python_app_db
```

### Check What's Happening

```bash
# See all pods
kubectl get pods -n app-deployment

# See services
kubectl get svc -n app-deployment

# See deployments
kubectl get deployments -n app-deployment
```

### View Logs

```bash
# Watch backend logs in real-time
kubectl logs -n app-deployment -l app=backend -f

# Get logs from a specific pod
kubectl logs -n app-deployment <pod-name>

# Last 100 lines
kubectl logs -n app-deployment -l app=backend --tail=100
```

### Open a Shell Inside a Pod

```bash
# Connect to a backend pod
kubectl exec -it -n app-deployment <pod-name> -- /bin/sh

# Or run a command without staying in
kubectl exec -n app-deployment <pod-name> -- ps aux
```

### Scale Things Up or Down

```bash
# Run 5 backend pods instead of 2
kubectl scale deployment backend --replicas=5 -n app-deployment

# Scale back down
kubectl scale deployment backend --replicas=1 -n app-deployment

# Check the status
kubectl get pods -n app-deployment
```

### See Everything that Happened

```bash
# Events in order
kubectl get events -n app-deployment --sort-by='.lastTimestamp'

# More details about a pod
kubectl describe pod -n app-deployment <pod-name>
```

### Deploy Changes

```bash
# Deploy only postgres changes
kubectl apply -f postgres/

# Deploy everything and watch
kubectl apply -f . && kubectl get pods -n app-deployment -w
```

### Deploy Everything in One Shot

```bash
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
| See all namespaces | `kubectl get namespaces` |
| Create custom namespace | `kubectl create namespace my-namespace` |
| Delete namespace | `kubectl delete namespace my-namespace` |
| Switch default namespace | `kubectl config set-context --current --namespace=my-namespace` |
| See pod logs | `kubectl logs -n app-deployment <pod-name>` |
| Connect to pod | `kubectl exec -it -n app-deployment <pod-name> -- /bin/sh` |
| Port-forward | `kubectl port-forward -n app-deployment svc/frontend 3000:80` |
| Get pod details | `kubectl describe pod -n app-deployment <pod-name>` |
| Scale deployment | `kubectl scale deployment backend --replicas=3 -n app-deployment` |
| Check all resources | `kubectl get all -n app-deployment` |
| Restart deployment | `kubectl rollout restart deployment/backend -n app-deployment` |
| See recent events | `kubectl get events -n app-deployment --sort-by='.lastTimestamp'` |
| View ConfigMap | `kubectl describe configmap backend-config -n app-deployment` |
| Edit ConfigMap | `kubectl edit configmap backend-config -n app-deployment` |
| Apply ConfigMap changes | `kubectl apply -f backend/configmap.yaml && kubectl rollout restart deployment/backend -n app-deployment` |

---

## Troubleshooting

### Pods are stuck in "Pending" or "CrashLoopBackOff"

```bash
kubectl describe pod -n app-deployment <pod-name>
```

The Events section at the bottom usually tells you what's wrong.

### Images aren't found

Did you forget to build them in Minikube's Docker?

```bash
eval $(minikube docker-env)
docker build -t backend:latest ../assignment1/backend
docker build -t frontend:latest ../assignment1/frontend
```

### Can't connect to the app

```bash
# Are the pods actually running?
kubectl get pods -n app-deployment

# Is the service there?
kubectl get svc -n app-deployment

# Try to reach it directly
kubectl exec -n app-deployment -it <frontend-pod-name> -- curl http://localhost
```

### Backend can't talk to the database

Backend logs will show connection errors:

```bash
kubectl logs -n app-deployment -l app=backend
```

The postgres pod might still be starting. Give it a minute and try again.

### Port already in use when port-forwarding

Something else is using that port:

```bash
sudo lsof -i :3000

# Kill it if needed
sudo kill -9 <PID>
```

---

## Clean Up

### Just restart everything
```bash
kubectl delete -f .
kubectl apply -f .
```

### Keep the namespace but reload everything
```bash
kubectl delete -f . && kubectl apply -f .
```

### Remove the whole namespace
```bash
kubectl delete namespace app-deployment
```

### Stop Minikube (keeps your VM)
```bash
minikube stop
```

### Delete everything (can't undo)
```bash
minikube delete
```

---

## Key Concepts

**Deployment**: Describes how many pods you want and how to create them. If a pod dies, the Deployment makes a new one.

**Pod**: A container (or group of containers). In our case, one container per pod.

**Service**: How pods talk to each other and how the outside world reaches them. Uses DNS names instead of IP addresses.

**ConfigMap**: A place to store configuration that isn't secrets.

**PersistentVolumeClaim**: A request for storage. The data survives even if the pod is deleted.

**Namespace**: A way to organize and isolate resources. Like a folder. You can have multiple namespaces on the same cluster and deploy the same application in each with different names and configurations. This guide uses the `app-deployment` namespace, but you can customize it to use your own namespace name (see "Using Your Own Namespace" section).

---

## Configuration Notes

- **Namespace**: Default is `app-deployment`. Customize using `setup-custom-namespace.sh` or edit `namespace.yaml`
- **Database password** is `password123` (change in `postgres/configmap.yaml` for production)
- **Database name** is `python_app_db`
- Backend uses `imagePullPolicy: Never` so it uses your local Docker images
- Each pod has resource limits to not hog the Minikube VM
- Health checks are configured so bad pods get restarted automatically

---

## Environment Variables

All application configuration is now managed through ConfigMaps rather than hardcoded environment variables.

**Backend Configuration** (in `backend/configmap.yaml`):
- `FLASK_ENV` - Flask environment mode (development/production)
- `FLASK_APP` - Entry point for Flask app
- `DATABASE_USER` - Database user (admin)
- `DATABASE_PASSWORD` - Database password
- `DATABASE_HOST` - Database hostname (postgres)
- `DATABASE_PORT` - Database port (5432)
- `DATABASE_NAME` - Database name (python_app_db)
- `SECRET_KEY` - Flask application secret key
- `CORS_ORIGINS` - Allowed origins for CORS

**Frontend Configuration** (in `frontend/configmap.yaml`):
- `BACKEND_API_URL` - URL for backend API calls
- `APP_NAME` - Application display name
- `APP_VERSION` - Application version
- `NGINX_WORKER_PROCESSES` - Number of Nginx worker processes
- `NGINX_WORKER_CONNECTIONS` - Max connections per worker

**Database Configuration** (in `postgres/configmap.yaml`):
- `POSTGRES_DB` - Database name to create
- `POSTGRES_USER` - Admin user (admin)
- `POSTGRES_PASSWORD` - Admin password

See the ConfigMaps section above for how to modify these values.

---

## Important Notes

- Configuration is managed through ConfigMaps (`backend-config`, `frontend-config`, `postgres-config`)
- ConfigMap changes require manual deployment restart to take effect
- **Namespace Management**: Use `setup-custom-namespace.sh` to easily deploy with a custom namespace
- All kubectl commands use `-n app-deployment` by default - change this to your namespace name
- You can have multiple instances of this app running in different namespaces on the same cluster
- We use `imagePullPolicy: Never` so Kubernetes doesn't try to download the images
- Each pod requests CPU and memory - this keeps things from crashing due to resource hunger
- Health checks restart pods that aren't responding
- The frontend is on NodePort (accessible from outside the cluster)
- Backend and postgres are ClusterIP (only accessible from inside Kubernetes)

---

## Pro Tips

- **Custom Namespace**: Use `./setup-custom-namespace.sh` for easy multi-environment deployments
- **Set default namespace**: `kubectl config set-context --current --namespace=my-namespace` (saves typing `-n` flag)
- Use `kubectl get events -n app-deployment --sort-by='.lastTimestamp'` to see a timeline of what happened
- Port-forward is handy for debugging: `kubectl port-forward -n app-deployment pod/<name> 5000:5000`
- Check resource usage: `kubectl top pods -n app-deployment` (requires metrics server)
- Use `kubectx` and `kubens` tools to switch between clusters and namespaces faster
- Add this to your shell profile (~/.bashrc or ~/.zshrc) to auto-set docker env: `eval $(minikube docker-env)`
- Deploy multiple instances: Create different namespaces and run the helper script multiple times for dev, staging, and production

---

Good luck! Let me know if you hit any snags.
