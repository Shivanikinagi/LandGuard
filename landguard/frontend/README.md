# 🏛️ LandGuard Frontend

AI-Powered Land Fraud Detection System - React Dashboard

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
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

## 🛠️ Tech Stack

- **Framework:** React 18.2.0
- **Build Tool:** Vite 5.0.8
- **UI Library:** Material-UI (MUI) 5.14.20
- **Routing:** React Router DOM 6.20.1
- **Charts:** Recharts 2.10.3
- **HTTP Client:** Axios 1.6.2
- **State Management:** React Hooks
- **Date Handling:** date-fns 2.30.0
- **File Upload:** react-dropzone 14.2.3
- **Notifications:** react-toastify 9.1.3

## 📦 Prerequisites

Before you begin, ensure you have the following installed:

- **Node.js** >= 18.0.0 (LTS recommended)
- **npm** >= 9.0.0 or **yarn** >= 1.22.0
- **Git** (for version control)

### Verify Installation

```bash
node --version  # Should show v18.x.x or higher
npm --version   # Should show 9.x.x or higher
```

## 🚀 Installation

### Step 1: Clone the Repository

```bash
# Clone the main project
git clone https://github.com/yourusername/landguard.git
cd landguard/frontend
```

### Step 2: Install Dependencies

```bash
# Using npm
npm install

# OR using yarn
yarn install
```

**Running Codacy security analysis on dependencies:**

```javascript
codacy_cli_analyze({
  rootPath: "f:\\shivani\\VSCode\\projects\\compression\\compression-\\landguard\\frontend",
  tool: "trivy"
})
```

### Step 3: Create Environment File

```bash
# Copy the example environment file
cp .env.example .env.local

# Edit the file with your configuration
nano .env.local
```

## ⚙️ Configuration

### Environment Variables

Create a `.env.local` file in the root directory:

```env
# API Configuration
VITE_API_BASE_URL=http://localhost:8000/api
VITE_API_TIMEOUT=30000

# Application Settings
VITE_APP_NAME=LandGuard
VITE_APP_VERSION=1.0.0

# Features
VITE_ENABLE_MONGODB=false
VITE_MAX_UPLOAD_SIZE=10485760
```

### Configuration Options

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_BASE_URL` | Backend API base URL | `http://localhost:8000/api` |
| `VITE_API_TIMEOUT` | API request timeout (ms) | `30000` |
| `VITE_APP_NAME` | Application name | `LandGuard` |
| `VITE_MAX_UPLOAD_SIZE` | Max file upload size (bytes) | `10485760` (10MB) |

## 🏃 Running the Application

### Development Mode

```bash
# Start development server
npm run dev

# OR with yarn
yarn dev
```

The application will be available at: **http://localhost:3000**

### Production Build

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

### Production Mode

```bash
# Build the application
npm run build

# Serve the built files
npm run preview
```

## 📁 Project Structure

```
frontend/
├── public/                 # Static files
├── src/
│   ├── components/        # React components
│   │   ├── Dashboard.jsx
│   │   ├── Login.jsx
│   │   ├── Navbar.jsx
│   │   ├── Sidebar.jsx
│   │   ├── LandRecordList.jsx
│   │   ├── LandRecordDetail.jsx
│   │   ├── AnalysisView.jsx
│   │   ├── BulkUpload.jsx
│   │   ├── ReportCenter.jsx
│   │   ├── UserManagement.jsx
│   │   ├── StatsCard.jsx
│   │   └── RiskChart.jsx
│   ├── services/          # API services
│   │   ├── api.js
│   │   ├── auth.js
│   │   ├── landRecords.js
│   │   └── analysis.js
│   ├── hooks/             # Custom React hooks
│   │   └── useAuth.js
│   ├── utils/             # Utility functions
│   │   ├── constants.js
│   │   ├── formatters.js
│   │   └── validators.js
│   ├── styles/            # Global styles
│   │   ├── index.css
│   │   └── App.css
│   ├── App.jsx            # Main App component
│   └── main.jsx           # Entry point
├── .env.example           # Environment variables template
├── .gitignore
├── index.html
├── package.json
├── vite.config.js
└── README.md
```

## 📜 Available Scripts

### Development

```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run preview      # Preview production build
npm run lint         # Run ESLint
```

### Testing

```bash
# Run unit tests (when configured)
npm run test

# Run tests with coverage
npm run test:coverage
```

## 🌐 API Integration

### Backend Requirements

The frontend requires the LandGuard backend API to be running. Ensure the backend is started before running the frontend.

```bash
# In a separate terminal, start the backend
cd ../backend
uvicorn main:app --reload --port 8000
```

### API Endpoints Used

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/login` | POST | User authentication |
| `/api/land-records` | GET | Fetch land records |
| `/api/land-records/:id` | GET | Get record details |
| `/api/analysis` | GET | Fetch analysis results |
| `/api/analysis/land/:id` | POST | Analyze land record |
| `/api/reports` | GET | Fetch reports |
| `/api/users` | GET | Fetch users (Admin only) |

### Authentication

The application uses JWT tokens for authentication:

1. Login with credentials
2. Token is stored in `localStorage`
3. Token is sent in `Authorization` header for all API requests
4. Token expires after 24 hours (configurable in backend)

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

### Vercel Deployment

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

### Netlify Deployment

```bash
# Build the project
npm run build

# Deploy the dist folder to Netlify
```

### Docker Deployment

```bash
# Build Docker image
docker build -t landguard-frontend .

# Run container
docker run -p 3000:80 landguard-frontend
```

### Environment Variables for Production

Update `.env.production`:

```env
VITE_API_BASE_URL=https://api.yourdomain.com/api
VITE_APP_NAME=LandGuard
```

## 🔧 Troubleshooting

### Common Issues

#### Issue: Cannot connect to backend

**Solution:**
```bash
# Check if backend is running
curl http://localhost:8000/api/health

# Update VITE_API_BASE_URL in .env.local
VITE_API_BASE_URL=http://localhost:8000/api
```

#### Issue: CORS errors

**Solution:**
Ensure backend CORS settings allow frontend origin:

```python
# In backend main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### Issue: Module not found errors

**Solution:**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

#### Issue: Port 3000 already in use

**Solution:**
```bash
# Use different port
npm run dev -- --port 3001

# OR kill process using port 3000
# Windows
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:3000 | xargs kill -9
```

### Debugging

Enable verbose logging:

```bash
# Set DEBUG environment variable
DEBUG=* npm run dev
```

Check browser console for errors:
1. Open DevTools (F12)
2. Go to Console tab
3. Look for error messages

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Code Style

- Use ESLint for code linting
- Follow React best practices
- Write meaningful commit messages
- Add comments for complex logic

### Before Submitting PR

```bash
# Run linting
npm run lint

# Build to check for errors
npm run build

# Test your changes
npm run test
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Your Name** - *Initial work* - [YourGitHub](https://github.com/yourusername)

## 🙏 Acknowledgments

- Material-UI for the component library
- Recharts for data visualization
- React community for excellent documentation
- FastAPI team for the backend framework

## 📞 Support

For support, email support@landguard.com or open an issue on GitHub.

## 🔗 Links

- [Backend Repository](https://github.com/yourusername/landguard-backend)
- [Documentation](https://landguard.com/docs)
- [Live Demo](https://landguard.com)
- [API Documentation](https://api.landguard.com/docs)

---

**Made with ❤️ by the LandGuard Team**