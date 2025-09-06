# # compressors/compressor.py


# from pathlib import Path


# import os





# def compress_file(file_path: str, file_info: dict, model_hint: str = None):


#     ext = Path(file_path).suffix.lower()


#     original_data = open(file_path, "rb").read()


#     original_size = len(original_data)





#     if file_info["type"] == "image" and (model_hint == "vae" or not model_hint):


#         print("🖼️ Using VAE for image compression...")


#         try:


#             from compressors.image.vae import VAE, load_image, save_latent


#             import torch





#             model = VAE()


#             model.load_state_dict(torch.load("../models/vae.pth"))


#             model.eval()





#             img = load_image(file_path)


#             with torch.no_grad():


#                 mu, _ = model.encode(img)


#             latent_path = file_path + ".vae.npy"


#             save_latent(mu, latent_path)


#             compressed = open(latent_path, "rb").read()


#             return compressed, "vae-v1", len(compressed)


#         except Exception as e:


#             print(f"⚠️ VAE failed: {e}")


#             return original_data, "none", original_size





#     elif file_info["type"] == "text":


#         print("📄 Using BPE for text compression...")


#         try:


#             from compressors.text.bpe_compressor import compress_text


#             text = original_data.decode('utf-8')


#             compressed = compress_text(text)


#             return compressed, "bpe-gpt-lite", len(compressed)


#         except Exception as e:


#             print(f"⚠️ BPE failed: {e}")


#             return original_data, "none", original_size





#     else:


#         print("⚠️ No AI model yet. Using raw data.")


#         return original_data, "none", original_size





# read.py


from curses import raw
import cbor2


import sys


from pathlib import Path





# HACK: Add project root and pcc directory to path to allow imports.


project_root = Path(__file__).resolve().parent.parent


sys.path.insert(0, str(project_root))


sys.path.insert(1, str(project_root / "pcc"))





from crypto.aes import decrypt_data


from core.ppc_format import PPCFile


import cbor2





# Load and parse


# Remove or comment out these lines at the bottom of the file:
# with open("downloaded.ppc", "rb") as f:
#     ppc_data = f.read()



decoded = PPCFile.unpack(raw)


data_blob = decoded["data"]


header = decoded["header"]





# Decrypt


encrypted_blob = cbor2.loads(data_blob)


password = "middleout"  # ← Use the correct password





try:


    decrypted = decrypt_data(encrypted_blob, password)


    print("🔓 DECRYPTED CONTENT:")


    print(decrypted.decode('utf-8'))


except Exception as e:


    print("❌ Decryption failed:", str(e))