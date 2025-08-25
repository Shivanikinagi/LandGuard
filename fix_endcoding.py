# Save as fix_encoding.py and run: python fix_encoding.py
import os

def convert_to_utf8_no_bom(root_dir):
    for folder, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.py'):
                path = os.path.join(folder, file)
                with open(path, 'rb') as f:
                    content = f.read()
                # Remove BOM if present
                if content.startswith(b'\xef\xbb\xbf'):
                    print(f"Fixing BOM in: {path}")
                    content = content[3:]
                    with open(path, 'wb') as f:
                        f.write(content)
                else:
                    # Re-save as UTF-8 (no BOM)
                    try:
                        text = content.decode('utf-8')
                        with open(path, 'w', encoding='utf-8') as f:
                            f.write(text)
                    except Exception:
                        pass

convert_to_utf8_no_bom('.')