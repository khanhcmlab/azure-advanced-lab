# FastAPI PostgreSQL Sample App - Docker Setup

This directory contains Docker configuration files to run the FastAPI PostgreSQL sample application locally using Docker Compose.

## Quick Start

1. **Build and start the services:**
   ```bash
   docker-compose up --build
   ```

2. **Access the application:**
   - FastAPI app: http://localhost:8000
   - FastAPI docs: http://localhost:8000/docs
   - pgAdmin: http://localhost:8080 (admin@fastapi.com / admin)

3. **Stop the services:**
   ```bash
   docker-compose down
   ```

## Services

### FastAPI Application
- **Port:** 8000
- **Container:** fastapi-app
- **Features:** 
  - Hot reload enabled for development
  - Automatic database seeding
  - Health checks

### PostgreSQL Database
- **Port:** 5432
- **Container:** fastapi-postgres
- **Database:** fastapi_db
- **User:** fastapi_user
- **Password:** fastapi_password

### pgAdmin (Database Management)
- **Port:** 8080
- **Container:** fastapi-pgadmin
- **Email:** admin@fastapi.com
- **Password:** admin

## Environment Variables

The Docker Compose setup uses the following environment variables:

- `DBNAME`: Database name
- `DBHOST`: Database host (postgres service)
- `DBPORT`: Database port (5432)
- `DBUSER`: Database user
- `DBPASS`: Database password
- `AZURE_POSTGRESQL_CONNECTIONSTRING`: Full connection string

## Development

### File Watching
The FastAPI service is configured with volume mounts for hot reload:
- `./src` → `/app/src`
- `./static` → `/app/static`
- `./templates` → `/app/templates`

### Database Persistence
PostgreSQL data is persisted using Docker volumes:
- `postgres_data`: Database files
- `pgadmin_data`: pgAdmin configuration

### Logs
View logs for specific services:
```bash
# All services
docker-compose logs -f

# FastAPI app only
docker-compose logs -f fastapi-app

# PostgreSQL only
docker-compose logs -f postgres
```

## Commands

### Full Reset
To completely reset the environment:
```bash
docker-compose down -v  # Remove containers and volumes
docker-compose up --build  # Rebuild and start
```

### Database Shell Access
```bash
docker-compose exec postgres psql -U fastapi_user -d fastapi_db
```

### Application Shell Access
```bash
docker-compose exec fastapi-app bash
```

## Troubleshooting

1. **Port conflicts:** Make sure ports 8000, 5432, and 8080 are not in use
2. **Database connection issues:** Wait for the postgres service health check to pass
3. **Permission issues:** Ensure the entrypoint script is executable (`chmod +x src/entrypoint.sh`)

## Production Considerations

For production deployment:
1. Use environment-specific `.env` files
2. Configure proper secrets management
3. Set up SSL/TLS certificates
4. Use production-grade PostgreSQL configuration
5. Configure proper logging and monitoring