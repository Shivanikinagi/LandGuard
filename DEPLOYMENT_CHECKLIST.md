# 📋 Deployment Checklist

Print this checklist and check off items as you complete them.

---

## Pre-Deployment Setup

### Prerequisites Installation
- [ ] Python 3.8+ installed and verified (`python --version`)
- [ ] Node.js 16+ installed (for blockchain features) (`node --version`)
- [ ] Git installed (`git --version`)
- [ ] PostgreSQL installed (for production)
- [ ] Docker installed (if using Docker deployment)

### Account Creation
- [ ] Pinata account created (https://pinata.cloud/)
- [ ] Pinata API keys obtained:
  - [ ] PINATA_API_KEY
  - [ ] PINATA_SECRET_KEY
  - [ ] PINATA_JWT
- [ ] PolygonScan account (optional, for blockchain)
- [ ] PolygonScan API key obtained (optional)
- [ ] Polygon wallet created (optional, for blockchain)
- [ ] Test MATIC obtained from faucet (optional)

---

## Configuration

### Environment Files
- [ ] Copied `.env.example` to `.env` in root directory
- [ ] Copied `pcc/.env.example` to `pcc/.env`
- [ ] Copied `landguard/.env.example` to `landguard/.env`
- [ ] Copied `landguard/Blockchain/.env.example` to `landguard/Blockchain/.env` (if using blockchain)

### Environment Variables Set
- [ ] PINATA_API_KEY configured in all necessary .env files
- [ ] PINATA_SECRET_KEY configured in all necessary .env files
- [ ] PINATA_JWT configured in all necessary .env files
- [ ] DATABASE_URL configured (if using database)
- [ ] SECRET_KEY generated and configured
- [ ] CORS_ORIGINS configured for your domain
- [ ] BLOCKCHAIN_RPC_URL configured (if using blockchain)
- [ ] CONTRACT_ADDRESS configured (after deployment, if using blockchain)
- [ ] PRIVATE_KEY configured (if using blockchain) ⚠️ KEEP SECRET!

---

## Local Development Setup

### Automated Setup
- [ ] Ran `setup.ps1` (Windows) or `setup.sh` (Linux/Mac)
- [ ] Setup completed without errors
- [ ] Virtual environments created successfully

### Manual Verification
- [ ] PCC virtual environment activated
- [ ] PCC dependencies installed (`pip list` shows all packages)
- [ ] LandGuard virtual environment activated
- [ ] LandGuard dependencies installed
- [ ] Blockchain dependencies installed (if using blockchain)

### Service Testing
- [ ] Started PCC service
- [ ] PCC accessible at http://localhost:8000
- [ ] PCC health check passes (`curl http://localhost:8000/health`)
- [ ] Started LandGuard service
- [ ] LandGuard accessible at http://localhost:8001
- [ ] LandGuard health check passes (`curl http://localhost:8001/health`)

---

## Docker Deployment

### Docker Setup
- [ ] Docker installed and running
- [ ] docker-compose installed
- [ ] `.env` file configured in root directory
- [ ] Docker images built successfully

### Docker Services
- [ ] Ran `docker-compose up -d`
- [ ] All containers started successfully (`docker-compose ps`)
- [ ] PostgreSQL container healthy
- [ ] PCC container healthy
- [ ] LandGuard container healthy
- [ ] Nginx container healthy
- [ ] Can access services through nginx

### Docker Verification
- [ ] Services accessible through proxy
- [ ] Health checks passing in all containers
- [ ] Logs show no errors (`docker-compose logs`)
- [ ] Volumes created and persisting data

---

## Production Server Setup

### Server Preparation
- [ ] Ubuntu/Debian server provisioned
- [ ] SSH access configured
- [ ] Firewall configured:
  - [ ] Port 22 (SSH) - limited to your IP
  - [ ] Port 80 (HTTP)
  - [ ] Port 443 (HTTPS)
  - [ ] Port 5432 (PostgreSQL) - internal only
- [ ] System updated (`sudo apt update && sudo apt upgrade`)

### Software Installation
- [ ] Python 3.11 installed
- [ ] PostgreSQL installed and running
- [ ] Nginx installed
- [ ] Node.js installed (if using blockchain)
- [ ] Application user created (`piedpiper`)

### Application Deployment
- [ ] Repository cloned to server
- [ ] Virtual environments created
- [ ] Dependencies installed
- [ ] Environment files configured
- [ ] PostgreSQL database created
- [ ] Database migrations run (if applicable)

### Systemd Services
- [ ] PCC systemd service created (`/etc/systemd/system/pcc.service`)
- [ ] LandGuard systemd service created (`/etc/systemd/system/landguard.service`)
- [ ] Services enabled (`systemctl enable`)
- [ ] Services started (`systemctl start`)
- [ ] Services running without errors (`systemctl status`)

### Nginx Configuration
- [ ] Nginx config created (`/etc/nginx/sites-available/piedpiper`)
- [ ] Config symlinked to sites-enabled
- [ ] Nginx config tested (`nginx -t`)
- [ ] Nginx reloaded
- [ ] Application accessible through Nginx

### SSL Certificate
- [ ] Certbot installed
- [ ] SSL certificate obtained
- [ ] HTTPS working
- [ ] HTTP redirects to HTTPS
- [ ] Auto-renewal configured

---

## Blockchain Deployment

### Wallet Setup
- [ ] Wallet created or imported
- [ ] Private key secured (NEVER commit to git!)
- [ ] Wallet funded with test MATIC (testnet)
- [ ] Balance verified (`npm run balance`)

### Smart Contract Deployment
- [ ] Hardhat dependencies installed
- [ ] Blockchain .env configured
- [ ] Contract compiled successfully
- [ ] Contract deployed to Amoy testnet
- [ ] Contract address saved
- [ ] Deployment transaction confirmed
- [ ] Contract verified on PolygonScan (optional)

### Contract Integration
- [ ] Contract address added to LandGuard .env
- [ ] Contract ABI available
- [ ] Test transaction successful
- [ ] Contract functions working

---

## Testing & Validation

### Functional Testing
- [ ] Compressed test file successfully
- [ ] File uploaded to IPFS
- [ ] IPFS link accessible
- [ ] File decompressed successfully
- [ ] Decrypted content matches original
- [ ] Database operations working (if applicable)
- [ ] API endpoints responding correctly

### Performance Testing
- [ ] Tested with various file sizes
- [ ] Tested with different file types
- [ ] Compression ratios acceptable
- [ ] Processing times reasonable
- [ ] Memory usage acceptable
- [ ] No memory leaks detected

### Security Testing
- [ ] HTTPS enabled (production)
- [ ] Passwords not in logs
- [ ] Environment variables not exposed
- [ ] API rate limiting working
- [ ] Input validation working
- [ ] Private keys secured
- [ ] Firewall rules correct

---

## Monitoring & Maintenance

### Logging
- [ ] Log directory created
- [ ] Log rotation configured
- [ ] Error logs accessible
- [ ] Log levels appropriate

### Backups
- [ ] Database backup script created
- [ ] Backup schedule configured
- [ ] Test restore performed
- [ ] Backup retention policy set

### Monitoring
- [ ] Health check endpoints verified
- [ ] Uptime monitoring configured (optional)
- [ ] Error alerting set up (optional)
- [ ] Resource monitoring active (optional)

---

## Documentation

### Team Documentation
- [ ] Deployment process documented
- [ ] Environment variables documented
- [ ] API endpoints documented
- [ ] Troubleshooting guide created

### Access & Credentials
- [ ] Server access credentials saved securely
- [ ] Database credentials saved securely
- [ ] API keys saved securely (password manager)
- [ ] Wallet private key backed up securely
- [ ] Team has access to necessary credentials

---

## Final Verification

### Smoke Tests
- [ ] Homepage loads (if applicable)
- [ ] Can create new user/account
- [ ] Can upload and compress file
- [ ] Can download and decompress file
- [ ] IPFS links working
- [ ] Blockchain transactions working (if applicable)

### Load Testing (Optional)
- [ ] Tested with expected concurrent users
- [ ] Response times acceptable under load
- [ ] No crashes under load
- [ ] Auto-scaling working (if configured)

---

## Go-Live

### Pre-Launch
- [ ] All tests passing
- [ ] Team briefed on deployment
- [ ] Rollback plan prepared
- [ ] Support plan ready
- [ ] Monitoring dashboard ready

### Launch
- [ ] DNS updated (if applicable)
- [ ] SSL certificate verified
- [ ] All services started
- [ ] Health checks green
- [ ] Monitoring confirmed active

### Post-Launch
- [ ] Monitor error rates
- [ ] Check performance metrics
- [ ] Verify user feedback
- [ ] Document any issues
- [ ] Celebrate! 🎉

---

## Notes Section

Use this space for deployment-specific notes, server IPs, or other important information:

```
Server IP: ________________________________

Domain: ___________________________________

Database Host: ____________________________

Contract Address: _________________________

Deployment Date: __________________________

Deployed By: ______________________________

Notes:
_________________________________________
_________________________________________
_________________________________________
_________________________________________
_________________________________________
```

---

**Checklist Version:** 2.0  
**Last Updated:** January 2, 2026

Keep this checklist for future deployments and updates!
