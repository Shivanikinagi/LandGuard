# compressors/image/train_vae.py


from curses.ascii import FF
import torch


import torch.optim as optim


from tqdm import tqdm


from vae import VAE, load_image, save_latent





def train_vae_on_image(file_path, epochs=50):


    model = VAE(latent_dim=128)


    optimizer = optim.Adam(model.parameters(), lr=1e-3)


    img_tensor = load_image(file_path)





    for epoch in tqdm(range(epochs), desc="Training VAE"):


        optimizer.zero_grad()


        recon, mu, logvar = model(img_tensor)


        


        mse_loss = FF.mse_loss(recon, img_tensor)


        kl_loss = -0.5 * torch.sum(1 + logvar - mu.pow(2) - logvar.exp())


        loss = mse_loss + 0.001 * kl_loss





        loss.backward()


        optimizer.step()





    torch.save(model.state_dict(), "../models/vae.pth")


    print("✅ VAE saved to models/vae.pth")





    with torch.no_grad():


        mu, _ = model.encode(img_tensor)


    return mu