import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
import torch
from torch.utils.data import Dataset, DataLoader

class NetworkDataset(Dataset):
    def __init__(self, data):
        self.data = torch.FloatTensor(data.values)
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        return self.data[idx]

def load_data(data_path):
    """Load and preprocess the data."""
    # Load the data
    df = pd.read_csv(data_path)
    
    # Separate features and target if exists
    if 'label' in df.columns:
        X = df.drop('label', axis=1)
    else:
        X = df
    
    # Handle string columns
    encoders = {}
    for column in X.columns:
        if X[column].dtype == 'object':
            encoders[column] = LabelEncoder()
            X[column] = encoders[column].fit_transform(X[column].astype(str))
    
    # Scale the features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Convert back to DataFrame with original column names
    X_scaled_df = pd.DataFrame(X_scaled, columns=X.columns)
    
    return X_scaled_df

def create_dataloader(data, batch_size=256, num_workers=4):
    """Create a PyTorch DataLoader for the data."""
    dataset = NetworkDataset(data)
    dataloader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=True
    )
    
    return dataloader 