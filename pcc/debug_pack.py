def pack_command(args):
    file_path = args.file
    password = args.password

    print(f"📦 Packing {file_path} with password {password}...")

    from detector.file_type import detect_file_type
    from crypto.aes import encrypt_data
    from core.ppc_format import PPCFile
    from storage.ipfs_client import upload_to_ipfs
    import cbor2, os

    with open(file_path, "rb") as f:
        data = f.read()
    print(f"Read {len(data)} bytes")

    info = detect_file_type(file_path)
    print("Detected:", info)

    encrypted = encrypt_data(data, password)
    payload = cbor2.dumps(encrypted)
    print("Encrypted, payload size:", len(payload))

    metadata = {
        "original_filename": os.path.basename(file_path),
        "original_mime_type": "text/plain",
        "file_type": "text",
        "model_used": "none-yet",
        "encryption_algo": "AES-256-GCM"
    }
    ppc = PPCFile(payload, metadata)
    output = file_path + ".ppc"
    with open(output, "wb") as f:
        f.write(ppc.pack())
    print(f"✅ Wrote {output}")

    link = upload_to_ipfs(output)
    print(f"🌐 IPFS Link: {link}")
