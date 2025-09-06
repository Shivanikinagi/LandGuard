# test_import.py
try:
    from detector.file_type import detect_file_type
    print("✅ Success: detect_file_type imported!")
    
    # Test with a real file
    result = detect_file_type("samples/test.txt")
    print("🔍 Detected:", result)
except Exception as e:
    print("❌ Error:", e)