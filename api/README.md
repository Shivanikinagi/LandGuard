# LandGuard & PCC API

REST API interface for the LandGuard document processing and PCC compression systems.

## Features

- Document compression with PCC
- Document decompression
- LandGuard fraud detection processing
- File information retrieval
- Secure file handling

## Prerequisites

- Python 3.8+
- Virtual environment (recommended)

## Installation

1. Navigate to the API directory:
```bash
cd compression-/api
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
```bash
# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

## Starting the Server

```bash
python server.py
```

The server will start on `http://localhost:5000`.

## API Endpoints

### Health Check
- `GET /` - Server status and availability check

### System Information
- `GET /api/system/info` - Get system information and available modules

### Document Processing
- `POST /api/documents/compress` - Compress a document using PCC
- `POST /api/documents/decompress` - Decompress a .ppc document
- `POST /api/documents/process` - Process a document through LandGuard workflow
- `GET /api/documents/info/<filename>` - Get information about a .ppc file

## Usage Examples

### Compress a Document
```bash
curl -X POST \
  -F "file=@sample.txt" \
  -F "password=mysecretpassword" \
  http://localhost:5000/api/documents/compress \
  -o compressed.ppc
```

### Process a Document with LandGuard
```bash
curl -X POST \
  -F "file=@land_document.txt" \
  -F "password=mysecretpassword" \
  http://localhost:5000/api/documents/process
```

## Frontend Integration

The API is designed to work with the React frontend located in the `frontend/` directory. The frontend communicates with the API through HTTP requests.

## Security

- All file uploads are sanitized
- Passwords are used for encryption but not stored
- Files are processed in isolated temporary directories
- CORS is enabled for local development

## Error Handling

The API returns appropriate HTTP status codes and JSON error messages:
- 200: Success
- 400: Bad request (missing file, invalid parameters)
- 404: File not found
- 500: Internal server error
- 503: Service unavailable (module not available)

## Development

To extend the API:

1. Add new endpoints in `server.py`
2. Import required modules from `pcc/` or `landguard/` directories
3. Follow the existing patterns for error handling and response formatting

## Deployment

For production deployment:

1. Use a production WSGI server like Gunicorn
2. Set up proper SSL/TLS certificates
3. Configure firewall rules
4. Implement authentication if needed
5. Set up logging and monitoring

## Support

For issues with the API:
1. Check server logs for error messages
2. Verify all dependencies are installed
3. Ensure the PCC and LandGuard modules are accessible
4. Contact the development team for assistance