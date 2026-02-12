# Kubernetes Deployment Guide - Assignment 3

Deploy a three-tier application to your Kubernetes cluster with automatic startup order management!

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

## Quick Deployment

### Prerequisites

- **kubectl** - Connected to your Kubernetes cluster
- **Namespace "ushakanth"** - Already created
- **Docker images** - Pushed to Docker Hub or your registry

### Step 1: Build and Push Docker Images

```bash
cd ../assignment1

# Build the images
docker build -t backend:latest ./backend
docker build -t frontend:latest ./frontend

# Tag and push to Docker Hub
docker tag backend:latest ushakanth24/backend:latest
docker tag frontend:latest ushakanth24/frontend:latest

docker push ushakanth24/backend:latest
docker push ushakanth24/frontend:latest
```

**Other Registry Options:**
- AWS ECR: `123456789.dkr.ecr.us-east-1.amazonaws.com/backend:latest`
- GCP GCR: `gcr.io/your-project/backend:latest`
- Azure ACR: `your-registry.azurecr.io/backend:latest`

### Step 2: Verify Cluster Connection

```bash
kubectl config current-context
kubectl get nodes
kubectl get namespaces | grep ushakanth
```

### Step 3: Deploy to Kubernetes

**No storage class needed!** The database uses temporary storage (perfect for testing/development).

```bash
cd ../assignment3

# Deploy all layers (init containers will manage startup order)
kubectl apply -f postgres/ -f backend/ -f frontend/ -n ushakanth

# Note: Don't apply the pvc.yaml - we're using emptyDir instead
```

**Or deploy step-by-step (see each layer start):**

```bash
# Deploy postgres first
kubectl apply -f postgres/ -n ushakanth
kubectl get pods -n ushakanth -w
# Wait until postgres shows Running (Ctrl+C)

# Deploy backend (init container waits for postgres)
kubectl apply -f backend/ -n ushakanth
kubectl get pods -n ushakanth -w
# Wait until both backend pods show Running (Ctrl+C)

# Deploy frontend (init container waits for backend)
kubectl apply -f frontend/ -n ushakanth
kubectl get pods -n ushakanth -w
# Wait until frontend pods show Running (Ctrl+C)
```

### Step 4: Monitor Deployment

```bash
# Watch all pods
kubectl get pods -n ushakanth -w

# Check services
kubectl get svc -n ushakanth

# View all resources
kubectl get all -n ushakanth
```

### Step 5: Access Your Application

**Option A: Using NodePort**
```bash
kubectl get svc frontend -n ushakanth
# Note the PORT(S) value (should be something like 80:30080/TCP)
# Visit: http://<your-cluster-ip>:30080
```

**Option B: Port Forwarding**
```bash
kubectl port-forward -n ushakanth svc/frontend 8080:80
# Visit: http://localhost:8080
```

**Option C: LoadBalancer (Cloud Only)**

Edit `frontend/service.yaml` and change:
```yaml
spec:
  type: LoadBalancer  # Instead of NodePort
```

Then:
```bash
kubectl apply -f frontend/service.yaml -n ushakanth
kubectl get svc frontend -n ushakanth
# Wait for EXTERNAL-IP to be assigned
```

---

## Database Storage Explained

This deployment uses **emptyDir** for database storage:

- **What it is**: Temporary storage that lives on the node
- **When data is lost**: When the pod is deleted or restarts
- **Good for**: Testing, development, demos
- **NOT good for**: Production (use PVC + StorageClass for production)

### For Production - Use PersistentVolume

To add persistent storage:

1. Enable your StorageClass (AWS EBS, Azure Disk, etc.)
2. Update `postgres/pvc.yaml` with your storage class
3. Update `postgres/deployment.yaml` to use the PVC

For now, emptyDir keeps things simple!

Each deployment uses init containers to ensure proper startup order:

**Postgres**: No dependencies, starts immediately

**Backend**: Has init container that:
- Waits for postgres:5432 to be listening
- Only then starts Flask application

**Frontend**: Has init container that:
- Waits for backend:5000 to be listening
- Only then starts Nginx

This prevents "host not found" and connection errors!

---

## Pod States Explained

| State | Meaning |
|-------|---------|
| `Pending` | Waiting for node resources |
| `Init:0/1` | Running init container (waiting for dependency) |
| `Running` | Pod is healthy and ready |
| `CrashLoopBackOff` | Pod keeps crashing - check logs |

### Init Containers are Normal!

If you see `Init:0/1`, the init container is working:

```bash
# Check init container logs
kubectl logs -n ushakanth <pod-name> -c wait-for-backend
kubectl logs -n ushakanth <pod-name> -c wait-for-postgres

# This just means it's waiting - be patient!
```

---

## Configuration Management

### Backend (backend/configmap.yaml)

```yaml
FLASK_ENV: development
DATABASE_HOST: postgres
DATABASE_USER: admin
DATABASE_PASSWORD: password123
SECRET_KEY: dev-secret-key
CORS_ORIGINS: http://localhost:3000,http://frontend:80
```

