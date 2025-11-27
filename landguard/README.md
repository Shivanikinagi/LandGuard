# 🏛️ LandGuard

AI-Powered Land Fraud Detection System

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [CLI Tool](#cli-tool)
- [Project Structure](#project-structure)
- [Available Scripts](#available-scripts)
- [Environment Variables](#environment-variables)
- [API Integration](#api-integration)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## ✨ Features

- 📊 **Interactive Dashboard** - Real-time statistics and visualizations
- 🔍 **Land Record Management** - Search, view, and manage land records
- 🎯 **Fraud Analysis** - AI-powered fraud detection and risk assessment
- 📤 **Bulk Upload** - CSV/Excel file upload for batch processing
- 📑 **Report Generation** - Generate PDF/Excel reports
- 👥 **User Management** - Role-based access control (Admin, Analyst, Viewer)
- 🔐 **Secure Authentication** - JWT-based authentication
- 📱 **Responsive Design** - Works on desktop, tablet, and mobile
- 🛡️ **Document Security** - Compression, encryption, and blockchain verification
- 🌐 **Decentralized Storage** - IPFS integration for permanent document storage

## 🛠️ Tech Stack

- **Backend:** FastAPI, Python 3.9+
- **Database:** PostgreSQL with SQLAlchemy ORM
- **Frontend:** React 18.2.0, Vite 5.0.8, Material-UI 5.14.20
- **Authentication:** JWT, OAuth2
- **Storage:** IPFS (Pinata), PostgreSQL
- **Security:** bcrypt, JWT, AES-256 encryption
- **Blockchain:** Smart contracts (sandbox mode)
- **Compression:** PCC (Pied Piper Compression) integration

## 📦 Prerequisites

Before you begin, ensure you have the following installed:

- **Python** >= 3.9
- **Node.js** >= 18.0.0 (LTS recommended)
- **npm** >= 9.0.0 or **yarn** >= 1.22.0
- **PostgreSQL** >= 13.0
- **Git** (for version control)

### Verify Installation

```bash
python --version  # Should show Python 3.9.x or higher
node --version    # Should show v18.x.x or higher
npm --version     # Should show 9.x.x or higher
psql --version    # Should show PostgreSQL 13.x or higher
```

## 🚀 Installation

### Step 1: Clone the Repository

```bash
# Clone the main project
git clone https://github.com/yourusername/landguard.git
cd landguard
```

### Step 2: Backend Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows
venv\Scripts\activate
# On Linux/Mac
source venv/bin/activate

# Install backend dependencies
pip install -r requirements.txt
```

### Step 3: Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install frontend dependencies
npm install

# OR using yarn
yarn install

# Navigate back to root
cd ..
```

### Step 4: Database Setup

```bash
# Create database (adjust credentials as needed)
createdb landguard

# Run database migrations
python database/init_db.py
```

### Step 5: Environment Configuration

Create a `.env` file in the root directory:

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=landguard
DB_USER=your_username
DB_PASSWORD=your_password

# JWT Configuration
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Configuration
HOST=localhost
PORT=8000
DEBUG=True

# PCC Integration
PCC_PATH=../pcc

# IPFS Configuration (optional)
PINATA_JWT=your_pinata_jwt_token
```

## 🏃 Running the Application

### Backend Server

```bash
# Activate virtual environment
# On Windows
venv\Scripts\activate
# On Linux/Mac
source venv/bin/activate

# Start backend server
python api/main.py
```

The backend will be available at: **http://localhost:8000**

API Documentation: **http://localhost:8000/docs**

### Frontend Development Server

```bash
# Navigate to frontend directory
cd frontend

# Start development server
npm run dev

# OR with yarn
yarn dev
```

The frontend will be available at: **http://localhost:5173**

## 🛠 CLI Tool

LandGuard includes a command-line interface for processing documents directly from the terminal:

```bash
# Process documents
python cli/landguard_cli.py process documents/property_deed.pdf

# Verify documents
python cli/landguard_cli.py verify QmXyZ123AbC456DeF789GhI012JkLmNoPqRsTuVwXyZ123AbC4
```

See [CLI Documentation](cli/README.md) for more details.

## 📁 Project Structure

```
landguard/
├── api/                  # FastAPI backend
│   ├── main.py          # Application entry point
│   ├── routes/          # API route handlers
│   └── middleware.py    # Custom middleware
├── database/            # Database models and utilities
│   ├── models.py        # SQLAlchemy models
│   ├── connection.py    # Database connection
│   ├── auth.py          # Authentication utilities
│   └── init_db.py       # Database initialization
├── core/                # Core business logic
│   ├── landguard/       # LandGuard core modules
│   └── blockchain/      # Blockchain integration
├── Blockchain/          # Blockchain components
│   ├── blockchain/      # Smart contracts and handlers
│   └── smart_contracts/ # Smart contract implementations
├── cli/                 # Command-line interface
│   ├── landguard_cli.py # Main CLI implementation
│   └── README.md        # CLI documentation
├── frontend/            # React frontend
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── services/    # API services
│   │   └── hooks/       # Custom React hooks
│   └── public/          # Static files
├── uploads/             # Uploaded files (auto-created)
├── processed/           # Processed files (auto-created)
├── .env.example         # Environment variables template
├── requirements.txt     # Python dependencies
└── README.md            # This file
```

## 📜 Available Scripts

### Backend

```bash
# Run backend server
python api/main.py

# Run with auto-reload (development)
python api/main.py --debug

# Run tests
python -m pytest tests/

# Database migrations
python database/init_db.py
```

### Frontend

```bash
# Navigate to frontend directory
cd frontend

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run linting
npm run lint
```

## ⚙️ Environment Variables

### Backend

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_HOST` | Database host | `localhost` |
| `DB_PORT` | Database port | `5432` |
| `DB_NAME` | Database name | `landguard` |
| `DB_USER` | Database user | `postgres` |
| `DB_PASSWORD` | Database password | `postgres` |
| `SECRET_KEY` | JWT secret key | `your-secret-key-change-in-production` |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration | `30` |
| `HOST` | Server host | `localhost` |
| `PORT` | Server port | `8000` |
| `DEBUG` | Debug mode | `True` |

### Frontend

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_BASE_URL` | Backend API base URL | `http://localhost:8000/api` |
| `VITE_API_TIMEOUT` | API request timeout (ms) | `30000` |
| `VITE_APP_NAME` | Application name | `LandGuard` |

## 🌐 API Integration

### Backend Requirements

The frontend requires the LandGuard backend API to be running. Ensure the backend is started before running the frontend.

```bash
# In a separate terminal, start the backend
python api/main.py
```

### API Endpoints Used

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/auth/login` | POST | User authentication |
| `/api/v1/land-records` | GET | Fetch land records |
| `/api/v1/land-records/:id` | GET | Get record details |
| `/api/v1/analysis` | GET | Fetch analysis results |
| `/api/v1/statistics/overview` | GET | Get dashboard statistics |
| `/api/v1/processing/process-document` | POST | Process documents through complete workflow |

### Authentication

The application uses JWT tokens for authentication:

1. Login with credentials
2. Token is stored in `localStorage`
3. Token is sent in `Authorization` header for all API requests
4. Token expires after 30 minutes (configurable)

### Demo Credentials

**Admin User:**
- Username: `admin`
- Password: `admin123`

**Analyst User:**
- Username: `analyst`
- Password: `analyst123`

**Viewer User:**
- Username: `viewer`
- Password: `viewer123`

## 🚀 Deployment

### Production Build

```bash
# Backend
python api/main.py --host 0.0.0.0 --port 8000 --debug False

# Frontend
cd frontend
npm run build
# Serve the dist folder with your preferred web server
```

### Docker Deployment (Optional)

```bash
# Build and run with Docker Compose
docker-compose up -d
```

### Environment Variables for Production

Update `.env` for production:

```env
SECRET_KEY=your-production-secret-key
DEBUG=False
HOST=0.0.0.0
```

## 🔧 Troubleshooting

### Common Issues

#### Issue: Cannot connect to backend

**Solution:**
```bash
# Check if backend is running
curl http://localhost:8000/api/v1/health

# Ensure correct API base URL in frontend .env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

#### Issue: CORS errors

**Solution:**
Ensure backend CORS settings allow frontend origin:

```python
# In backend main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### Issue: Database connection failed

**Solution:**
```bash
# Check PostgreSQL service
sudo systemctl status postgresql

# Verify database credentials in .env
# Try connecting manually
psql -h localhost -p 5432 -U your_username -d landguard
```

#### Issue: Module not found errors

**Solution:**
```bash
# Clear cache and reinstall
pip install --no-cache-dir -r requirements.txt
```

### Debugging

Enable verbose logging:

```bash
# Set DEBUG environment variable
DEBUG=True python api/main.py
```

Check logs for errors:
1. Backend logs in terminal
2. Browser console (F12 → Console tab)

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Code Style

- Follow PEP 8 for Python code
- Use ESLint for frontend code
- Write meaningful commit messages
- Add comments for complex logic

### Before Submitting PR

```bash
# Run backend tests
python -m pytest tests/

# Run frontend linting
cd frontend && npm run lint

# Build to check for errors
npm run build
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Your Name** - *Initial work* - [YourGitHub](https://github.com/yourusername)

## 🙏 Acknowledgments

- FastAPI team for the excellent backend framework
- React community for the frontend library
- Material-UI for the component library
- PostgreSQL team for the database
- All contributors and open-source projects used

## 📞 Support

For support, email support@landguard.com or open an issue on GitHub.

## 🔗 Links

- [Documentation](https://landguard.com/docs)
- [Live Demo](https://landguard.com)
- [API Documentation](https://api.landguard.com/docs)

---
**Built with ❤️ by the LandGuard Team**