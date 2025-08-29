# Save this as extract_cifar10_images.py in your project root (f:\data_com)
import os
import pickle
import numpy as np
from PIL import Image
from torchvision.io import read_image, ImageReadMode

# Path to your CIFAR-10 batch files
cifar_dir = r"c:\Users\skpav\Downloads\cifar-10-python\cifar-10-batches-py"
# Output directory for images
output_dir = r"f:\data_com\dataset"
os.makedirs(output_dir, exist_ok=True)

def unpickle(file):
    with open(file, 'rb') as fo:
        dict = pickle.load(fo, encoding='bytes')
    return dict

batch_files = [f"data_batch_{i}" for i in range(1, 6)] + ["test_batch"]

img_count = 0
for batch_name in batch_files:
    batch_path = os.path.join(cifar_dir, batch_name)
    batch = unpickle(batch_path)
    data = batch[b'data']
    for i, img_flat in enumerate(data):
        img = img_flat.reshape(3, 32, 32).transpose(1, 2, 0)  # (32,32,3)
        img = Image.fromarray(img)
        img.save(os.path.join(output_dir, f"cifar_{img_count:05d}.png"), format="PNG")
        img_count += 1

print(f"Extracted {img_count} images to {output_dir}")

import os

image_dir = r"f:\data_com\dataset"
for img_file in os.listdir(image_dir):
    img_path = os.path.join(image_dir, img_file)
    if os.path.getsize(img_path) == 0:  # Empty file
        print(f"Removing empty file: {img_path}")
        os.remove(img_path)

def __getitem__(self, idx):
    img_path = self.image_paths[idx]
    try:
        image = read_image(str(img_path), mode=ImageReadMode.RGB)
    except Exception as e:
        print(f"Skipping corrupted image: {img_path}, error: {e}")
        # Optionally, return a dummy image or raise
        return torch.zeros((3, 32, 32))
    return image