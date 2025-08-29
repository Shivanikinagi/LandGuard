from PIL import Image
import os

image_dir = r"f:\data_com\dataset"
for img_file in os.listdir(image_dir):
    img_path = os.path.join(image_dir, img_file)
    try:
        with Image.open(img_path) as img:
            img.verify()
    except Exception:
        print(f"Removing corrupted file: {img_path}")
        os.remove(img_path)