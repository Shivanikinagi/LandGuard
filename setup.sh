#!/bin/bash

# Pied Piper 2.0 - Automated Setup Script for Linux/Mac
# This script sets up the entire project for local development

set -e  # Exit on error

echo "🚀 Pied Piper 2.0 - Automated Setup"
echo "=================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo "📋 Checking prerequisites..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed. Please install Python 3.8 or higher.${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d" " -f2 | cut -d"." -f1,2)
echo -e "${GREEN}✅ Python $PYTHON_VERSION found${NC}"

# Check if we're in the right directory
if [ ! -f "README.md" ]; then
    echo -e "${RED}❌ Please run this script from the project root directory${NC}"
    exit 1
fi

# Create base directory structure
echo ""
echo "📁 Setting up directory structure..."
mkdir -p data logs backups

# Setup PCC (Compression Core)
echo ""
echo "🔧 Setting up PCC (Compression Core)..."
cd pcc

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
else
    echo "Virtual environment already exists"
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo -e "${GREEN}✅ PCC setup complete${NC}"
deactivate

cd ..

# Setup LandGuard (Backend API)
echo ""
echo "🔧 Setting up LandGuard (Backend API)..."
cd landguard

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
else
    echo "Virtual environment already exists"
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cat > .env << 'EOF'
# Database Configuration
DATABASE_URL=postgresql://piedpiper:changeme@localhost:5432/landguard
DATABASE_POOL_SIZE=20

# Security
SECRET_KEY=change_this_to_a_random_secret_key_in_production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Blockchain (Optional - configure if using blockchain features)
BLOCKCHAIN_RPC_URL=https://rpc-amoy.polygon.technology
CONTRACT_ADDRESS=
PRIVATE_KEY=

# IPFS/Pinata
PINATA_API_KEY=your_pinata_api_key
PINATA_SECRET_KEY=your_pinata_secret_key

# API Settings
API_HOST=0.0.0.0
API_PORT=8001
CORS_ORIGINS=http://localhost:3000
EOF
    echo -e "${YELLOW}⚠️  Please edit landguard/.env with your actual credentials${NC}"
else
    echo ".env file already exists"
fi

echo -e "${GREEN}✅ LandGuard setup complete${NC}"
deactivate

cd ..

# Setup Blockchain (Optional)
echo ""
read -p "Do you want to set up Blockchain features? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🔧 Setting up Blockchain..."
    cd landguard/Blockchain
    
    if ! command -v node &> /dev/null; then
        echo -e "${YELLOW}⚠️  Node.js is not installed. Skipping Blockchain setup.${NC}"
        echo "Please install Node.js 16+ to use blockchain features."
    else
        NODE_VERSION=$(node --version)
        echo -e "${GREEN}✅ Node.js $NODE_VERSION found${NC}"
        
        echo "Installing Node.js dependencies..."
        npm install
        
        # Create .env if it doesn't exist
        if [ ! -f ".env" ]; then
            echo "Creating blockchain .env file..."
            cat > .env << 'EOF'
PRIVATE_KEY=your_wallet_private_key_without_0x_prefix
POLYGON_AMOY_RPC_URL=https://rpc-amoy.polygon.technology
POLYGONSCAN_API_KEY=your_polygonscan_api_key
EOF
            echo -e "${YELLOW}⚠️  Please edit landguard/Blockchain/.env with your wallet details${NC}"
        else
            echo "Blockchain .env file already exists"
        fi
        
        echo -e "${GREEN}✅ Blockchain setup complete${NC}"
    fi
    
    cd ../..
fi

# Create a helper script for starting services
echo ""
echo "📝 Creating helper scripts..."

cat > start.sh << 'EOF'
#!/bin/bash
# Start Pied Piper services

echo "🚀 Starting Pied Piper 2.0..."

# Start PCC in background
echo "Starting PCC service..."
cd pcc
source venv/bin/activate
python -m uvicorn app:app --host 0.0.0.0 --port 8000 &
PCC_PID=$!
echo "PCC running on http://localhost:8000 (PID: $PCC_PID)"
deactivate
cd ..

# Start LandGuard in background
echo "Starting LandGuard service..."
cd landguard
source venv/bin/activate
python -m uvicorn app:app --host 0.0.0.0 --port 8001 &
LANDGUARD_PID=$!
echo "LandGuard running on http://localhost:8001 (PID: $LANDGUARD_PID)"
deactivate
cd ..

echo ""
echo "✅ Services started!"
echo "PCC: http://localhost:8000"
echo "LandGuard: http://localhost:8001"
echo ""
echo "To stop services, run: ./stop.sh"
echo "To view logs, use: journalctl or check terminal output"

# Save PIDs for cleanup
echo $PCC_PID > .pcc.pid
echo $LANDGUARD_PID > .landguard.pid
EOF

cat > stop.sh << 'EOF'
#!/bin/bash
# Stop Pied Piper services

echo "🛑 Stopping Pied Piper 2.0..."

if [ -f .pcc.pid ]; then
    PCC_PID=$(cat .pcc.pid)
    if kill -0 $PCC_PID 2>/dev/null; then
        kill $PCC_PID
        echo "✅ PCC stopped (PID: $PCC_PID)"
    fi
    rm .pcc.pid
fi

if [ -f .landguard.pid ]; then
    LANDGUARD_PID=$(cat .landguard.pid)
    if kill -0 $LANDGUARD_PID 2>/dev/null; then
        kill $LANDGUARD_PID
        echo "✅ LandGuard stopped (PID: $LANDGUARD_PID)"
    fi
    rm .landguard.pid
fi

echo "All services stopped"
EOF

chmod +x start.sh stop.sh

# Final summary
echo ""
echo "=================================="
echo -e "${GREEN}✅ Setup Complete!${NC}"
echo "=================================="
echo ""
echo "📝 Next Steps:"
echo ""
echo "1. Configure your environment:"
echo "   - Edit landguard/.env with your credentials"
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "   - Edit landguard/Blockchain/.env with your wallet details"
fi
echo ""
echo "2. Get required API keys:"
echo "   - Pinata IPFS: https://pinata.cloud/"
echo "   - Polygon Amoy: https://faucet.polygon.technology/"
echo ""
echo "3. Start the services:"
echo "   ./start.sh"
echo ""
echo "4. Test the installation:"
echo "   cd pcc"
echo "   source venv/bin/activate"
echo "   python -c 'from compressors import Compressor; print(\"Working!\")'"
echo ""
echo "5. Read the deployment guide:"
echo "   cat DEPLOYMENT.md"
echo ""
echo "🎉 Happy coding!"
