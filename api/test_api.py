#!/usr/bin/env python3
"""
Test script to verify all API endpoints are working correctly
"""

import requests
import os
import json
import time

# API base URL
BASE_URL = "http://localhost:5000"

def test_health_check():
    """Test the health check endpoint"""
    print("Testing health check endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            data = response.json()
            print(f"  ✓ Health check passed: {data}")
            return True
        else:
            print(f"  ✗ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"  ✗ Health check error: {e}")
        return False

def test_system_info():
    """Test the system info endpoint"""
    print("Testing system info endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/system/info")
        if response.status_code == 200:
            data = response.json()
            print(f"  ✓ System info retrieved: {data['name']} v{data['version']}")
            return True
        else:
            print(f"  ✗ System info failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"  ✗ System info error: {e}")
        return False

def create_test_file():
    """Create a test file for testing"""
    test_content = """Land Document Sample

Property Address: 123 Main Street, Anytown, ST 12345
Owner: John Doe
Parcel Number: 123-456-789
Lot Size: 0.5 acres
Zoning: Residential

This is a sample land document for demonstration purposes."""
    
    with open("test_document.txt", "w") as f:
        f.write(test_content)
    
    return "test_document.txt"

def test_compress_endpoint():
    """Test the compress endpoint"""
    print("Testing compress endpoint...")
    try:
        # Create test file
        test_file = create_test_file()
        
        with open(test_file, 'rb') as f:
            files = {'file': f}
            data = {'password': 'test_password'}
            response = requests.post(f"{BASE_URL}/api/documents/compress", files=files, data=data)
            
        if response.status_code == 200:
            # Save the compressed file
            with open("test_document.txt.ppc", "wb") as f:
                f.write(response.content)
            print("  ✓ File compressed successfully")
            return True
        else:
            print(f"  ✗ Compression failed: {response.status_code}")
            # Try to parse error response as JSON
            try:
                if response.headers.get('content-type', '').startswith('application/json'):
                    error_data = response.json()
                    print(f"    Error: {error_data}")
            except:
                print(f"    Error response: {response.text}")
            return False
    except Exception as e:
        print(f"  ✗ Compression error: {e}")
        return False

def test_decompress_endpoint():
    """Test the decompress endpoint"""
    print("Testing decompress endpoint...")
    try:
        # Check if compressed file exists
        if not os.path.exists("test_document.txt.ppc"):
            print("  ! Compressed file not found, skipping decompress test")
            return True
            
        with open("test_document.txt.ppc", 'rb') as f:
            files = {'file': f}
            data = {'password': 'test_password'}
            response = requests.post(f"{BASE_URL}/api/documents/decompress", files=files, data=data)
            
        if response.status_code == 200:
            # Try to parse response as JSON
            try:
                data = response.json()
                print(f"  ✓ File decompressed successfully: {data}")
                # Save the decompressed file
                with open("restored_test_document.txt", "wb") as f:
                    f.write(response.content)
                return True
            except:
                print(f"  ✗ Failed to parse decompress response as JSON")
                return False
        else:
            print(f"  ✗ Decompression failed: {response.status_code}")
            # Try to parse error response as JSON
            try:
                if response.headers.get('content-type', '').startswith('application/json'):
                    error_data = response.json()
                    print(f"    Error: {error_data}")
            except:
                print(f"    Error response: {response.text}")
            return False
    except Exception as e:
        print(f"  ✗ Decompression error: {e}")
        return False

def test_info_endpoint():
    """Test the file info endpoint"""
    print("Testing file info endpoint...")
    try:
        # Check if compressed file exists
        if not os.path.exists("test_document.txt.ppc"):
            print("  ! Compressed file not found, skipping info test")
            return True
            
        response = requests.get(f"{BASE_URL}/api/documents/info/test_document.txt.ppc")
        
        if response.status_code == 200:
            # Try to parse response as JSON
            try:
                data = response.json()
                print(f"  ✓ File info retrieved: {data.get('original_filename', 'Unknown')}")
                return True
            except:
                print(f"  ✗ Failed to parse info response as JSON")
                return False
        else:
            print(f"  ✗ File info failed: {response.status_code}")
            # Try to parse error response as JSON
            try:
                if response.headers.get('content-type', '').startswith('application/json'):
                    error_data = response.json()
                    print(f"    Error: {error_data}")
            except:
                print(f"    Error response: {response.text}")
            return False
    except Exception as e:
        print(f"  ✗ File info error: {e}")
        return False

def test_process_endpoint():
    """Test the process endpoint"""
    print("Testing process endpoint...")
    try:
        # Create test file
        test_file = create_test_file()
        
        with open(test_file, 'rb') as f:
            files = {'file': f}
            data = {'password': 'test_password'}
            response = requests.post(f"{BASE_URL}/api/documents/process", files=files, data=data)
            
        if response.status_code == 200:
            # Try to parse response as JSON
            try:
                data = response.json()
                print(f"  ✓ Document processed successfully: {data.get('message', 'Processed successfully')}")
                return True
            except:
                print(f"  ✗ Failed to parse process response as JSON")
                return False
        else:
            print(f"  ✗ Processing failed: {response.status_code}")
            # Try to parse error response as JSON
            try:
                if response.headers.get('content-type', '').startswith('application/json'):
                    error_data = response.json()
                    print(f"    Error: {error_data}")
            except:
                print(f"    Error response: {response.text}")
            return False
    except Exception as e:
        print(f"  ✗ Processing error: {e}")
        return False

def cleanup_test_files():
    """Clean up test files"""
    test_files = ["test_document.txt", "test_document.txt.ppc", "restored_test_document.txt"]
    for file in test_files:
        if os.path.exists(file):
            os.remove(file)
            print(f"  Cleaned up {file}")

def main():
    """Main test function"""
    print("=== LandGuard & PCC API Test Suite ===\n")
    
    # Test endpoints
    tests = [
        test_health_check,
        test_system_info,
        test_compress_endpoint,
        test_decompress_endpoint,
        test_info_endpoint,
        test_process_endpoint
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
            print()
            time.sleep(1)  # Small delay between tests
        except Exception as e:
            print(f"  ✗ Test failed with exception: {e}\n")
            results.append(False)
    
    # Summary
    passed = sum(results)
    total = len(results)
    print(f"=== Test Results: {passed}/{total} tests passed ===")
    
    if passed == total:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed. Please check the output above.")
    
    # Cleanup
    cleanup_test_files()
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)