# 🚀 Pied Piper 2.0 - Deployment Guide

Complete guide for deploying Pied Piper 2.0 to various environments.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development Deployment](#local-development-deployment)
3. [Docker Deployment](#docker-deployment)
4. [Production Server Deployment](#production-server-deployment)
5. [Blockchain Smart Contract Deployment](#blockchain-smart-contract-deployment)
6. [Cloud Deployment Options](#cloud-deployment-options)
7. [Environment Configuration](#environment-configuration)
8. [Troubleshooting](#troubleshooting)

---

## 🔧 Prerequisites

### Required Software
- **Python 3.8+** ([Download](https://www.python.org/downloads/))
- **Node.js 16+** (for blockchain features) ([Download](https://nodejs.org/))
- **Git** ([Download](https://git-scm.com/downloads))
- **Docker** (optional, for containerized deployment) ([Download](https://www.docker.com/))

### Required Accounts
- **Pinata IPFS** account for decentralized storage ([Sign up](https://pinata.cloud/))
- **Polygon Amoy** testnet account (for blockchain features)
- **PostgreSQL** database (for LandGuard features)

---

## 💻 Local Development Deployment

### Quick Start

#### Windows (PowerShell)
```powershell
# Clone the repository
git clone https://github.com/Parthkk90/compression-.git
cd compression-

# Run automated setup (recommended)
.\setup.ps1
```

#### Linux/Mac
```bash
# Clone the repository
git clone https://github.com/Parthkk90/compression-.git
cd compression-

# Run automated setup (recommended)
chmod +x setup.sh
./setup.sh
```

### Manual Setup

#### Step 1: Set Up PCC (Compression Core)
```bash
cd pcc

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Test the installation
python -c "from compressors import Compressor; print('PCC installed successfully!')"
```

#### Step 2: Set Up LandGuard (Backend API)
```bash
cd ../landguard

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your configurations

# Test the installation
python -m cli.landguard_cli --help
```

#### Step 3: Set Up Blockchain (Optional)
```bash
cd Blockchain

# Install Node.js dependencies
npm install

# Configure blockchain environment
cp .env.example .env
# Add your wallet private key and RPC URL

# Check account balance
npm run balance
```

---

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)

```bash
# Build and start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Individual Docker Container

```bash
# Build PCC container
docker build -t pied-piper-pcc -f Dockerfile.pcc .

# Run PCC container
docker run -p 8000:8000 -v $(pwd)/data:/app/data pied-piper-pcc

# Build LandGuard container
docker build -t pied-piper-landguard -f Dockerfile.landguard .

# Run LandGuard container
docker run -p 8001:8001 \
  -e DATABASE_URL=postgresql://user:pass@db:5432/landguard \
  pied-piper-landguard
```

---

## 🖥️ Production Server Deployment

### Ubuntu/Debian Server

#### Step 1: Prepare Server
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install -y python3.11 python3.11-venv python3-pip postgresql nginx

# Install Node.js (for blockchain)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
```

#### Step 2: Deploy Application
```bash
# Create application user
sudo useradd -m -s /bin/bash piedpiper
sudo su - piedpiper

# Clone repository
git clone https://github.com/Parthkk90/compression-.git
cd compression-

# Set up PCC
cd pcc
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn
deactivate

# Set up LandGuard
cd ../landguard
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn
deactivate

# Set up environment
cp .env.example .env
nano .env  # Configure your settings
```

#### Step 3: Create Systemd Services

**PCC Service** (`/etc/systemd/system/pcc.service`):
```ini
[Unit]
Description=Pied Piper PCC Service
After=network.target

[Service]
User=piedpiper
Group=piedpiper
WorkingDirectory=/home/piedpiper/compression-/pcc
Environment="PATH=/home/piedpiper/compression-/pcc/venv/bin"
ExecStart=/home/piedpiper/compression-/pcc/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker app:app --bind 127.0.0.1:8000

[Install]
WantedBy=multi-user.target
```

**LandGuard Service** (`/etc/systemd/system/landguard.service`):
```ini
[Unit]
Description=Pied Piper LandGuard Service
After=network.target postgresql.service

[Service]
User=piedpiper
Group=piedpiper
WorkingDirectory=/home/piedpiper/compression-/landguard
Environment="PATH=/home/piedpiper/compression-/landguard/venv/bin"
EnvironmentFile=/home/piedpiper/compression-/landguard/.env
ExecStart=/home/piedpiper/compression-/landguard/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker app:app --bind 127.0.0.1:8001

[Install]
WantedBy=multi-user.target
```

#### Step 4: Configure Nginx

```nginx
# /etc/nginx/sites-available/piedpiper
server {
    listen 80;
    server_name your-domain.com;

    # PCC API
    location /api/pcc/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # LandGuard API
    location /api/landguard/ {
        proxy_pass http://127.0.0.1:8001/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # Increase upload size for large files
    client_max_body_size 100M;
}
```

#### Step 5: Start Services
```bash
# Enable and start services
sudo systemctl enable pcc landguard
sudo systemctl start pcc landguard

# Enable nginx
sudo ln -s /etc/nginx/sites-available/piedpiper /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Check status
sudo systemctl status pcc landguard
```

#### Step 6: SSL Certificate (Recommended)
```bash
# Install certbot
sudo apt install -y certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal is configured automatically
```

---

## ⛓️ Blockchain Smart Contract Deployment

### Polygon Amoy Testnet

#### Step 1: Get Test MATIC
1. Visit [Polygon Faucet](https://faucet.polygon.technology/)
2. Select "Amoy" network
3. Enter your wallet address
4. Receive test MATIC

#### Step 2: Configure Deployment
```bash
cd landguard/Blockchain

# Install dependencies
npm install

# Create .env file
cat > .env << EOF
PRIVATE_KEY=your_wallet_private_key_here
POLYGON_AMOY_RPC_URL=https://rpc-amoy.polygon.technology
POLYGONSCAN_API_KEY=your_polygonscan_api_key
EOF

# Check balance
npm run balance
```

#### Step 3: Deploy Contracts
```bash
# Deploy to Amoy testnet
npm run deploy:amoy

# Note the deployed contract address
# Example output: Contract deployed to: 0x1234...
```

#### Step 4: Verify Contract (Optional)
```bash
# Verify on PolygonScan
npx hardhat verify --network amoy <CONTRACT_ADDRESS>
```

---

## ☁️ Cloud Deployment Options

### AWS EC2 Deployment

```bash
# Launch Ubuntu EC2 instance (t2.medium or higher recommended)
# Connect via SSH
ssh -i your-key.pem ubuntu@your-ec2-ip

# Follow Production Server Deployment steps above

# Configure Security Groups:
# - Allow HTTP (80)
# - Allow HTTPS (443)
# - Allow SSH (22) from your IP only
```

### Google Cloud Platform

```bash
# Create Compute Engine instance
gcloud compute instances create piedpiper \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --machine-type=e2-medium \
  --zone=us-central1-a

# SSH into instance
gcloud compute ssh piedpiper

# Follow Production Server Deployment steps
```

### DigitalOcean Droplet

```bash
# Create Ubuntu droplet (2GB RAM minimum)
# SSH into droplet
ssh root@your-droplet-ip

# Follow Production Server Deployment steps
```

### Heroku Deployment

```bash
# Install Heroku CLI
# Login to Heroku
heroku login

# Create app for PCC
cd pcc
heroku create your-app-pcc
git init
git add .
git commit -m "Initial commit"
git push heroku main

# Create app for LandGuard
cd ../landguard
heroku create your-app-landguard
heroku addons:create heroku-postgresql:mini
git init
git add .
git commit -m "Initial commit"
git push heroku main

# Set environment variables
heroku config:set PINATA_API_KEY=your_key
heroku config:set PINATA_SECRET_KEY=your_secret
```

---

## 🔐 Environment Configuration

### PCC Environment Variables
Create `pcc/.env`:
```bash
# IPFS/Pinata Configuration
PINATA_API_KEY=your_pinata_api_key
PINATA_SECRET_KEY=your_pinata_secret_key
PINATA_JWT=your_pinata_jwt_token

# Application Settings
MAX_FILE_SIZE=100000000  # 100MB in bytes
COMPRESSION_LEVEL=9
ENABLE_IPFS=true

# Security
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com
```

### LandGuard Environment Variables
Create `landguard/.env`:
```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/landguard
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# Security
SECRET_KEY=your_super_secret_key_here_change_this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Blockchain
BLOCKCHAIN_RPC_URL=https://rpc-amoy.polygon.technology
CONTRACT_ADDRESS=your_deployed_contract_address
PRIVATE_KEY=your_wallet_private_key

# IPFS
PINATA_API_KEY=your_pinata_api_key
PINATA_SECRET_KEY=your_pinata_secret_key

# API Settings
API_HOST=0.0.0.0
API_PORT=8001
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
```

### Blockchain Environment Variables
Create `landguard/Blockchain/.env`:
```bash
PRIVATE_KEY=your_wallet_private_key_without_0x_prefix
POLYGON_AMOY_RPC_URL=https://rpc-amoy.polygon.technology
POLYGONSCAN_API_KEY=your_polygonscan_api_key_for_verification
```

---

## 🔍 Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Find process using port
lsof -i :8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows

# Kill process
kill -9 <PID>  # Linux/Mac
taskkill /PID <PID> /F  # Windows
```

#### Database Connection Failed
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Restart PostgreSQL
sudo systemctl restart postgresql

# Verify connection
psql -U postgres -h localhost -d landguard
```

#### IPFS Upload Failed
- Verify Pinata API keys are correct
- Check internet connection
- Verify file size is within limits
- Check Pinata account quota

#### Smart Contract Deployment Failed
- Ensure sufficient MATIC balance
- Verify RPC URL is accessible
- Check private key format (no 0x prefix)
- Verify network ID matches Amoy (80002)

### Logs and Debugging

```bash
# View systemd service logs
sudo journalctl -u pcc -f
sudo journalctl -u landguard -f

# View nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Python debugging
# Add to your code:
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## 📊 Monitoring and Maintenance

### Health Checks

```bash
# Check PCC service
curl http://localhost:8000/health

# Check LandGuard service
curl http://localhost:8001/health

# Check database
psql -U postgres -c "SELECT version();"
```

### Automated Backups

```bash
# Database backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump landguard > /backups/landguard_$DATE.sql
find /backups -mtime +7 -delete  # Keep 7 days
```

### Updates

```bash
# Update application
cd /home/piedpiper/compression-
git pull origin main

# Update dependencies
cd pcc
source venv/bin/activate
pip install -r requirements.txt --upgrade
deactivate

cd ../landguard
source venv/bin/activate
pip install -r requirements.txt --upgrade
deactivate

# Restart services
sudo systemctl restart pcc landguard
```

---

## 🎯 Performance Optimization

### Nginx Optimization
```nginx
# Add to nginx.conf
worker_processes auto;
worker_connections 1024;

# Enable gzip compression
gzip on;
gzip_vary on;
gzip_types text/plain text/css application/json application/javascript;
```

### Database Optimization
```sql
-- Create indexes
CREATE INDEX idx_files_created_at ON files(created_at);
CREATE INDEX idx_users_email ON users(email);

-- Regular vacuum
VACUUM ANALYZE;
```

### Application Optimization
```bash
# Use more workers for gunicorn
# Recommended: (2 x CPU cores) + 1
gunicorn -w 9 -k uvicorn.workers.UvicornWorker app:app
```

---

## 📞 Support

For deployment issues:
1. Check [Troubleshooting](#troubleshooting) section
2. Review logs for error messages
3. Check GitHub Issues
4. Contact: support@piedpiper.com

---

## 🎉 Deployment Checklist

- [ ] Python 3.8+ installed
- [ ] Node.js 16+ installed (for blockchain)
- [ ] Virtual environments created
- [ ] Dependencies installed
- [ ] Environment variables configured
- [ ] Database set up and migrated
- [ ] IPFS/Pinata account configured
- [ ] Blockchain wallet funded (if using blockchain)
- [ ] Services running
- [ ] Nginx configured (production)
- [ ] SSL certificate installed (production)
- [ ] Firewall configured
- [ ] Monitoring set up
- [ ] Backups configured
- [ ] Documentation reviewed

---

**Deployment Status**: Ready for Production ✅

Last Updated: January 2, 2026
