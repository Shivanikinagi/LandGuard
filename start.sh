#!/bin/bash
cd api && pip install -r requirements.txt
cd ../pcc && pip install -r requirements.txt
cd ../api
uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000}
