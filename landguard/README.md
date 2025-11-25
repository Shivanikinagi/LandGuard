# 🔍 LandGuard - Land Record Fraud Detection System

**Intelligent anomaly detection for land records and property transactions**

LandGuard is an AI-powered fraud detection system that analyzes land records, ownership histories, and property transactions to identify suspicious patterns and potential fraud indicators.

---

## 🌟 Features

- **🚨 Comprehensive Fraud Detection**
  - Rapid ownership transfer detection
  - Transaction party mismatch identification
  - Duplicate land ID detection
  - Large transfer flagging
  - Cross-document conflict detection
  - Chronological validation
  - Evidence capture and reporting

- **📄 Multi-Format Support**
  - JSON structured data
  - CSV files
  - PDF documents (with table extraction)
  - Scanned images (OCR)

- **💻 Modern CLI Interface**
  - Single file analysis
  - Batch processing
  - Customizable rules via YAML config
  - Rich terminal output

- **📊 Detailed Reporting**
  - Severity-based issue classification
  - Confidence scoring
  - Evidence snippets
  - Batch analysis summaries

---

## 🚀 Installation

### Prerequisites
- Python 3.8+
- Tesseract OCR (for scanned documents)

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Install Tesseract (for OCR)
**Windows:**
```bash
# Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
# Add to PATH: C:\Program Files\Tesseract-OCR
```

**Linux:**
```bash
sudo apt-get install tesseract-ocr
```

**Mac:**
```bash
brew install tesseract
```

---

## 📖 Quick Start

### Analyze a Single File
```bash
python -m landguard.cli.main analyze path/to/land_record.json
```

### Batch Analysis
```bash
python -m landguard.cli.main batch path/to/records_dir/ --output batch_report.json
```

### Generate Config Template
```bash
python -m landguard.cli.main config-template --output my_config.yaml
```

### Analyze with Custom Config
```bash
python -m landguard.cli.main analyze record.json --config my_config.yaml --verbose
```

---

## 🔧 Configuration

Create a custom configuration file to adjust detection thresholds:

```yaml
# landguard_config.yaml
rapid_transfer_days: 180
rapid_transfer_count: 2
large_transfer_threshold: 10000000
name_similarity_threshold: 85
date_order_tolerance_days: 1
```

---

## 📝 Input Data Format

### JSON Format
```json
{
  "land_id": "LD-12345",
  "owner_history": [
    {
      "owner_name": "John Smith",
      "date": "2015-05-01",
      "document_id": "DOC-001"
    }
  ],
  "transactions": [
    {
      "tx_id": "TX-001",
      "date": "2020-03-15",
      "amount": 15000000,
      "from_party": "John Smith",
      "to_party": "Jane Doe"
    }
  ],
  "property_area": 5000.0,
  "registration_number": "REG-2015-001"
}
```

### CSV Format
```csv
land_id,owner_name,owner_date,tx_id,tx_date,amount,from_party,to_party
LD-12345,John Smith,2015-05-01,TX-001,2020-03-15,15000000,John Smith,Jane Doe
```

---

## 🚨 Detected Fraud Indicators

### 1. Rapid Ownership Transfers
**What:** Multiple ownership changes within a short time period  
**Why Suspicious:** May indicate document forgery or shell company schemes  
**Example:** 3 transfers in 60 days

### 2. Party Mismatches
**What:** Transaction "from" party doesn't match current owner  
**Why Suspicious:** Invalid transfer or unauthorized transaction  
**Example:** Alice owns land, but transaction shows Bob as seller

### 3. Duplicate Land IDs
**What:** Same land ID appears in multiple documents  
**Why Suspicious:** Possible double-registration or forged documents  
**Example:** LD-12345 in both file1.json and file2.pdf

### 4. Large Transfers
**What:** Transaction amounts significantly above threshold  
**Why Suspicious:** Unusual activity requiring scrutiny  
**Example:** 50M transfer when average is 5M

### 5. Cross-Document Conflicts
**What:** Different values for same land ID across files  
**Why Suspicious:** Data tampering or administrative errors  
**Example:** Property area 1000 sqm in doc1, 1500 sqm in doc2

### 6. Time Order Violations
**What:** Ownership dates not in chronological order  
**Why Suspicious:** Backdated transfers or data entry errors  
**Example:** Owner B dated before Owner A

### 7. Missing Mandatory Fields
**What:** Critical data fields are empty  
**Why Suspicious:** Incomplete or manipulated records  
**Example:** No land_id or owner_history

---

## 📊 Sample Output

```
📊 Analysis Report
─────────────────────────────────────────────────
Record: LD-67890
Confidence Score: 45%
Issues Found: 2
Highest Severity: high

🚨 Detected Issues
┏━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Type            ┃ Severity ┃ Message                  ┃
┡━━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ rapid_transfer  │ high     │ Ownership changed 2      │
│                 │          │ times within 16 days     │
│ party_mismatch  │ high     │ Transaction from party   │
│                 │          │ doesn't match owner      │
└─────────────────┴──────────┴──────────────────────────┘
```

---

## 🧪 Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=landguard --cov-report=html

# Run specific test file
pytest tests/test_analyzer.py -v
```

---

## 🏗️ Project Structure

```
landguard/
├── cli/
│   └── main.py              # CLI interface
├── core/
│   ├── models.py            # Data models
│   └── landguard/
│       └── analyzer.py      # Fraud detection engine
├── detector/
│   └── extractors/          # File parsers
│       ├── json_extractor.py
│       ├── csv_extractor.py
│       ├── pdf_extractor.py
│       └── ocr_extractor.py
├── tests/
│   ├── test_analyzer.py     # Unit tests
│   └── test_extractors.py
├── data/
│   └── samples/             # Sample data
└── config.yaml              # Default config
```

---

## 🔬 How It Works

1. **File Ingestion** → Parse JSON/CSV/PDF/Image files
2. **Data Extraction** → Convert to standardized `LandRecord` format
3. **Normalization** → Clean dates, names, amounts
4. **Rule Engine** → Run 7+ fraud detection rules
5. **Evidence Collection** → Capture specific violations
6. **Confidence Scoring** → Calculate overall trust score
7. **Report Generation** → Output structured anomaly report

---

## 🎯 Use Cases

- **Government Land Registries** - Detect fraudulent property registrations
- **Title Insurance Companies** - Validate ownership chains
- **Legal Firms** - Due diligence for property transactions
- **Banks** - Verify collateral for land-backed loans
- **Anti-Corruption Agencies** - Identify suspicious patterns

---

## 🤝 Contributing

Contributions welcome! Areas for improvement:

- Additional fraud detection rules
- Machine learning-based anomaly scoring
- Real-time monitoring dashboard
- Integration with blockchain verification
- Multi-language support for OCR

---

## 📄 License

MIT License - See LICENSE file for details

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/yourusername/landguard/issues)
- **Email:** support@landguard.example
- **Docs:** [Full Documentation](https://docs.landguard.example)

---

**Built with ❤️ for safer property transactions**