# LandGuard & PCC Complete Setup Guide

This guide will help you set up and run the complete LandGuard & PCC system with both backend and frontend components.

## System Architecture

The LandGuard & PCC system consists of three main components:

1. **Backend Services** (`pcc/` and `landguard/` directories)
   - Core Python modules for document processing
   - CLI interfaces for direct command-line usage

2. **API Layer** (`api/` directory)
   - REST API that exposes backend functionality to web clients
   - Built with Flask for easy integration

3. **Frontend Interface** (`frontend/` directory)
   - React web application with interactive UI
   - Communicates with API layer for all operations

## Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn
- Virtual environment tool (venv or conda)

## Installation Steps

### 1. Backend Setup

Navigate to the project root directory:

```bash
cd f:\shivani\VSCode\projects\compression\compression-
```

Create and activate a virtual environment:

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

Install backend dependencies:

```bash
# Install PCC dependencies
pip install -r pcc/requirements.txt

# Install LandGuard dependencies
pip install -r landguard/requirements.txt
```

Test the backend CLI:

```bash
# Test PCC compression
cd pcc
python main.py --help

# Test LandGuard processing
cd ../landguard
python cli/landguard_cli.py --help
```

### 2. API Setup

Navigate to the project root directory and create a dedicated virtual environment for the API:

```bash
# Create a new virtual environment for the API
python -m venv api_env

# Activate the virtual environment
# On Windows:
api_env\Scripts\activate

# On macOS/Linux:
# source api_env/bin/activate
```

Navigate to the API directory and install API dependencies:

```bash
cd api
pip install -r requirements.txt

# Install additional dependencies needed for PCC and LandGuard integration
pip install cbor2 cryptography requests rich typer
```

Start the API server:

```bash
python server.py
```

The API server will start on `http://localhost:5000`. You can verify it's working by visiting:

```bash
curl http://localhost:5000
```

You should see a JSON response indicating the server is running.
### 3. Frontend Setup

Open a new terminal window/tab (keep the API server running) and navigate to the frontend directory:

```bash
cd f:\shivani\VSCode\projects\compression\compression-\frontend
```

Install frontend dependencies:

```bash
npm install
```

Start the frontend development server:

```bash
npm run dev
```

The frontend will start on `http://localhost:5175` (or the next available port).

## Usage Instructions

### Using the Complete System

1. **Access the Web Interface**
   - Open your browser and navigate to `http://localhost:5175`
   - You'll see the LandGuard & PCC web interface

2. **Process Documents**
   - Click "Choose File" to select a document
   - Optionally enter a password for encryption
   - Click "Compress File" to compress the document with PCC
   - Click "Process with LandGuard" to run the full fraud detection workflow

3. **Using the CLI Directly**
   - You can still use the command-line interfaces:
   ```bash
   # PCC compression
   cd pcc
   python main.py pack test.txt --password mySecurePassword123
   
   # LandGuard processing
   cd ../landguard
   python cli/landguard_cli.py process sample_land_doc.txt --password mySecurePassword123
   ```

## API Endpoints

The API provides the following endpoints for integration:

### System Information
- `GET /api/system/info` - Get system capabilities

### Document Operations
- `POST /api/documents/compress` - Compress a document
- `POST /api/documents/decompress` - Decompress a .ppc file
- `POST /api/documents/process` - Process document with LandGuard
- `GET /api/documents/info/<filename>` - Get file information

## File Structure

```
compression-/
├── api/                 # REST API server
│   ├── server.py        # Main API application
│   ├── requirements.txt # API dependencies
│   └── README.md        # API documentation
├── frontend/            # React web interface
│   ├── src/             # Source code
│   ├── package.json     # Frontend dependencies
│   └── README.md        # Frontend documentation
├── pcc/                 # PCC compression system
│   ├── main.py          # PCC CLI interface
│   ├── core/            # Core modules
│   ├── compressors/     # Compression algorithms
│   ├── crypto/          # Encryption modules
│   └── requirements.txt # PCC dependencies
├── landguard/           # LandGuard fraud detection
│   ├── cli/             # CLI interface
│   ├── agents/          # Autonomous agents
│   ├── core/            # Core modules
│   └── requirements.txt # LandGuard dependencies
└── SETUP_GUIDE.md       # This file
```

## Troubleshooting

### Common Issues

1. **Port Conflicts**
   - If port 5000 is in use, modify `api/server.py` to use a different port
   - If port 5175 is in use, Vite will automatically use the next available port

2. **Module Import Errors**
   - Ensure you're in the correct directory when running commands
   - Check that all dependencies are installed
   - Verify the virtual environment is activated

3. **CORS Errors**
   - The API has CORS enabled for local development
   - For production, configure CORS appropriately

4. **File Upload Issues**
   - Check file size limits (currently 16MB)
   - Verify file types are allowed (.txt, .pdf, .doc, .docx, .jpg, .jpeg, .png)

### Testing the Integration

1. **Verify API is Running**
   ```bash
   curl http://localhost:5000
   ```

2. **Test Document Compression via API**
   ```bash
   curl -X POST \
     -F "file=@test.txt" \
     -F "password=test123" \
     http://localhost:5000/api/documents/compress \
     -o test.txt.ppc
   ```

3. **Verify Frontend Can Access API**
   - Open browser developer tools
   - Check Network tab for successful API requests

## Extending the System

### Adding New Features

1. **Backend Extensions**
   - Add new modules in `pcc/` or `landguard/` directories
   - Update CLI interfaces to expose new functionality
   - Add new endpoints in `api/server.py`

2. **Frontend Extensions**
   - Create new components in `frontend/src/components/`
   - Add new routes in `frontend/src/App.jsx`
   - Update UI to reflect new capabilities

3. **API Extensions**
   - Add new endpoints in `api/server.py`
   - Follow existing patterns for error handling
   - Update API documentation

## Security Considerations

- Passwords are used for encryption but not stored
- File uploads are sanitized and validated
- Temporary files are cleaned up after processing
- CORS is configured for development only

For production deployment:
- Implement proper authentication
- Use HTTPS with valid certificates
- Configure firewalls appropriately
- Set up logging and monitoring

## Performance Optimization

- For large file processing, consider implementing streaming
- Add caching for frequently accessed data
- Implement background job processing for long-running tasks
- Use a production WSGI server like Gunicorn for the API

## Support

For issues with the complete system:

1. Check all servers are running (API on port 5000, frontend on port 5175+)
2. Verify all dependencies are installed
3. Check browser console and server logs for error messages
4. Ensure file paths are correct in all configuration files
5. Contact the development team for assistance

## Next Steps

After setting up the complete system:

1. Process sample documents through the web interface
2. Test all API endpoints with curl or Postman
3. Customize the frontend UI to match your branding
4. Extend the system with additional features
5. Prepare for production deployment