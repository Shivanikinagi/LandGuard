# 🚀 Quick Deployment Guide

Choose your deployment method:

## 🎯 Quick Options

### 1. Automated Setup (Recommended for Beginners)
**Windows:**
```powershell
.\setup.ps1
```

**Linux/Mac:**
```bash
chmod +x setup.sh
./setup.sh
```

### 2. Docker (Recommended for Production)
```bash
# Copy environment template
cp .env.example .env
# Edit .env with your credentials

# Start all services
docker-compose up -d

# Check status
docker-compose ps
```

### 3. Manual Setup
See [DEPLOYMENT.md](DEPLOYMENT.md) for complete instructions.

---

## 📁 Essential Configuration Files

Before deploying, configure these files:

1. **Root Level**
   - `.env` - Main environment variables (copy from `.env.example`)

2. **LandGuard Service**
   - `landguard/.env` - Backend configuration (copy from `landguard/.env.example`)

3. **PCC Service**
   - `pcc/.env` - Compression core configuration (copy from `pcc/.env.example`)

4. **Blockchain (Optional)**
   - `landguard/Blockchain/.env` - Smart contract deployment (copy from `landguard/Blockchain/.env.example`)

---

## 🔑 Required API Keys

Get these before deployment:

1. **Pinata (Required for IPFS)**
   - Sign up: https://pinata.cloud/
   - Get: `PINATA_API_KEY`, `PINATA_SECRET_KEY`, `PINATA_JWT`

2. **PolygonScan (Optional, for blockchain)**
   - Sign up: https://polygonscan.com/
   - Get: `POLYGONSCAN_API_KEY`

3. **Polygon Faucet (Optional, for testnet)**
   - Get test MATIC: https://faucet.polygon.technology/

---

## ⚡ Quick Start Commands

### Start Services
```bash
# Using setup script
.\start.ps1          # Windows
./start.sh           # Linux/Mac

# Using Docker
docker-compose up -d
```

### Stop Services
```bash
# Using setup script
.\stop.ps1           # Windows
./stop.sh            # Linux/Mac

# Using Docker
docker-compose down
```

### Check Status
```bash
# PCC (Compression)
curl http://localhost:8000/health

# LandGuard (Backend)
curl http://localhost:8001/health
```

---

## 📚 Full Documentation

- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Complete deployment guide for all platforms
- **[BLOCKCHAIN_DEPLOYMENT.md](BLOCKCHAIN_DEPLOYMENT.md)** - Smart contract deployment guide
- **[README.md](README.md)** - Project overview and usage instructions

---

## 🆘 Common Issues

### Issue: Port already in use
```bash
# Find and kill process on port 8000
netstat -ano | findstr :8000    # Windows
lsof -i :8000                   # Linux/Mac
```

### Issue: Module not found
```bash
# Activate virtual environment first
.\venv\Scripts\Activate.ps1     # Windows
source venv/bin/activate        # Linux/Mac

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: Database connection failed
```bash
# Check PostgreSQL is running
# Install if needed: https://www.postgresql.org/download/

# Create database
psql -U postgres
CREATE DATABASE landguard;
```

---

## ✅ Deployment Checklist

- [ ] Python 3.8+ installed
- [ ] Node.js 16+ installed (for blockchain features)
- [ ] API keys obtained (Pinata, etc.)
- [ ] `.env` files configured
- [ ] Dependencies installed
- [ ] Services started successfully
- [ ] Health checks passing
- [ ] Test compression working

---

## 🎉 Next Steps

After deployment:

1. **Test the system**
   ```bash
   cd pcc
   python main.py pack test.txt --password test123
   ```

2. **Access the APIs**
   - PCC: http://localhost:8000
   - LandGuard: http://localhost:8001

3. **Deploy blockchain** (optional)
   ```bash
   cd landguard/Blockchain
   npm run deploy:amoy
   ```

4. **Set up monitoring** (production)
   - See DEPLOYMENT.md for monitoring setup

---

**Need help?** Check the full [DEPLOYMENT.md](DEPLOYMENT.md) guide.
