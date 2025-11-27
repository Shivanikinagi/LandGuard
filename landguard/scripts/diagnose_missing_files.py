"""
Comprehensive diagnostic to verify all files needed for the complete workflow:
Upload → Anomaly Detection → Compression → Encryption → .ppc → IPFS → Blockchain → Audit
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple

def check_file(filepath: Path) -> Tuple[bool, int, str]:
    """Check if file exists and return status"""
    if not filepath.exists():
        return False, 0, "❌ MISSING"
    
    size = filepath.stat().st_size
    if size == 0:
        return False, 0, "⚠️ EMPTY"
    
    if size < 100:
        return False, size, "⚠️ INCOMPLETE"
    
    return True, size, "✅ OK"

def analyze_workflow_files():
    """Analyze all files needed for the complete workflow"""
    
    base_path = Path(__file__).parent.parent
    
    print("\n" + "="*80)
    print("  🔍 LANDGUARD COMPLETE WORKFLOW FILES DIAGNOSTIC")
    print("="*80 + "\n")
    
    # Workflow requirement mapping
    workflow_files = {
        "1️⃣ FILE UPLOAD & PROCESSING": {
            "api/routes/upload.py": "Handle document uploads",
            "api/models/requests.py": "Upload request schemas",
            "detector/__init__.py": "File type detection",
            "detector/extractors/__init__.py": "Document extractors",
        },
        
        "2️⃣ ANOMALY DETECTION & FRAUD CHECK": {
            "ML_section/anomaly_detector.py": "Detect suspicious patterns",
            "ML_section/fraud_classifier.py": "Classify fraud risk",
            "ML_section/feature_engineering.py": "Extract features",
            "core/analyzer.py": "Main analysis engine",
        },
        
        "3️⃣ COMPRESSION (PCC Integration)": {
            "../pcc/main.py": "PCC compression CLI",
            "../pcc/compressors/compressor.py": "Compression engine",
            "../pcc/models/base.py": "Compression models",
            "core/landguard/compression_bridge.py": "Bridge to PCC",
        },
        
        "4️⃣ ENCRYPTION": {
            "../pcc/crypto/aes.py": "AES-256-GCM encryption",
            "core/security/encryption.py": "Security layer",
            "database/auth.py": "Authentication & hashing",
        },
        
        "5️⃣ .PPC FILE FORMAT": {
            "../pcc/core/ppc_format.py": "PPC format handler",
            "../pcc/container.py": "Container management",
            "api/routes/analysis.py": "Analysis results",
        },
        
        "6️⃣ IPFS UPLOAD": {
            "../pcc/storage/ipfs_client.py": "IPFS client",
            "Blockchain/blockchain/ipfs_handler.py": "IPFS handler",
            "core/blockchain/ipfs_integration.py": "IPFS integration",
        },
        
        "7️⃣ BLOCKCHAIN RECORDING": {
            "Blockchain/blockchain/smart_contract.py": "Smart contract",
            "Blockchain/blockchain/transaction_handler.py": "Transaction handler",
            "core/blockchain/blockchain_client.py": "Blockchain client",
        },
        
        "8️⃣ AUDIT TRAIL": {
            "database/models.py": "Audit log models",
            "database/repositories.py": "Data access layer",
            "api/routes/statistics.py": "Audit statistics",
        },
        
        "9️⃣ VERIFICATION": {
            "Blockchain/blockchain/verifier.py": "CID verification",
            "api/routes/health.py": "System health checks",
            "core/analyzer.py": "Analysis verification",
        },
        
        "🔧 CORE INFRASTRUCTURE": {
            "api/main.py": "FastAPI application",
            "api/dependencies.py": "Auth dependencies",
            "database/connection.py": "Database connection",
            "requirements.txt": "Python dependencies",
            ".env": "Environment config",
        }
    }
    
    missing_files = []
    incomplete_files = []
    existing_files = []
    total_files = 0
    
    for workflow_step, files in workflow_files.items():
        print(f"\n{workflow_step}")
        print("-" * 80)
        
        for filepath, description in files.items():
            total_files += 1
            full_path = base_path / filepath
            exists, size, status = check_file(full_path)
            
            print(f"  {status} {filepath:<50} {description}")
            if size > 0:
                print(f"       └─ Size: {size:,} bytes")
            
            if not exists:
                if "MISSING" in status:
                    missing_files.append((filepath, description))
                else:
                    incomplete_files.append((filepath, description, size))
            else:
                existing_files.append(filepath)
    
    # Summary
    print("\n" + "="*80)
    print("  📊 WORKFLOW READINESS SUMMARY")
    print("="*80)
    print(f"✅ Complete files:     {len(existing_files)}/{total_files}")
    print(f"⚠️  Incomplete files:   {len(incomplete_files)}/{total_files}")
    print(f"❌ Missing files:      {len(missing_files)}/{total_files}")
    
    completion_rate = (len(existing_files) / total_files) * 100
    print(f"\n📈 Overall Completion: {completion_rate:.1f}%")
    
    if completion_rate >= 90:
        print("🟢 Status: READY TO DEPLOY")
    elif completion_rate >= 70:
        print("🟡 Status: MOSTLY READY - Minor fixes needed")
    elif completion_rate >= 50:
        print("🟠 Status: PARTIAL - Significant work needed")
    else:
        print("🔴 Status: NOT READY - Major components missing")
    
    # Critical missing files
    if missing_files:
        print("\n" + "="*80)
        print("  🔴 CRITICAL MISSING FILES")
        print("="*80)
        for filepath, description in missing_files:
            print(f"  ❌ {filepath}")
            print(f"     Purpose: {description}")
    
    if incomplete_files:
        print("\n" + "="*80)
        print("  ⚠️  INCOMPLETE FILES (Need Review)")
        print("="*80)
        for filepath, description, size in incomplete_files:
            print(f"  ⚠️  {filepath} ({size} bytes)")
            print(f"     Purpose: {description}")
    
    # Workflow stage analysis
    print("\n" + "="*80)
    print("  🔄 WORKFLOW STAGE READINESS")
    print("="*80)
    
    for stage_name in workflow_files.keys():
        stage_files = workflow_files[stage_name]
        stage_ready = sum(1 for f in stage_files.keys() if (base_path / f).exists() and (base_path / f).stat().st_size > 100)
        stage_total = len(stage_files)
        stage_percent = (stage_ready / stage_total) * 100 if stage_total > 0 else 0
        
        status_icon = "✅" if stage_percent == 100 else "⚠️" if stage_percent >= 50 else "❌"
        print(f"  {status_icon} {stage_name:<40} {stage_ready}/{stage_total} files ({stage_percent:.0f}%)")
    
    print("\n" + "="*80 + "\n")
    
    return missing_files, incomplete_files, completion_rate

if __name__ == "__main__":
    missing, incomplete, completion = analyze_workflow_files()
    
    if completion >= 90:
        print("✅ Project is ready for deployment!")
        sys.exit(0)
    else:
        print(f"⚠️  Project needs {100 - completion:.1f}% more work")
        sys.exit(1)