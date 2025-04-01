# data_preprocess.py
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import os

def preprocess_data():
    """Preprocess network data for GAN training"""
    # Create necessary directories
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    processed_dir = os.path.join(data_dir, 'processed')
    os.makedirs(processed_dir, exist_ok=True)
    
    # Generate sample network data (replace this with your actual data collection)
    n_samples = 1000
    n_features = 10
    
    # Generate synthetic network features
    data = {
        'packet_size': np.random.normal(1000, 200, n_samples),
        'inter_arrival_time': np.random.exponential(0.1, n_samples),
        'protocol_type': np.random.choice(['TCP', 'UDP', 'ICMP'], n_samples),
        'src_port': np.random.randint(1024, 65535, n_samples),
        'dst_port': np.random.randint(1024, 65535, n_samples),
        'src_ip': np.random.randint(0, 2**32, n_samples),
        'dst_ip': np.random.randint(0, 2**32, n_samples),
        'packet_count': np.random.poisson(5, n_samples),
        'byte_count': np.random.normal(5000, 1000, n_samples),
        'duration': np.random.exponential(1.0, n_samples)
    }
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    # Convert categorical variables to numeric
    df['protocol_type'] = df['protocol_type'].map({'TCP': 0, 'UDP': 1, 'ICMP': 2})
    
    # Scale numerical features
    scaler = StandardScaler()
    numerical_features = ['packet_size', 'inter_arrival_time', 'src_port', 'dst_port',
                         'src_ip', 'dst_ip', 'packet_count', 'byte_count', 'duration']
    df[numerical_features] = scaler.fit_transform(df[numerical_features])
    
    # Save processed data
    output_path = os.path.join(processed_dir, 'train_data.csv')
    df.to_csv(output_path, index=False)
    
    print(f"Preprocessed data saved to {output_path}")
    print(f"Shape: {df.shape}")
    print("\nFeature statistics:")
    print(df.describe())
    
    return output_path

if __name__ == "__main__":
    preprocess_data()
