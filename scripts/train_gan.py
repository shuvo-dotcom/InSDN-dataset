# train_gan.py
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import numpy as np
import logging
import os
from tqdm import tqdm
import matplotlib.pyplot as plt
from gan_model import Generator, Discriminator
from data_loader import load_data, create_dataloader

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/training.log'),
        logging.StreamHandler()
    ]
)

class FeatureWeightedLoss(nn.Module):
    def __init__(self, n_features):
        super(FeatureWeightedLoss, self).__init__()
        # Initialize feature weights (can be adjusted based on domain knowledge)
        self.feature_weights = nn.Parameter(torch.ones(n_features))
        
    def forward(self, real_data, fake_data):
        # Calculate weighted MSE loss for each feature
        feature_losses = torch.mean((real_data - fake_data) ** 2, dim=0)
        weighted_loss = torch.mean(feature_losses * self.feature_weights)
        return weighted_loss

def gradient_penalty(discriminator, real_data, fake_data, device):
    batch_size = real_data.size(0)
    alpha = torch.rand(batch_size, 1).to(device)
    interpolated = (alpha * real_data + (1 - alpha) * fake_data).requires_grad_(True)
    
    d_interpolated = discriminator(interpolated)
    gradients = torch.autograd.grad(
        outputs=d_interpolated,
        inputs=interpolated,
        grad_outputs=torch.ones_like(d_interpolated),
        create_graph=True,
        retain_graph=True
    )[0]
    
    gradients = gradients.view(batch_size, -1)
    gradient_norm = gradients.norm(2, dim=1)
    penalty = torch.mean((gradient_norm - 1) ** 2)
    return penalty

def train_gan(data_path, epochs=50, batch_size=256, lr_g=0.0001, lr_d=0.0001, beta1=0.5, beta2=0.999):
    """Train the GAN model with improved techniques."""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logging.info(f"Using device: {device}")
    
    # Load and preprocess data
    data = load_data(data_path)
    n_features = len(data.columns)
    dataloader = create_dataloader(data, batch_size=batch_size)
    
    # Initialize models
    generator = Generator(output_dim=n_features).to(device)
    discriminator = Discriminator(input_dim=n_features).to(device)
    feature_loss = FeatureWeightedLoss(n_features).to(device)
    
    # Initialize optimizers with learning rate scheduling
    g_optimizer = optim.Adam(generator.parameters(), lr=lr_g, betas=(beta1, beta2))
    d_optimizer = optim.Adam(discriminator.parameters(), lr=lr_d, betas=(beta1, beta2))
    
    g_scheduler = optim.lr_scheduler.ReduceLROnPlateau(g_optimizer, mode='min', factor=0.5, patience=5, verbose=True)
    d_scheduler = optim.lr_scheduler.ReduceLROnPlateau(d_optimizer, mode='min', factor=0.5, patience=5, verbose=True)
    
    # Training metrics
    g_losses = []
    d_losses = []
    
    # Training loop
    logging.info("Starting training loop")
    for epoch in range(epochs):
        pbar = tqdm(dataloader, desc=f"Epoch {epoch+1}/{epochs}")
        epoch_g_loss = 0
        epoch_d_loss = 0
        n_batches = 0
        
        for real_data in pbar:
            batch_size = real_data.size(0)
            real_data = real_data.to(device)
            
            # Train Discriminator
            d_optimizer.zero_grad()
            
            # Generate fake data
            z = torch.randn(batch_size, 100).to(device)
            fake_data = generator(z).detach()
            
            # Calculate discriminator loss with gradient penalty
            d_real = discriminator(real_data)
            d_fake = discriminator(fake_data)
            
            gp = gradient_penalty(discriminator, real_data, fake_data, device)
            d_loss = -(torch.mean(d_real) - torch.mean(d_fake)) + 10.0 * gp
            
            d_loss.backward()
            d_optimizer.step()
            
            # Train Generator (more frequently as training progresses)
            if n_batches % max(1, 5 - epoch // 10) == 0:
                g_optimizer.zero_grad()
                
                # Generate new fake data
                z = torch.randn(batch_size, 100).to(device)
                fake_data = generator(z)
                
                # Calculate generator loss with feature weighting
                g_loss_gan = -torch.mean(discriminator(fake_data))
                g_loss_feature = feature_loss(real_data, fake_data)
                g_loss = g_loss_gan + 0.1 * g_loss_feature
                
                g_loss.backward()
                g_optimizer.step()
                
                epoch_g_loss += g_loss.item()
            
            epoch_d_loss += d_loss.item()
            n_batches += 1
            
            # Update progress bar
            pbar.set_postfix({
                'D_loss': f"{d_loss.item():.4f}",
                'G_loss': f"{g_loss.item():.4f}" if 'g_loss' in locals() else "N/A"
            })
        
        # Calculate average epoch losses
        avg_g_loss = epoch_g_loss / n_batches
        avg_d_loss = epoch_d_loss / n_batches
        g_losses.append(avg_g_loss)
        d_losses.append(avg_d_loss)
        
        # Update learning rates
        g_scheduler.step(avg_g_loss)
        d_scheduler.step(avg_d_loss)
        
        # Log progress
        logging.info(f"Epoch [{epoch+1}/{epochs}] completed. "
                    f"Avg Loss D: {avg_d_loss:.4f}, Avg Loss G: {avg_g_loss:.4f}")
        
        # Save loss plot every 5 epochs
        if (epoch + 1) % 5 == 0:
            plt.figure(figsize=(10, 5))
            plt.plot(g_losses, label='Generator')
            plt.plot(d_losses, label='Discriminator')
            plt.xlabel('Epoch')
            plt.ylabel('Loss')
            plt.legend()
            plt.savefig('reports/loss_plot.png')
            plt.close()
            logging.info(f"Loss plot saved at epoch {epoch + 1}")
    
    # Save the trained models
    os.makedirs('data/models', exist_ok=True)
    torch.save(generator.state_dict(), 'data/models/generator.pt')
    torch.save(discriminator.state_dict(), 'data/models/discriminator.pt')
    
    # Save final loss plot
    plt.figure(figsize=(10, 5))
    plt.plot(g_losses, label='Generator')
    plt.plot(d_losses, label='Discriminator')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    plt.savefig('reports/final_loss_plot.png')
    plt.close()
    
    logging.info("Training completed successfully")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--epochs', type=int, default=50)
    parser.add_argument('--batch_size', type=int, default=256)
    parser.add_argument('--data', type=str, default='data/processed/train_data.csv')
    args = parser.parse_args()
    
    train_gan(args.data, args.epochs, args.batch_size)
