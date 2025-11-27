# LandGuard CLI

Command line interface for processing land documents through the complete LandGuard workflow.

## Features

- Process land documents through the complete security workflow
- Detect anomalies and suspicious activities
- Compress and encrypt documents
- Create .ppc files with metadata
- Upload to IPFS for decentralized storage
- Store CID on blockchain for immutable proof
- Generate audit records
- Verify document authenticity later

## Usage

### Process Documents

```bash
python cli/landguard_cli.py process [file1] [file2] ... [--password PASSWORD]
```

Example:
```bash
python cli/landguard_cli.py process documents/property_deed.pdf documents/sale_agreement.json
```

### Verify Documents

```bash
python cli/landguard_cli.py verify [CID]
```

Example:
```bash
python cli/landguard_cli.py verify QmXyZ123AbC456DeF789GhI012JkLmNoPqRsTuVwXyZ123AbC4
```

## Output Format

The CLI produces clear, structured output similar to:

```
🚀 LANDGUARD WORKFLOW STARTED
============================

📄 STEP 1: FILE UPLOAD
---------------------
• Processing: property_deed.pdf (2.1 MB)
✅ Uploaded 1 files successfully

🔍 STEP 2: ANOMALY DETECTION
---------------------------
• Property: LD-2024-1234
• Files: 1 files processed
⚠️  ANOMALIES FOUND:
❌ RAPID_TRANSFER: Property changed hands 3 times in 6 months
• Risk Score: 7.8/10 (HIGH RISK)

... (more steps)

✅ WORKFLOW COMPLETE
===================

📋 FINAL SUMMARY:
• Property: LD-2024-1234
• Status: ⚠️  PROCESSED WITH WARNINGS
• Risk Level: HIGH (7.8/10)
• Storage: IPFS + Blockchain
• Verification CID: QmXyZ123AbC456DeF789GhI012JkLmNoPqRsTuVwXyZ123AbC4

🔍 VERIFICATION COMMAND:
landguard verify QmXyZ123AbC456DeF789GhI012JkLmNoPqRsTuVwXyZ123AbC4
```

## Simple User Output

For end users, a simplified version is also displayed:

```
==================================================
✅ LANDGUARD PROCESSING COMPLETE

Property: LD-2024-1234
Status: ⚠️  PROCESSED (Minor issues)
Risk: 7.8/10 (HIGH)
Storage: 🔒 Secured on blockchain

🔍 Your Verification Code: QmXyZ123AbC456DeF789GhI012JkLmNoPqRsTuVwXyZ123AbC4

Need to verify later? Use: landguard verify QmXyZ123AbC456DeF789GhI012JkLmNoPqRsTuVwXyZ123AbC4
```