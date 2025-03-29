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
    def __init__(self, input_dim=100, output_dim=84, hidden_dims=[512, 512, 256]):
        super(Generator, self).__init__()
        
        # Input layer
        layers = [
            nn.Linear(input_dim, hidden_dims[0]),
            nn.LayerNorm(hidden_dims[0]),
            nn.LeakyReLU(0.2)
        ]
        
        # Hidden layers with residual blocks
        for i in range(len(hidden_dims)-1):
            layers.extend([
                ResidualBlock(hidden_dims[i]),
                nn.Linear(hidden_dims[i], hidden_dims[i+1]),
                nn.LayerNorm(hidden_dims[i+1]),
                nn.LeakyReLU(0.2),
                nn.Dropout(0.1)
            ])
        
        # Output layer
        layers.extend([
            ResidualBlock(hidden_dims[-1]),
            nn.Linear(hidden_dims[-1], output_dim),
            nn.Tanh()
        ])
        
        self.model = nn.Sequential(*layers)
        
    def forward(self, z):
        return self.model(z)

# Example discriminator update in gan_model.py
# gan_model.py Discriminator update
class Discriminator(nn.Module):
    def __init__(self, input_dim=84, hidden_dims=[256, 512, 512]):
        super(Discriminator, self).__init__()
        
        # Input layer
        layers = [
            nn.Linear(input_dim, hidden_dims[0]),
            nn.LayerNorm(hidden_dims[0]),
            nn.LeakyReLU(0.2),
            nn.Dropout(0.2)
        ]
        
        # Hidden layers with residual blocks
        for i in range(len(hidden_dims)-1):
            layers.extend([
                ResidualBlock(hidden_dims[i]),
                nn.Linear(hidden_dims[i], hidden_dims[i+1]),
                nn.LayerNorm(hidden_dims[i+1]),
                nn.LeakyReLU(0.2),
                nn.Dropout(0.2)
            ])
        
        # Output layer
        layers.extend([
            ResidualBlock(hidden_dims[-1]),
            nn.Linear(hidden_dims[-1], 1),
            nn.Sigmoid()
        ])
        
        self.model = nn.Sequential(*layers)
        
    def forward(self, x):
        return self.model(x)

