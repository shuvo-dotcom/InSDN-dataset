# gan_model.py
import torch
import torch.nn as nn

class ResidualBlock(nn.Module):
    def __init__(self, dim):
        super(ResidualBlock, self).__init__()
        self.block = nn.Sequential(
            nn.Linear(dim, dim),
            nn.LayerNorm(dim),
            nn.LeakyReLU(0.2),
            nn.Linear(dim, dim),
            nn.LayerNorm(dim)
        )
        self.activation = nn.LeakyReLU(0.2)
    
    def forward(self, x):
        return self.activation(x + self.block(x))

# Define Generator Model
class Generator(nn.Module):
    def __init__(self, input_dim, hidden_dim=128):
        super(Generator, self).__init__()
        self.model = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim * 2),
            nn.ReLU(),
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, input_dim),
            nn.Tanh()
        )
    
    def forward(self, x):
        return self.model(x)

# Example discriminator update in gan_model.py
# gan_model.py Discriminator update
class Discriminator(nn.Module):
    def __init__(self, input_dim, hidden_dim=128):
        super(Discriminator, self).__init__()
        self.model = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.LeakyReLU(0.2),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.LeakyReLU(0.2),
            nn.Linear(hidden_dim // 2, 1),
            nn.Sigmoid()
        )
    
    def forward(self, x):
        return self.model(x)

class GAN:
    def __init__(self, input_dim, hidden_dim=128):
        self.generator = Generator(input_dim, hidden_dim)
        self.discriminator = Discriminator(input_dim, hidden_dim)
        self.input_dim = input_dim
        
    def generate_fake_samples(self, batch_size):
        noise = torch.randn(batch_size, self.input_dim)
        return self.generator(noise)
    
    def train_step(self, real_data, batch_size, d_optimizer, g_optimizer, criterion):
        # Train Discriminator
        d_optimizer.zero_grad()
        real_labels = torch.ones(batch_size, 1)
        fake_labels = torch.zeros(batch_size, 1)
        
        # Real data
        d_real = self.discriminator(real_data)
        d_real_loss = criterion(d_real, real_labels)
        
        # Fake data
        fake_data = self.generate_fake_samples(batch_size)
        d_fake = self.discriminator(fake_data.detach())
        d_fake_loss = criterion(d_fake, fake_labels)
        
        d_loss = d_real_loss + d_fake_loss
        d_loss.backward()
        d_optimizer.step()
        
        # Train Generator
        g_optimizer.zero_grad()
        fake_data = self.generate_fake_samples(batch_size)
        d_fake = self.discriminator(fake_data)
        g_loss = criterion(d_fake, real_labels)
        
        g_loss.backward()
        g_optimizer.step()
        
        return d_loss.item(), g_loss.item()

