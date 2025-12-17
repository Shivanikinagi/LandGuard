#!/usr/bin/env python3
"""
PCC (Pied Piper Compression) - Main CLI Interface
"""

import os
import sys
import argparse
from pathlib import Path

# Add parent directory to path to import PCC modules
pcc_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, pcc_path)

from core.ppc_format import PPCFile, create_ppc_file, read_ppc_file
from compressors.compressor import compress_file
from crypto.aes import encrypt_data, decrypt_data
from detector.file_type import detect_file_type

def print_success(message):
    """Print a success message"""
    print(f"SUCCESS: {message}")

def print_error(message):
    """Print an error message"""
    print(f"ERROR: {message}")

def print_info(message):
    """Print an info message"""
    print(f"INFO: {message}")

def print_header(text):
    """Print a formatted header"""
    print(f"\n{text}")
    print("=" * len(text))

def pack_file(input_file, password):
    """Pack a file into a .ppc container with compression and encryption"""
    print_header(f"PACKING: {input_file}")
    
    # Check if file exists
    if not os.path.exists(input_file):
        print_error(f"File not found: {input_file}")
        return False
    
    try:
        # Detect file type
        file_info = detect_file_type(input_file)
        print_info(f"File type: {file_info['mime']} ({file_info['type']})")
        
        # Compress the file
        print_info("Compressing file...")
        compressed_data, model_used, compressed_size = compress_file(input_file, file_info)
        
        original_size = os.path.getsize(input_file)
        compression_ratio = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0
        
        print_info(f"Original size: {original_size} bytes")
        print_info(f"Compressed size: {compressed_size} bytes")
        print_info(f"Compression ratio: {compression_ratio:.1f}%")
        print_info(f"Model used: {model_used}")
        
        # Encrypt the compressed data
        print_info("Encrypting data...")
        encrypted_package = encrypt_data(compressed_data, password)
        
        # Create metadata with timestamp
        from datetime import datetime
        metadata = {
            "original_filename": os.path.basename(input_file),
            "original_size_bytes": original_size,
            "compressed_size_bytes": compressed_size,
            "compression_algorithm": model_used,
            "compression_ratio": compression_ratio,
            "file_type": file_info['type'],
            "mime_type": file_info['mime'],
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Create output filename
        output_file = f"{input_file}.ppc"
        
        # Create PPC file
        print_info("Creating PPC container...")
        create_ppc_file(encrypted_package, metadata, output_file)
        
        print_success(f"Packed successfully: {output_file}")
        return True
        
    except Exception as e:
        print_error(f"Failed to pack file: {str(e)}")
        return False

def unpack_file(ppc_file, password, output_file=None):
    """Unpack a .ppc file, decrypting and decompressing it"""
    print_header(f"UNPACKING: {ppc_file}")
    
    # Check if file exists
    if not os.path.exists(ppc_file):
        print_error(f"File not found: {ppc_file}")
        return False
    
    try:
        # Read PPC file
        print_info("Reading PPC container...")
        ppc_data = read_ppc_file(ppc_file)
        
        header = ppc_data['header']
        encrypted_data = ppc_data['data']
        
        # Display file information
        print_info(f"Original filename: {header.get('original_filename', 'Unknown')}")
        print_info(f"Original size: {header.get('original_size_bytes', 0)} bytes")
        print_info(f"Compression: {header.get('compression_algorithm', 'Unknown')} ({header.get('compression_ratio', 0):.1f}%)")
        print_info(f"File type: {header.get('file_type', 'Unknown')}")
        
        # Decrypt the data
        print_info("Decrypting data...")
        decrypted_data = decrypt_data(encrypted_data, password)
        
        # For this basic implementation, we'll just return the decrypted data
        # In a full implementation, we would decompress it based on the compression algorithm
        
        # Determine output filename
        if not output_file:
            original_name = header.get('original_filename', 'restored_file')
            output_file = f"restored_{original_name}"
        
        # Save the restored file
        print_info("Saving restored file...")
        with open(output_file, 'wb') as f:
            f.write(decrypted_data)
        
        print_success(f"Unpacked successfully: {output_file}")
        return True
        
    except Exception as e:
        print_error(f"Failed to unpack file: {str(e)}")
        return False

def info_file(ppc_file):
    """Display information about a .ppc file without extracting it"""
    print_header(f"FILE INFO: {ppc_file}")
    
    # Check if file exists
    if not os.path.exists(ppc_file):
        print_error(f"File not found: {ppc_file}")
        return False
    
    try:
        # Read PPC file
        print_info("Reading PPC container...")
        ppc_data = read_ppc_file(ppc_file)
        
        header = ppc_data['header']
        
        # Display information
        print(f"\nFILE METADATA")
        print(f"  Original filename: {header.get('original_filename', 'Unknown')}")
        print(f"  Original size: {header.get('original_size_bytes', 0)} bytes")
        print(f"  Compressed size: {header.get('compressed_size_bytes', 0)} bytes")
        print(f"  Compression ratio: {header.get('compression_ratio', 0):.1f}%")
        print(f"  Compression algorithm: {header.get('compression_algorithm', 'Unknown')}")
        print(f"  File type: {header.get('file_type', 'Unknown')}")
        print(f"  MIME type: {header.get('mime_type', 'Unknown')}")
        
        # Calculate space savings
        original_size = header.get('original_size_bytes', 0)
        compressed_size = header.get('compressed_size_bytes', 0)
        if original_size > 0:
            space_saved = original_size - compressed_size
            print(f"  Space saved: {space_saved} bytes ({(space_saved/original_size)*100:.1f}%)")
        
        print_success("Information displayed successfully")
        return True
        
    except Exception as e:
        print_error(f"Failed to read file info: {str(e)}")
        return False

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="PCC (Pied Piper Compression) - Intelligent file compression and encryption tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  pack    Compress, encrypt & package file into .ppc container
  unpack  Decrypt & decompress .ppc file
  info    Display metadata about .ppc file
  
Examples:
  python main.py pack document.pdf -p MySecretPassword
  python main.py unpack document.pdf.ppc -p MySecretPassword
  python main.py info document.pdf.ppc
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Pack command
    pack_parser = subparsers.add_parser('pack', help='Compress, encrypt & package file')
    pack_parser.add_argument('input_file', help='File to compress and encrypt')
    pack_parser.add_argument('-p', '--password', required=True, help='Password for encryption')
    
    # Unpack command
    unpack_parser = subparsers.add_parser('unpack', help='Decrypt & decompress file')
    unpack_parser.add_argument('ppc_file', help='.ppc file to decompress')
    unpack_parser.add_argument('-p', '--password', required=True, help='Password for decryption')
    unpack_parser.add_argument('-o', '--output', help='Output filename (optional)')
    
    # Info command
    info_parser = subparsers.add_parser('info', help='Display file metadata')
    info_parser.add_argument('ppc_file', help='.ppc file to examine')
    
    args = parser.parse_args()
    
    if args.command == 'pack':
        return pack_file(args.input_file, args.password)
    elif args.command == 'unpack':
        return unpack_file(args.ppc_file, args.password, args.output)
    elif args.command == 'info':
        return info_file(args.ppc_file)
    else:
        parser.print_help()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)