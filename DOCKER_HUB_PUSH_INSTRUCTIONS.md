# Docker Hub Push Instructions

Complete guide to build, tag, and push your Docker images to Docker Hub.

## Prerequisites

- Docker installed (v20.10 or higher)
- Docker Compose installed (v1.29 or higher)
- Docker Hub account created at https://hub.docker.com
- Internet connection

## Step 1: Login to Docker Hub

Open a terminal and run:

```bash
docker login
```

Enter your Docker Hub username and password when prompted.

**Verification:**
```bash
docker info
```

You should see your username listed in the output.

---

## Step 2: Navigate to Project Directory

```bash
cd c:\docker_workspace\docker-assignment1\assignment1
```

Or on Ubuntu:
```bash
cd /path/to/assignment1
```

---

## Step 3: Build Images

Build all containers using Docker Compose:

```bash
docker compose build
```

This builds two images:
- `assignment1-backend:latest`
- `assignment1-frontend:latest`

**Verify images were built:**
```bash
docker images
```

---

## Step 4: Tag Images for Docker Hub

Replace `ushakanth24` with your actual Docker Hub username.

### Tag Backend Image

```bash
docker tag assignment1-backend:latest ushakanth24/python_backend:v1.0.0
docker tag assignment1-backend:latest ushakanth24/python_backend:latest
```

### Tag Frontend Image

```bash
docker tag assignment1-frontend:latest ushakanth24/web_frontend:v1.0.0
docker tag assignment1-frontend:latest ushakanth24/web_frontend:latest
```

**Example (if your username is "john_dev"):**
```bash
docker tag assignment1-backend:latest john_dev/python_backend:v1.0.0
docker tag assignment1-backend:latest john_dev/python_backend:latest

docker tag assignment1-frontend:latest john_dev/web_frontend:v1.0.0
docker tag assignment1-frontend:latest john_dev/web_frontend:latest
```

**Verify tags:**
```bash
docker images | grep "ushakanth24"
```

---

## Step 5: Push Images to Docker Hub

### Push Backend Image

```bash
docker push ushakanth24/python_backend:v1.0.0
docker push ushakanth24/python_backend:latest
```

**Expected output:** Progress bars showing upload status

### Push Frontend Image

```bash
docker push ushakanth24/web_frontend:v1.0.0
docker push ushakanth24/web_frontend:latest
```

**Expected output:** Progress bars showing upload status

---

## Step 6: Verify on Docker Hub

1. Open https://hub.docker.com and log in
2. Navigate to "Repositories"
3. Verify both repositories appear:
   - `python_backend`
   - `web_frontend`
4. Click on each repository to see the tags (v1.0.0, latest)

---

## Step 7: (Optional) Update docker-compose.yml

To use your pushed images instead of building locally:

### Backup original file

```bash
cp docker-compose.yml docker-compose.yml.backup
```

### Update docker-compose.yml

Change the backend service from:

```yaml
backend:
  build:
    context: ./backend
    dockerfile: Dockerfile
```

To:

```yaml
backend:
  image: ushakanth24/python_backend:v1.0.0
```

Change the frontend service from:

```yaml
frontend:
  build:
    context: ./frontend
    dockerfile: Dockerfile
```

To:

```yaml
frontend:
  image: ushakanth24/web_frontend:v1.0.0
```

---

## Step 8: Test with Pushed Images

```bash
docker compose pull
docker compose up
```

This pulls your images from Docker Hub instead of building locally.

---

## Troubleshooting

### "docker login" fails
- Verify Docker Hub credentials
- Check internet connection
- Run `docker logout` and try again

### "permission denied" when pushing
- Ensure you created repositories on Docker Hub first
- Repository names must match your username/repository format
- Check you're logged in: `docker login`

### Image not appearing on Docker Hub
- Verify the push completed without errors
- Check repository permissions
- Try pushing again: `docker push ushakanth24/python_backend:v1.0.0`

### Port conflicts
- If containers fail to start, check if ports are in use:
  - Frontend: 3000
  - Backend: 5000
  - PostgreSQL: 5432

---

## Useful Commands

**List all images:**
```bash
docker images
```

**Remove a tag:**
```bash
docker rmi ushakanth24/python_backend:v1.0.0
```

**View push history:**
```bash
docker history ushakanth24/python_backend:v1.0.0
```

**Logout from Docker Hub:**
```bash
docker logout
```

---

## Next Steps

1. Share repository URL with team: `https://hub.docker.com/r/ushakanth24/python_backend`
2. Create README files in Docker Hub (optional)
3. Set up automated builds (optional)
4. Create more versions/tags as needed

---

## Reference

- Docker Hub: https://hub.docker.com
- Docker Push Documentation: https://docs.docker.com/engine/reference/commandline/push/
- Docker Tag Documentation: https://docs.docker.com/engine/reference/commandline/tag/
