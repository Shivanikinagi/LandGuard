"""
Comprehensive test suite for all extractors
Run with: python tests/test_all_extractors.py
"""

import sys

import os 
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import json
import csv
import os
from datetime import date

from landguard.detector.extractors.base import get_registry
from landguard.detector.extractors.json_extractor import JSONExtractor
from landguard.detector.extractors.csv_extractor import CSVExtractor
# from detector.extractors.pdf_extractor import PDFExtractor
# from detector.extractors.ocr_extractor import OCRExtractor


def create_test_json():
    """Create test JSON file"""
    data = {
        "land_id": "LD-TEST-001",
        "registration_date": "2018-01-15",
        "area": 2500.0,
        "location": "Test Plot, Mumbai",
        "registration_number": "REG-2018-001",
        "owner_history": [
            {"name": "Alice Kumar", "date": "2018-01-15", "document_id": "DOC001"},
            {"name": "Bob Shah", "date": "2020-06-20", "document_id": "DOC002"}
        ],
        "transactions": [
            {
                "tx_id": "TX001",
                "date": "2020-06-20",
                "amount": 5000000,
                "from": "Alice Kumar",
                "to": "Bob Shah"
            }
        ]
    }
    
    with open("test_data.json", "w") as f:
        json.dump(data, f, indent=2)
    
    return "test_data.json"


def create_test_csv():
    """Create test CSV file"""
    with open("test_data.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['land_id', 'tx_id', 'date', 'from_party', 'to_party', 'amount'])
        writer.writerow(['LD-TEST-002', 'TX001', '2020-06-20', 'Alice Kumar', 'Bob Shah', '5000000'])
        writer.writerow(['LD-TEST-002', 'TX002', '2024-03-10', 'Bob Shah', 'Carol Singh', '7500000'])
    
    return "test_data.csv"


def test_json_extractor():
    """Test JSON extractor"""
    print("\n" + "="*60)
    print("🧪 TESTING JSON EXTRACTOR")
    print("="*60)
    
    test_file = create_test_json()
    
    try:
        extractor = JSONExtractor()
        result = extractor.extract(test_file)
        
        print(f"\n✓ Extraction: {'✅ SUCCESS' if result.success else '❌ FAILED'}")
        
        if result.success and result.record:
            record = result.record
            print(f"\n📋 Extracted Data:")
            print(f"  • Land ID: {record.land_id}")
            print(f"  • Owners: {len(record.owner_history)}")
            for owner in record.owner_history:
                print(f"    - {owner.name} (from {owner.date})")
            print(f"  • Transactions: {len(record.transactions)}")
            for tx in record.transactions:
                print(f"    - {tx.tx_id}: ₹{tx.amount:,.0f} ({tx.from_party} → {tx.to_party})")
            print(f"  • Area: {record.area} sq ft")
            print(f"  • Location: {record.location}")
            print(f"  • Confidence: {record.extraction_confidence:.2%}")
        
        if result.warnings:
            print(f"\n⚠️  Warnings ({len(result.warnings)}):")
            for warning in result.warnings:
                print(f"  • {warning}")
        
        if result.error:
            print(f"\n❌ Error: {result.error}")
        
        return result.success
    
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)


def test_csv_extractor():
    """Test CSV extractor"""
    print("\n" + "="*60)
    print("🧪 TESTING CSV EXTRACTOR")
    print("="*60)
    
    test_file = create_test_csv()
    
    try:
        extractor = CSVExtractor()
        result = extractor.extract(test_file)
        
        print(f"\n✓ Extraction: {'✅ SUCCESS' if result.success else '❌ FAILED'}")
        
        if result.success and result.record:
            record = result.record
            print(f"\n📋 Extracted Data:")
            print(f"  • Land ID: {record.land_id}")
            print(f"  • Owners: {len(record.owner_history)}")
            for owner in record.owner_history:
                print(f"    - {owner.name} (from {owner.date})")
            print(f"  • Transactions: {len(record.transactions)}")
            for tx in record.transactions:
                print(f"    - {tx.tx_id}: ₹{tx.amount:,.0f} ({tx.from_party} → {tx.to_party})")
            print(f"  • Confidence: {record.extraction_confidence:.2%}")
        
        if result.warnings:
            print(f"\n⚠️  Warnings ({len(result.warnings)}):")
            for warning in result.warnings:
                print(f"  • {warning}")
        
        if result.error:
            print(f"\n❌ Error: {result.error}")
        
        return result.success
    
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)


def test_registry():
    """Test extractor registry"""
    print("\n" + "="*60)
    print("🧪 TESTING EXTRACTOR REGISTRY")
    print("="*60)
    
    registry = get_registry()
    
    print(f"\n✓ Registered Extractors: {len(registry.extractors)}")
    for i, extractor in enumerate(registry.extractors, 1):
        print(f"  {i}. {extractor.__class__.__name__} ({extractor.extraction_method})")
    
    # Test file type detection
    test_cases = [
        ("test.json", "application/json", JSONExtractor),
        ("test.csv", "text/csv", CSVExtractor),
    ]
    
    print(f"\n✓ Testing File Type Detection:")
    for filename, mime, expected_class in test_cases:
        extractor = registry.get_extractor(filename, mime)
        if extractor:
            match = isinstance(extractor, expected_class)
            status = "✅" if match else "❌"
            print(f"  {status} {filename} ({mime}) → {extractor.__class__.__name__}")
        else:
            print(f"  ❌ {filename} ({mime}) → No extractor found")
    
    return True


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🚀 LANDGUARD EXTRACTOR TEST SUITE")
    print("="*60)
    
    results = {
        "JSON Extractor": test_json_extractor(),
        "CSV Extractor": test_csv_extractor(),
        "Registry": test_registry()
    }
    
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    total = len(results)
    passed = sum(results.values())
    
    for test_name, passed_test in results.items():
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"  {status} - {test_name}")
    
    print(f"\n{'='*60}")
    print(f"✓ Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
    else:
        print(f"⚠️  {total - passed} test(s) failed")
    
    print("="*60 + "\n")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)