### Frontend (frontend/configmap.yaml)

```yaml
BACKEND_API_URL: http://backend:5000
APP_NAME: Python Docker App
APP_VERSION: "1.0.0"
NGINX_WORKER_PROCESSES: "auto"
```

### Database (postgres/configmap.yaml)

```yaml
POSTGRES_DB: python_app_db
POSTGRES_USER: admin
POSTGRES_PASSWORD: password123
```

### Update Configuration

1. Edit the ConfigMap file
2. Apply changes:
   ```bash
   kubectl apply -f backend/configmap.yaml -n ushakanth
   ```
3. Restart the deployment:
   ```bash
   kubectl rollout restart deployment/backend -n ushakanth
   ```

---

## Troubleshooting

### Init Containers Waiting Too Long?

```bash
# Check init container status
kubectl get pods -n ushakanth

# View init container logs (normal to see "waiting for..." messages)
kubectl logs -n ushakanth <pod-name> -c wait-for-backend
kubectl logs -n ushakanth <pod-name> -c wait-for-postgres
```

### Postgres Stuck in Pending?

With emptyDir, this shouldn't happen. If it does:

```bash
kubectl describe pod -n ushakanth postgres-xxxxx
```

Check the Events section for errors.

### Pods CrashLoopBackOff?

Check logs:

```bash
kubectl logs -n ushakanth -l app=backend --tail=50
kubectl logs -n ushakanth -l app=frontend --tail=50
kubectl logs -n ushakanth -l app=postgres --tail=50
```

### Still Having Issues?

Get detailed info:

```bash
kubectl describe pod -n ushakanth <pod-name>
# Look at Events section at the bottom
```

---

## Useful Commands

```bash
# See all pods
kubectl get pods -n ushakanth

# See all services
kubectl get svc -n ushakanth

# View pod logs
kubectl logs -n ushakanth -l app=backend
kubectl logs -n ushakanth <specific-pod-name>

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

## Using a Different Namespace

To use a different namespace:

```bash
# Create new namespace
kubectl create namespace my-namespace

# Update all files
find . -name "*.yaml" -exec sed -i 's/namespace: ushakanth/namespace: my-namespace/g' {} \;

# Deploy
kubectl apply -f postgres/ -f backend/ -f frontend/ -n my-namespace
```

---

## Clean Up

```bash
# Delete all resources in namespace
kubectl delete -f postgres/ -f backend/ -f frontend/ -n ushakanth

# Or delete entire namespace (deletes everything in it)
kubectl delete namespace ushakanth
```

---

## Docker Images and Registry Configuration

### Current Setup with Kubernetes Secrets

✅ **Kubernetes Secret Configured:** `dockerhub-secret`

**Frontend deployment** is configured to pull images using the Docker registry secret for authentication.

- **Frontend**: Public image on Docker Hub (pulls via secret - `dockerhub-secret`)
- **Backend**: Public image on Docker Hub (pulls without secret)
- **Database**: PostgreSQL (no image registry needed)

### Secret Configuration Details

The secret `dockerhub-secret` is created with Docker Hub credentials and allows the frontend deployment to authenticate when pulling images.

**To verify the secret:**

```bash
# Check if secret exists in namespace ushakanth
kubectl get secret dockerhub-secret -n ushakanth

# View secret details
kubectl describe secret dockerhub-secret -n ushakanth
```

### Apply Frontend Deployment with Secret Authentication

```bash
# Apply the frontend deployment that uses imagePullSecrets
kubectl apply -f frontend/deployment.yaml -n ushakanth

# Restart frontend pods to pull with credentials
kubectl delete pod -l app=frontend -n ushakanth

# Watch pods come up
kubectl get pods -n ushakanth -w
```

### Making Frontend Image Private (Optional)

If you want to make the Docker Hub frontend repository private:

1. Go to https://hub.docker.com/r/ushakanth24/frontend → Settings → Visibility → **Private**

The frontend deployment will continue to work with the secret credentials.

### Creating/Updating the Secret

If you need to create a new secret or update credentials:

```bash
# Generate a Personal Access Token at https://hub.docker.com/settings/security

# Create the secret
kubectl create secret docker-registry dockerhub-secret \
  --docker-server=https://index.docker.io/v1/ \
  --docker-username=ushakanth24 \
  --docker-password=<your-access-token> \
  --docker-email=ushakanth24@gmail.com \
  -n ushakanth

# Or update existing secret
kubectl delete secret dockerhub-secret -n ushakanth
kubectl create secret docker-registry dockerhub-secret \
  --docker-server=https://index.docker.io/v1/ \
  --docker-username=ushakanth24 \
  --docker-password=<your-access-token> \
  --docker-email=ushakanth24@gmail.com \
  -n ushakanth

# Restart frontend pods to use new credentials
kubectl delete pod -l app=frontend -n ushakanth
```

---

**Namespace:** ushakanth  
**Status:** Production-ready with automatic startup order management and private image registry
