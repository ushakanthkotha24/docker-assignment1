# User Management Application with Docker Compose

This is a full-stack Python application built with Flask, PostgreSQL, and a modern web frontend.

## Project Structure

```
assignment1/
├── docker-compose.yml          # Docker Compose configuration
├── .env                        # Environment variables
├── backend/                    # Python Flask Backend
│   ├── Dockerfile             # Backend container definition
│   ├── requirements.txt        # Python dependencies
│   ├── app.py                 # Flask application with API endpoints
│   └── config.py              # Configuration management
├── frontend/                   # Web Frontend
│   ├── Dockerfile             # Frontend container definition
│   ├── nginx.conf             # Nginx web server configuration
│   ├── index.html             # Main HTML page
│   ├── style.css              # Cascading style sheets
│   └── script.js              # JavaScript application logic
└── postgres/                   # PostgreSQL Database
    └── init.sql               # Database initialization script
```

## Features

- **Backend API**: Flask-based REST API with CORS support
- **Database**: PostgreSQL with automatic initialization
- **Frontend**: Responsive web interface with user management
- **Docker**: Complete containerization with Docker Compose
- **User Management**: Create, read, update, and delete users
- **Health Checks**: Status monitoring for API and database connections

## Prerequisites

- Docker (v20.10 or higher)
- Docker Compose (v1.29 or higher)
- No need to install Python or PostgreSQL locally

## Quick Start

### 1. Start the Application

Navigate to the project directory and run:

```bash
docker-compose up
```

For background execution:

```bash
docker-compose up -d
```

### 2. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000
- **PostgreSQL**: localhost:5432

### 3. Default Credentials

- Database User: `admin`
- Database Password: `password123`
- Database Name: `python_app_db`

## Available API Endpoints

### Health Checks
- `GET /api/health` - Check if API is running
- `GET /api/database-status` - Check database connection

### User Management
- `GET /api/users` - Get all users
- `POST /api/users` - Create a new user
- `GET /api/users/<id>` - Get a specific user
- `PUT /api/users/<id>` - Update a user
- `DELETE /api/users/<id>` - Delete a user

## API Request Examples

### Create a User
```bash
curl -X POST http://localhost:5000/api/users \
  -H "Content-Type: application/json" \
  -d '{"username":"john_doe","email":"john@example.com"}'
```

### Get All Users
```bash
curl http://localhost:5000/api/users
```

### Delete a User
```bash
curl -X DELETE http://localhost:5000/api/users/1
```

## Services

### PostgreSQL Database
- Container name: `postgres_db`
- Port: 5432
- Automatic initialization with sample data
- Health checks enabled

### Python Backend
- Container name: `python_backend`
- Port: 5000
- Flask development server
- Automatic dependency installation

### Frontend Server
- Container name: `web_frontend`
- Port: 3000
- Nginx web server
- Reverse proxy to backend API

## Development

### View Logs
```bash
docker-compose logs -f backend
docker-compose logs -f postgres
docker-compose logs -f frontend
```

### Stop the Application
```bash
docker-compose down
```

### Remove All Data
```bash
docker-compose down -v
```

## Environment Variables

Edit the `.env` file to customize:
- Flask environment settings
- Database credentials
- Server ports
- Application configuration

## Troubleshooting

### Database Connection Issues
- Ensure PostgreSQL container has started: `docker-compose ps`
- Check database logs: `docker-compose logs postgres`
- Verify credentials in `.env` file

### Frontend Cannot Reach Backend
- Check if backend service is running
- Verify API endpoint in frontend/script.js
- Check Nginx configuration in frontend/nginx.conf

### Port Already in Use
- Change ports in docker-compose.yml and .env
- Or stop other services using the ports

## Technologies Used

- **Backend**: Python 3.9, Flask, SQLAlchemy
- **Database**: PostgreSQL 14
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Server**: Nginx
- **Containerization**: Docker, Docker Compose

## Notes

- The application includes sample user data on first startup
- All API responses are in JSON format
- CORS is enabled for cross-origin requests
- Nginx acts as reverse proxy and static file server
- Database uses persistent volumes for data retention

## License

This project is provided as-is for educational purposes.
