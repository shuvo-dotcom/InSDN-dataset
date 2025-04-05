# train_gan.py
import torch
import torch.nn as nn
import torch.optim as optim
import pandas as pd
import numpy as np
from tqdm import tqdm
import argparse
import os
import logging
import sys
import matplotlib.pyplot as plt
import seaborn as sns
from .gan_model import GAN

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/training.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

def plot_training_progress(d_losses, g_losses, save_dir):
    """Plot and save training progress graphs"""
    plt.figure(figsize=(15, 5))
    
    # Loss curves
    plt.subplot(1, 2, 1)
    plt.plot(d_losses, label='Discriminator Loss', color='blue', alpha=0.7)
    plt.plot(g_losses, label='Generator Loss', color='red', alpha=0.7)
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.title('Training Losses Over Time')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Loss ratio
    plt.subplot(1, 2, 2)
    loss_ratio = [g/d if d != 0 else 1.0 for g, d in zip(g_losses, d_losses)]
    plt.plot(loss_ratio, label='G/D Loss Ratio', color='green', alpha=0.7)
    plt.axhline(y=1.0, color='r', linestyle='--', alpha=0.3)
    plt.xlabel('Epoch')
    plt.ylabel('G/D Loss Ratio')
    plt.title('Generator/Discriminator Loss Ratio')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, 'training_progress.png'))
    plt.close()

def train_gan(epochs=50, batch_size=64, data_path=None):
    """Train the GAN model with logging and visualization"""
    logging.info("Starting GAN training process")
    
    # Create reports directory if it doesn't exist
    reports_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'reports')
    os.makedirs(reports_dir, exist_ok=True)
    
    # Load and preprocess data
    if data_path is None:
        data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'processed', 'train_data.csv')
    
    logging.info(f"Loading data from {data_path}")
    data = pd.read_csv(data_path)
    data = torch.FloatTensor(data.values)
    logging.info(f"Loaded data shape: {data.shape}")
    
    # Initialize GAN
    input_dim = data.shape[1]
    gan = GAN(input_dim)
    logging.info(f"Initialized GAN with input dimension: {input_dim}")
    
    # Initialize optimizers and loss function
    d_optimizer = optim.Adam(gan.discriminator.parameters(), lr=0.0002, betas=(0.5, 0.999))
    g_optimizer = optim.Adam(gan.generator.parameters(), lr=0.0002, betas=(0.5, 0.999))
    criterion = nn.BCELoss()
    logging.info("Initialized optimizers and loss function")
    
    # Lists to store losses for plotting
    d_losses = []
    g_losses = []
    
    # Training loop
    logging.info(f"Starting training for {epochs} epochs")
    for epoch in tqdm(range(epochs), desc="Training GAN"):
        total_d_loss = 0
        total_g_loss = 0
        num_batches = 0
        
        # Shuffle data
        indices = torch.randperm(len(data))
        
        for i in range(0, len(data), batch_size):
            batch_indices = indices[i:i + batch_size]
            real_data = data[batch_indices]
            
            # Train one step
            d_loss, g_loss = gan.train_step(real_data, len(batch_indices),
                                          d_optimizer, g_optimizer, criterion)
            
            total_d_loss += d_loss
            total_g_loss += g_loss
            num_batches += 1
        
        # Calculate average losses for the epoch
        avg_d_loss = total_d_loss / num_batches
        avg_g_loss = total_g_loss / num_batches
        
        # Store losses for plotting
        d_losses.append(avg_d_loss)
        g_losses.append(avg_g_loss)
        
        # Log progress
        logging.info(f"Epoch {epoch+1}/{epochs} - D_loss: {avg_d_loss:.4f}, G_loss: {avg_g_loss:.4f}")
        tqdm.write(f"Epoch {epoch+1}/{epochs} - D_loss: {avg_d_loss:.4f}, G_loss: {avg_g_loss:.4f}")
        
        # Save intermediate plots every 10 epochs
        if (epoch + 1) % 10 == 0:
            plot_training_progress(d_losses, g_losses, reports_dir)
    
    # Plot final training progress
    plot_training_progress(d_losses, g_losses, reports_dir)
    
    # Save losses to CSV for later analysis
    loss_df = pd.DataFrame({
        'epoch': range(1, epochs + 1),
        'discriminator_loss': d_losses,
        'generator_loss': g_losses
    })
    loss_df.to_csv(os.path.join(reports_dir, 'training_losses.csv'), index=False)
    
    # Save the trained models
    save_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')
    os.makedirs(save_dir, exist_ok=True)
    
    generator_path = os.path.join(save_dir, 'generator.pth')
    discriminator_path = os.path.join(save_dir, 'discriminator.pth')
    
    torch.save(gan.generator.state_dict(), generator_path)
    torch.save(gan.discriminator.state_dict(), discriminator_path)
    
    logging.info(f"Saved generator to {generator_path}")
    logging.info(f"Saved discriminator to {discriminator_path}")
    logging.info("Training completed successfully")
    
    return gan

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Train GAN model')
    parser.add_argument('--epochs', type=int, default=50, help='Number of epochs')
    parser.add_argument('--batch_size', type=int, default=64, help='Batch size')
    parser.add_argument('--data', type=str, default=None, help='Path to training data')
    args = parser.parse_args()
    
    train_gan(epochs=args.epochs, batch_size=args.batch_size, data_path=args.data)
