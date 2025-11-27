# Database Setup Guide

## Prerequisites

### 1. Install PostgreSQL

**Windows:**
```powershell
choco install postgresql
```

### 2. Install MongoDB

**Windows:**
```powershell
choco install mongodb
```

---

## Setup Steps

### Step 1: Install Python Dependencies

```bash
cd landguard
pip install -r requirements.txt
```

### Step 2: Configure Database

Edit `config/database.yaml` with your credentials.

### Step 3: Create PostgreSQL Database

```bash
psql -U postgres
CREATE DATABASE landguard;
CREATE USER landguard_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE landguard TO landguard_user;
\q
```

### Step 4: Run Setup Script

```bash
python scripts/setup_database.py
```

### Step 5: Verify Installation

```bash
pytest tests/test_database.py -v
```

---

## Usage Examples

```python
from database import db_manager
from database.repositories import LandRecordRepository

session = db_manager.get_pg_session()
record_repo = LandRecordRepository(session)

record = record_repo.create({
    'land_id': 'LND-001',
    'location': 'Mumbai',
    'area_sqft': 5000.0,
    'property_type': 'residential',
    'current_owner': 'John Doe'
})

session.close()
```