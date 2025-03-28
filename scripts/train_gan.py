# train_gan.py
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import pandas as pd
from gan_model import Generator, Discriminator
import argparse
import os

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Argument parsing
parser = argparse.ArgumentParser(description='Train GAN model.')
parser.add_argument('--epochs', type=int, default=100, help='Number of epochs for training')
parser.add_argument('--data', type=str, default=os.path.join(BASE_DIR, '..', 'data', 'processed', 'train_data.csv'), help='Path to processed training data')
parser.add_argument('--batch_size', type=int, default=256, help='Batch size for training')
args = parser.parse_args()

# GPU availability check
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Hyperparameters
batch_size = args.batch_size
epochs = args.epochs
lr_G = 0.0002
lr_D = 0.00015
input_dim = 100  # Size of noise input

# Load dataset
train_data = pd.read_csv(args.data)
feature_dim = train_data.shape[1] - 1  # Adjust automatically based on dataset
train_features = train_data.drop('label', axis=1).apply(pd.to_numeric, errors='coerce').fillna(0)
real_data = torch.tensor(train_features.values, dtype=torch.float32)

# DataLoader
data_loader = DataLoader(TensorDataset(real_data), batch_size=batch_size, shuffle=True, num_workers=4, pin_memory=True)

# Initialize models
generator = Generator(input_dim, feature_dim).to(device)
discriminator = Discriminator(feature_dim).to(device)

# Optimizers
optimizer_G = optim.Adam(generator.parameters(), lr=lr_G, betas=(0.5, 0.999))
optimizer_D = optim.Adam(discriminator.parameters(), lr=lr_D, betas=(0.5, 0.999))

# Loss function
criterion = nn.BCELoss()

# Training loop
for epoch in range(epochs):
    for batch_idx, (real_batch,) in enumerate(data_loader):
        batch_size_curr = real_batch.size(0)
        real_batch = real_batch.to(device)

        # Train Discriminator
        discriminator.zero_grad()
        real_labels = torch.ones(batch_size_curr, 1, device=device) * 0.95
        fake_labels = torch.zeros(batch_size_curr, 1, device=device) + 0.05

        outputs_real = discriminator(real_batch)
        loss_real = criterion(outputs_real, real_labels)

        noise = torch.randn(batch_size_curr, input_dim, device=device)
        fake_data = generator(noise)
        outputs_fake = discriminator(fake_data.detach())
        loss_fake = criterion(outputs_fake, fake_labels)

        loss_D = loss_real + loss_fake
        loss_D.backward()
        optimizer_D.step()

        # Train Generator
        generator.zero_grad()
        outputs = discriminator(fake_data)
        loss_G = criterion(outputs, real_labels)
        loss_G.backward()
        optimizer_G.step()

        if batch_idx % 20 == 0:
            print(f"Epoch [{epoch+1}/{epochs}], Batch [{batch_idx}/{len(data_loader)}], Loss D: {loss_D.item():.4f}, Loss G: {loss_G.item():.4f}")

    print(f"Epoch [{epoch+1}/{epochs}] completed. Loss D: {loss_D.item():.4f}, Loss G: {loss_G.item():.4f}")

# Save trained models
model_path = os.path.join(BASE_DIR, '..', 'data', 'models')
os.makedirs(model_path, exist_ok=True)
torch.save(generator.state_dict(), os.path.join(model_path, 'generator.pt'))
torch.save(discriminator.state_dict(), os.path.join(model_path, 'discriminator.pt'))

print("GAN training completed. Models saved.")
