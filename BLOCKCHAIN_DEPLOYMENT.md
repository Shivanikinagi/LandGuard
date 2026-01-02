# 🔗 Blockchain Smart Contract Deployment Guide

Complete guide for deploying LandGuard smart contracts to Polygon networks.

---

## 📋 Prerequisites

### Required Software
- **Node.js 16+** ([Download](https://nodejs.org/))
- **npm** (comes with Node.js)
- **Metamask** or compatible Web3 wallet ([Download](https://metamask.io/))

### Required Accounts
- **Polygon Wallet** with some MATIC tokens
- **PolygonScan API Key** (for contract verification)
- **Alchemy** or **Infura** account (optional, for better RPC reliability)

---

## 🚀 Quick Start

### Step 1: Navigate to Blockchain Directory
```bash
cd landguard/Blockchain
```

### Step 2: Install Dependencies
```bash
npm install
```

### Step 3: Configure Environment
```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your details
notepad .env  # Windows
nano .env     # Linux/Mac
```

### Step 4: Get Test MATIC (Testnet Only)
Visit [Polygon Faucet](https://faucet.polygon.technology/)
- Select "Amoy" network
- Enter your wallet address
- Request test MATIC

### Step 5: Check Balance
```bash
npm run balance
```

### Step 6: Deploy Contract
```bash
# Deploy to Amoy Testnet
npm run deploy:amoy

# Save the contract address from output!
```

### Step 7: Verify Contract (Optional)
```bash
npx hardhat verify --network amoy <CONTRACT_ADDRESS>
```

---

## 🔐 Wallet Setup

### Creating a New Wallet

#### Using Hardhat
```bash
npm run generate-wallet
```

This will generate:
- Private key
- Public address
- Mnemonic phrase

**⚠️ IMPORTANT: Save these securely! Never share your private key!**

#### Using Metamask
1. Install Metamask browser extension
2. Create new wallet
3. Save recovery phrase securely
4. Export private key from Metamask
   - Click account icon → Account details → Export Private Key

### Funding Your Wallet

#### Testnet (Amoy)
Get free test MATIC from:
- [Polygon Faucet](https://faucet.polygon.technology/)
- [Alchemy Faucet](https://www.alchemy.com/faucets/polygon-amoy)
- [QuickNode Faucet](https://faucet.quicknode.com/polygon/amoy)

#### Mainnet (Production)
Purchase MATIC from exchanges:
- Binance
- Coinbase
- Kraken
- Uniswap

---

## ⚙️ Configuration

### Environment Variables

Edit `landguard/Blockchain/.env`:

```bash
# Your wallet private key (NO 0x prefix)
PRIVATE_KEY=abc123def456...

# RPC endpoint
POLYGON_AMOY_RPC_URL=https://rpc-amoy.polygon.technology

# API key for verification
POLYGONSCAN_API_KEY=YOUR_POLYGONSCAN_API_KEY
```

### Getting RPC URLs

#### Free RPC (Public)
```
Amoy Testnet: https://rpc-amoy.polygon.technology
Polygon Mainnet: https://polygon-rpc.com
```

#### Alchemy (Recommended)
1. Sign up at [Alchemy](https://www.alchemy.com/)
2. Create new app
3. Select "Polygon" network
4. Copy RPC URL

```
Format: https://polygon-amoy.g.alchemy.com/v2/YOUR_API_KEY
```

#### Infura
1. Sign up at [Infura](https://infura.io/)
2. Create new project
3. Select "Polygon" network
4. Copy endpoint

```
Format: https://polygon-amoy.infura.io/v3/YOUR_PROJECT_ID
```

### Getting PolygonScan API Key

1. Visit [PolygonScan](https://polygonscan.com/)
2. Sign up for account
3. Go to API Keys section
4. Generate new API key
5. Copy to `.env` file

---

## 📜 Available Commands

### Development Commands

```bash
# Install dependencies
npm install

# Compile contracts
npm run compile

# Run tests
npm run test

# Check account balance
npm run balance

# Generate new wallet
npm run generate-wallet
```

### Deployment Commands

```bash
# Deploy to Amoy Testnet
npm run deploy:amoy

# Deploy to Mainnet (use with caution!)
npm run deploy:mainnet

# Verify deployed contract
npm run verify
```

### Utility Commands

```bash
# Check deployment setup
npm run verify-setup

# Run example interactions
npm run example

# List available accounts
npm run accounts
```

---

## 🎯 Deployment Process

### Amoy Testnet Deployment

```bash
# 1. Ensure you're in the Blockchain directory
cd landguard/Blockchain

# 2. Check your balance
npm run balance
# Should show: Balance: X.XX MATIC

# 3. Deploy contract
npm run deploy:amoy
```

**Expected Output:**
```
🚀 Deploying LandGuard Smart Contract...
📍 Network: Polygon Amoy Testnet
💰 Deployer: 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb7
💵 Balance: 1.5 MATIC

⏳ Deploying contract...
✅ Contract deployed!
📝 Contract Address: 0x1234567890abcdef1234567890abcdef12345678
⛽ Gas Used: 1234567
💲 Deployment Cost: 0.012 MATIC

🔍 Verify on PolygonScan:
https://amoy.polygonscan.com/address/0x1234567890abcdef1234567890abcdef12345678
```

**Save the contract address!** You'll need it for:
- Updating `landguard/.env` → `CONTRACT_ADDRESS`
- Verifying the contract
- Interacting with the contract

### Contract Verification

Verification makes your contract code publicly viewable on PolygonScan.

```bash
# Verify contract
npx hardhat verify --network amoy 0xYOUR_CONTRACT_ADDRESS

# If you used constructor arguments:
npx hardhat verify --network amoy 0xYOUR_CONTRACT_ADDRESS "arg1" "arg2"
```

**Expected Output:**
```
Successfully submitted source code for contract
Contract successfully verified
```

---

## 🌐 Mainnet Deployment (Production)

### ⚠️ CRITICAL WARNINGS

1. **Use Real MATIC**: Mainnet deployment costs real money
2. **Test First**: Always test on Amoy testnet first
3. **Secure Keys**: Use hardware wallet or secure key management
4. **Double Check**: Verify all configurations before deploying
5. **Gas Costs**: Ensure sufficient MATIC for deployment (~$10-50)

### Pre-Deployment Checklist

- [ ] Contract tested on Amoy testnet
- [ ] All tests passing
- [ ] Security audit completed
- [ ] Sufficient MATIC in wallet
- [ ] Backup of private keys
- [ ] Mainnet RPC configured
- [ ] Team approval received

### Deployment Steps

```bash
# 1. Update .env for mainnet
POLYGON_MAINNET_RPC_URL=https://polygon-rpc.com
# Or use Alchemy/Infura mainnet URL

# 2. Create mainnet deployment script if needed
# Copy final-deploy.js and modify for mainnet

# 3. Deploy
npm run deploy:mainnet

# 4. IMMEDIATELY save contract address
# 5. Verify contract
npx hardhat verify --network mainnet <CONTRACT_ADDRESS>

# 6. Test contract interactions
npm run example

# 7. Update production environment
# Update landguard/.env with mainnet contract address
```

---

## 🔍 Troubleshooting

### Issue: "Insufficient funds for gas"

**Solution:**
```bash
# Check balance
npm run balance

# Get more MATIC
# Testnet: Use faucet
# Mainnet: Purchase MATIC
```

### Issue: "Network request failed"

**Solution:**
- Check internet connection
- Try different RPC URL
- Verify RPC URL in `.env`
- Use Alchemy or Infura instead of public RPC

### Issue: "Invalid private key"

**Solution:**
- Ensure no `0x` prefix in `.env`
- Check for extra spaces
- Verify key is 64 hex characters
- Export fresh key from Metamask

### Issue: "Contract verification failed"

**Solution:**
```bash
# Ensure correct compiler version in hardhat.config.js
# Match the Solidity version in your contract

# Try manual verification on PolygonScan
# Upload contract source code manually
```

### Issue: "Nonce too high"

**Solution:**
```bash
# Reset nonce in Metamask
# Settings → Advanced → Reset Account

# Or specify nonce manually in deployment script
```

### Issue: "Transaction underpriced"

**Solution:**
- Network congestion
- Increase gas price
- Wait and retry
- Use different RPC

---

## 📊 Monitoring & Management

### Checking Contract Status

```bash
# View on PolygonScan
# Testnet:
https://amoy.polygonscan.com/address/<CONTRACT_ADDRESS>

# Mainnet:
https://polygonscan.com/address/<CONTRACT_ADDRESS>
```

### Interacting with Contract

```javascript
// example.js
import { ethers } from 'ethers';
import dotenv from 'dotenv';

dotenv.config();

const provider = new ethers.JsonRpcProvider(process.env.POLYGON_AMOY_RPC_URL);
const wallet = new ethers.Wallet(process.env.PRIVATE_KEY, provider);

// Contract ABI and address
const contractAddress = '0xYOUR_CONTRACT_ADDRESS';
const abi = [...]; // Your contract ABI

const contract = new ethers.Contract(contractAddress, abi, wallet);

// Call contract functions
const result = await contract.someFunction();
console.log(result);
```

### Upgrading Contract

Smart contracts are immutable, but you can:

1. **Deploy New Version**
   ```bash
   npm run deploy:amoy
   # Save new address
   ```

2. **Migrate Data** (if needed)
   ```javascript
   // Migration script
   // Read from old contract
   // Write to new contract
   ```

3. **Update Application**
   ```bash
   # Update CONTRACT_ADDRESS in landguard/.env
   CONTRACT_ADDRESS=0xNEW_CONTRACT_ADDRESS
   ```

---

## 🔒 Security Best Practices

### Key Management

1. **Never Commit Private Keys**
   ```bash
   # Ensure .env is in .gitignore
   echo ".env" >> .gitignore
   ```

2. **Use Environment Variables**
   ```bash
   # Don't hardcode keys in code
   const privateKey = process.env.PRIVATE_KEY;
   ```

3. **Separate Keys by Environment**
   - Development: Separate test wallet
   - Staging: Different test wallet
   - Production: Hardware wallet or KMS

4. **Regular Key Rotation**
   - Change keys periodically
   - Use multi-sig for production
   - Implement key access logging

### Contract Security

1. **Audit Before Mainnet**
   - Professional security audit
   - Automated tools (Slither, Mythril)
   - Peer review

2. **Test Coverage**
   ```bash
   npm run test
   # Aim for 100% coverage
   ```

3. **Gradual Rollout**
   - Deploy to testnet
   - Limited mainnet release
   - Monitor for issues
   - Full production deployment

---

## 📈 Gas Optimization

### Estimate Gas Costs

```bash
# Before deployment
npx hardhat run scripts/estimate-gas.js
```

### Reduce Gas Costs

1. **Optimize Solidity Code**
   - Use `uint256` instead of smaller types
   - Pack storage variables
   - Remove unnecessary storage

2. **Batch Transactions**
   - Combine multiple operations
   - Use arrays instead of loops

3. **Choose Right Time**
   - Deploy when gas prices are low
   - Monitor: [Polygon Gas Tracker](https://polygonscan.com/gastracker)

---

## 📞 Support & Resources

### Official Documentation
- [Polygon Docs](https://docs.polygon.technology/)
- [Hardhat Docs](https://hardhat.org/docs)
- [Ethers.js Docs](https://docs.ethers.org/)

### Community
- [Polygon Discord](https://discord.gg/polygon)
- [Hardhat Discord](https://discord.gg/hardhat)
- [Ethereum Stack Exchange](https://ethereum.stackexchange.com/)

### Tools
- [Remix IDE](https://remix.ethereum.org/) - Online Solidity IDE
- [Tenderly](https://tenderly.co/) - Contract monitoring
- [OpenZeppelin](https://openzeppelin.com/) - Secure contracts

---

## ✅ Deployment Checklist

### Pre-Deployment
- [ ] Node.js installed
- [ ] Dependencies installed (`npm install`)
- [ ] Wallet created with private key
- [ ] Test MATIC acquired (testnet)
- [ ] `.env` file configured
- [ ] RPC URL working
- [ ] Balance checked
- [ ] Contracts compiled
- [ ] Tests passing

### During Deployment
- [ ] Correct network selected
- [ ] Sufficient gas available
- [ ] Deployment command executed
- [ ] Contract address saved
- [ ] Transaction hash recorded
- [ ] Deployment confirmed on PolygonScan

### Post-Deployment
- [ ] Contract verified on PolygonScan
- [ ] Contract address updated in app
- [ ] Test interactions successful
- [ ] Documentation updated
- [ ] Team notified
- [ ] Monitoring setup

---

**Last Updated:** January 2, 2026
**Status:** Production Ready ✅
