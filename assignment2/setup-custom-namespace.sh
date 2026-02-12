#!/bin/bash

# =============================================================================
# Kubernetes Custom Namespace Setup Helper
# =============================================================================
# 
# This script makes it easy to deploy your app to its own custom 
# namespace instead of using the default 'app-deployment' namespace.
#
# Why would you want this?
# - Run multiple versions of the app on the same cluster (dev, staging, prod)
# - Keep different projects separated and organized
# - Easy to manage and clean up individual deployments
#
# What does this script do?
# 1. Asks you for your custom namespace name
# 2. Creates the namespace in Kubernetes
# 3. Automatically updates all config files with your namespace name
# 4. Deploys PostgreSQL, backend, and frontend
# 5. Shows you how to access your app
#
# =============================================================================

set -e  # Exit immediately if any command fails

# Define colors for output
GREEN='\033[0;32m'      # Success messages
BLUE='\033[0;34m'       # Info messages
YELLOW='\033[1;33m'     # Warnings and important info
RED='\033[0;31m'        # Errors
NC='\033[0m'            # No Color (reset)

echo -e "${BLUE}====================================================================${NC}"
echo -e "${BLUE}   Kubernetes Custom Namespace Setup Helper${NC}"
echo -e "${BLUE}   Deploy your app in its own custom namespace${NC}"
echo -e "${BLUE}====================================================================${NC}"
echo ""

# Ask the user for a namespace name
read -p "What would you like to name your namespace? (default: app-deployment): " NAMESPACE
NAMESPACE=${NAMESPACE:-app-deployment}

echo ""
echo -e "${YELLOW}Using namespace: ${GREEN}$NAMESPACE${NC}"
echo ""

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}Error: kubectl is not installed.${NC}"
    echo "Please install kubectl first: https://kubernetes.io/docs/tasks/tools/"
    echo ""
    exit 1
fi

# =============================================================================
# Step 1: Create the namespace
# =============================================================================
echo -e "${BLUE}-------------------------------------------------------------------${NC}"
echo -e "${BLUE}Step 1: Creating namespace${NC}"
echo -e "${BLUE}-------------------------------------------------------------------${NC}"

if kubectl get namespace "$NAMESPACE" &> /dev/null; then
    echo -e "${YELLOW}Note: Namespace '$NAMESPACE' already exists${NC}"
else
    kubectl create namespace "$NAMESPACE"
    echo -e "${GREEN}[OK] Namespace '$NAMESPACE' created${NC}"
fi

# =============================================================================
# Step 2: Update all configuration files
# =============================================================================
echo ""
echo -e "${BLUE}-------------------------------------------------------------------${NC}"
echo -e "${BLUE}Step 2: Updating configuration files${NC}"
echo -e "${BLUE}-------------------------------------------------------------------${NC}"
echo "Scanning and updating YAML files..."

find . -name "*.yaml" -not -path "./.git/*" -not -path "./setup-custom-namespace.sh" \
    -exec sed -i.bak "s/namespace: app-deployment/namespace: $NAMESPACE/g" {} \; \
    -print

echo -e "${GREEN}[OK] All configuration files updated${NC}"

# =============================================================================
# Step 3: Deploy the application
# =============================================================================
echo ""
echo -e "${BLUE}-------------------------------------------------------------------${NC}"
echo -e "${BLUE}Step 3: Deploying application${NC}"
echo -e "${BLUE}-------------------------------------------------------------------${NC}"
echo "Deploying: Database -> Backend -> Frontend"
echo ""

echo "Setting up namespace..."
kubectl apply -f namespace.yaml
echo -e "${GREEN}[OK] Namespace ready${NC}"

sleep 2

echo "Deploying PostgreSQL database..."
kubectl apply -f postgres/
echo -e "${GREEN}[OK] Database deployed${NC}"

sleep 2

echo "Deploying backend API..."
kubectl apply -f backend/
echo -e "${GREEN}[OK] Backend deployed${NC}"

sleep 2

echo "Deploying frontend web server..."
kubectl apply -f frontend/
echo -e "${GREEN}[OK] Frontend deployed${NC}"

# =============================================================================
# Step 4: Wait for deployments
# =============================================================================
echo ""
echo -e "${BLUE}-------------------------------------------------------------------${NC}"
echo -e "${BLUE}Step 4: Waiting for startup (this may take a minute)${NC}"
echo -e "${BLUE}-------------------------------------------------------------------${NC}"

echo "Checking database..."
kubectl rollout status deployment/postgres -n "$NAMESPACE" || true

echo "Checking backend..."
kubectl rollout status deployment/backend -n "$NAMESPACE" || true

echo "Checking frontend..."
kubectl rollout status deployment/frontend -n "$NAMESPACE" || true

# =============================================================================
# Summary
# =============================================================================
echo ""
echo -e "${BLUE}====================================================================${NC}"
echo -e "${GREEN}[OK] Deployment Complete - Your app is running!${NC}"
echo -e "${BLUE}====================================================================${NC}"
echo ""

echo -e "${YELLOW}Resources in namespace '$NAMESPACE':${NC}"
kubectl get all -n "$NAMESPACE"

echo ""
echo -e "${YELLOW}How to Access Your App:${NC}"
echo "Run this command to open it in your browser:"
echo -e "${GREEN}  minikube service frontend -n $NAMESPACE${NC}"

echo ""
echo -e "${YELLOW}Common Tasks:${NC}"
echo "  List all pods:"
echo "    kubectl get pods -n $NAMESPACE"
echo ""
echo "  View live logs from backend:"
echo "    kubectl logs -n $NAMESPACE -l app=backend -f"
echo ""
echo "  Forward frontend to localhost:"
echo "    kubectl port-forward -n $NAMESPACE svc/frontend 3000:80"
echo ""
echo "  Open a shell inside a pod:"
echo "    kubectl exec -it -n $NAMESPACE <pod-name> -- /bin/sh"
echo ""
echo -e "${YELLOW}To remove everything later:${NC}"
echo -e "${GREEN}  kubectl delete namespace $NAMESPACE${NC}"
echo ""

