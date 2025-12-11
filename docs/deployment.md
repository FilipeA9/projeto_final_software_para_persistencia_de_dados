# Tourism Platform - Deployment Guide

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development](#local-development)
3. [Production Deployment](#production-deployment)
4. [Docker Deployment](#docker-deployment)
5. [Environment Variables](#environment-variables)
6. [Database Setup](#database-setup)
7. [Monitoring & Logging](#monitoring--logging)
8. [Backup & Recovery](#backup--recovery)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

- **Python 3.11+**
- **Docker & Docker Compose** (for containerized deployment)
- **PostgreSQL 15** (if not using Docker)
- **MongoDB 7** (if not using Docker)
- **Redis 7** (if not using Docker)
- **Git**

### System Requirements

**Minimum**:
- CPU: 2 cores
- RAM: 4 GB
- Storage: 20 GB

**Recommended**:
- CPU: 4+ cores
- RAM: 8+ GB
- Storage: 50+ GB (SSD preferred)

---

## Local Development

### 1. Clone Repository

```bash
git clone <repository_url>
cd turistando
```

### 2. Setup Backend

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your settings
```

### 3. Start Docker Services

```bash
# From project root
docker-compose up -d

# Wait for services to be healthy
docker ps
```

### 4. Initialize Database

```bash
cd backend
python init_db_simple.py
```

### 5. Start Backend Server

```bash
cd backend
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### 6. Setup Frontend

```bash
# Open new terminal
cd frontend

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Start Streamlit
streamlit run src/Home.py
```

---

## Production Deployment

### Option 1: Traditional Server Deployment

#### 1. Server Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python
sudo apt install python3.11 python3.11-venv python3-pip -y

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Install MongoDB
# Follow official MongoDB installation guide

# Install Redis
sudo apt install redis-server -y

# Install Nginx (for reverse proxy)
sudo apt install nginx -y
```

#### 2. Create Application User

```bash
sudo useradd -m -s /bin/bash turistando
sudo su - turistando
```

#### 3. Deploy Application

```bash
# Clone repository
git clone <repository_url> /home/turistando/app
cd /home/turistando/app

# Setup backend
cd backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Setup environment
cp .env.example .env
nano .env  # Configure production settings
```

#### 4. Configure Systemd Service

Create `/etc/systemd/system/turistando-api.service`:

```ini
[Unit]
Description=Turistando API
After=network.target postgresql.service mongodb.service redis.service

[Service]
Type=notify
User=turistando
Group=turistando
WorkingDirectory=/home/turistando/app/backend
Environment="PATH=/home/turistando/app/backend/venv/bin"
ExecStart=/home/turistando/app/backend/venv/bin/uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable turistando-api
sudo systemctl start turistando-api
sudo systemctl status turistando-api
```

#### 5. Configure Nginx Reverse Proxy

Create `/etc/nginx/sites-available/turistando`:

```nginx
upstream turistando_api {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name your-domain.com;

    client_max_body_size 10M;

    location / {
        proxy_pass http://turistando_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /uploads {
        alias /home/turistando/app/uploads;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

Enable site:

```bash
sudo ln -s /etc/nginx/sites-available/turistando /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### 6. SSL Certificate (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

---

## Docker Deployment

### Production Docker Compose

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    restart: always
    environment:
      POSTGRES_DB: turistando_db
      POSTGRES_USER: turistando
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - turistando_network

  mongodb:
    image: mongo:7
    restart: always
    environment:
      MONGO_INITDB_ROOT_USERNAME: turistando
      MONGO_INITDB_ROOT_PASSWORD: ${MONGO_PASSWORD}
    volumes:
      - mongodb_data:/data/db
    networks:
      - turistando_network

  redis:
    image: redis:7-alpine
    restart: always
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    networks:
      - turistando_network

  api:
    build:
      context: ./backend
      dockerfile: Dockerfile
    restart: always
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://turistando:${POSTGRES_PASSWORD}@postgres:5432/turistando_db
      MONGODB_URL: mongodb://turistando:${MONGO_PASSWORD}@mongodb:27017
      REDIS_URL: redis://:${REDIS_PASSWORD}@redis:6379
    depends_on:
      - postgres
      - mongodb
      - redis
    volumes:
      - ./uploads:/app/uploads
    networks:
      - turistando_network

volumes:
  postgres_data:
  mongodb_data:
  redis_data:

networks:
  turistando_network:
    driver: bridge
```

Create `backend/Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

Deploy:

```bash
docker-compose -f docker-compose.prod.yml up -d
```

---

## Environment Variables

### Backend (.env)

```ini
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/turistando_db
MONGODB_URL=mongodb://user:password@localhost:27017
MONGODB_DB_NAME=turistando
REDIS_URL=redis://localhost:6379

# JWT
SECRET_KEY=your-secret-key-here-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# API
API_TITLE=Tourism Platform API
API_VERSION=1.0.0
API_V1_PREFIX=/api
ALLOWED_ORIGINS=http://localhost:8501,http://localhost:3000

# Logging
LOG_LEVEL=INFO

# Upload
UPLOAD_DIR=../uploads
MAX_UPLOAD_SIZE=5242880  # 5 MB
```

### Production Security

- Use strong, randomly generated passwords
- Store secrets in environment variables or secret management service
- Never commit `.env` files to version control
- Rotate secrets regularly

---

## Database Setup

### PostgreSQL Configuration

```bash
# Connect to PostgreSQL
sudo -u postgres psql

# Create database and user
CREATE DATABASE turistando_db;
CREATE USER turistando WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE turistando_db TO turistando;
\q

# Run migrations
cd backend
alembic upgrade head
```

### MongoDB Configuration

```bash
# Connect to MongoDB
mongosh

# Switch to admin database
use admin

# Create user
db.createUser({
  user: "turistando",
  pwd: "secure_password",
  roles: [
    { role: "readWrite", db: "turistando" }
  ]
})
```

### Redis Configuration

Edit `/etc/redis/redis.conf`:

```conf
requirepass your_redis_password
maxmemory 256mb
maxmemory-policy allkeys-lru
```

Restart Redis:

```bash
sudo systemctl restart redis
```

---

## Monitoring & Logging

### Application Logs

Logs are stored in `backend/logs/`:
- `turistando_YYYYMMDD.log`: Daily rotating logs
- Maximum 10 MB per file
- 5 backup files retained

### View Logs

```bash
# Real-time logs
tail -f backend/logs/turistando_$(date +%Y%m%d).log

# Systemd service logs
sudo journalctl -u turistando-api -f

# Docker logs
docker logs -f turistando-api
```

### Monitoring Tools

**Recommended**:
- **Prometheus**: Metrics collection
- **Grafana**: Visualization
- **Sentry**: Error tracking
- **Uptime Kuma**: Uptime monitoring

---

## Backup & Recovery

### Database Backups

#### PostgreSQL

```bash
# Backup
pg_dump -U turistando turistando_db > backup_$(date +%Y%m%d).sql

# Restore
psql -U turistando turistando_db < backup_20240101.sql
```

#### MongoDB

```bash
# Backup
mongodump --uri="mongodb://turistando:password@localhost:27017/turistando" --out=/backup

# Restore
mongorestore --uri="mongodb://turistando:password@localhost:27017/turistando" /backup/turistando
```

### Automated Backups

Create `/usr/local/bin/backup-turistando.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/backups/turistando"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup PostgreSQL
pg_dump -U turistando turistando_db | gzip > $BACKUP_DIR/postgres_$DATE.sql.gz

# Backup MongoDB
mongodump --uri="mongodb://turistando:password@localhost:27017/turistando" --out=$BACKUP_DIR/mongo_$DATE

# Keep only last 7 days
find $BACKUP_DIR -type f -mtime +7 -delete

echo "Backup completed: $DATE"
```

Add to crontab:

```bash
0 2 * * * /usr/local/bin/backup-turistando.sh
```

---

## Troubleshooting

### API Not Starting

**Check logs**:
```bash
sudo journalctl -u turistando-api -n 50
```

**Common issues**:
- Database connection failed: Check credentials in `.env`
- Port already in use: Change port or stop conflicting service
- Import errors: Reinstall dependencies

### Database Connection Issues

**Test PostgreSQL**:
```bash
psql -U turistando -h localhost -d turistando_db
```

**Test MongoDB**:
```bash
mongosh "mongodb://turistando:password@localhost:27017/turistando"
```

**Test Redis**:
```bash
redis-cli -a your_password ping
```

### Performance Issues

**Check resource usage**:
```bash
htop
docker stats
```

**Optimize queries**:
- Add database indexes
- Increase cache TTL
- Scale workers

### High Memory Usage

**Reduce worker count**:
```bash
# In systemd service
ExecStart=.../uvicorn ... --workers 2
```

**Increase cache memory limit** in Redis.

---

## Security Checklist

- [ ] Change default passwords
- [ ] Enable firewall (UFW/iptables)
- [ ] Setup SSL/TLS certificates
- [ ] Configure rate limiting
- [ ] Enable audit logging
- [ ] Regular security updates
- [ ] Backup encryption
- [ ] Access control lists
- [ ] Monitor failed login attempts

---

## Support & Maintenance

### Regular Maintenance

1. **Weekly**: Check logs for errors
2. **Monthly**: Update dependencies
3. **Quarterly**: Review security configurations
4. **Annually**: Audit access controls

### Update Application

```bash
cd /home/turistando/app
git pull origin main
cd backend
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
sudo systemctl restart turistando-api
```

---

## Conclusion

This guide covers the essential steps for deploying the Tourism Platform in production. Adjust configurations based on your specific infrastructure and requirements.

For additional support, refer to the main README.md and API documentation.
