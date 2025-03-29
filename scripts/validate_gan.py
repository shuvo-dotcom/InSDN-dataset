import torch
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error, mean_absolute_error
from gan_model import Generator, Discriminator
from data_loader import load_data
import logging
import os

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/validation.log'),
        logging.StreamHandler()
    ]
)

def validate_gan(data_path, generator_path='data/models/generator.pt', num_samples=100000):
    """Validate the trained GAN model."""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logging.info(f"Using device: {device}")
    
    # Load real data
    real_data = load_data(data_path)
    n_features = len(real_data.columns)
    
    # Sample real data to match num_samples
    if len(real_data) > num_samples:
        real_data = real_data.sample(n=num_samples, random_state=42)
    elif len(real_data) < num_samples:
        # If we have fewer real samples, we'll use all of them
        num_samples = len(real_data)
        logging.info(f"Using {num_samples} samples (all available real data)")
    
    # Load trained generator
    generator = Generator(output_dim=n_features).to(device)
    generator.load_state_dict(torch.load(generator_path))
    generator.eval()
    
    # Generate synthetic data
    logging.info(f"Generating {num_samples} synthetic samples...")
    batch_size = 1000  # Process in batches to avoid memory issues
    synthetic_data_list = []
    
    with torch.no_grad():
        for i in range(0, num_samples, batch_size):
            current_batch_size = min(batch_size, num_samples - i)
            z = torch.randn(current_batch_size, 100).to(device)
            synthetic_batch = generator(z).cpu().numpy()
            synthetic_data_list.append(synthetic_batch)
            if (i + batch_size) % 10000 == 0:
                logging.info(f"Generated {i + batch_size}/{num_samples} samples")
    
    synthetic_data = np.vstack(synthetic_data_list)
    logging.info(f"Generated {len(synthetic_data)} synthetic samples")
    
    # Convert to DataFrame for easier comparison
    synthetic_df = pd.DataFrame(synthetic_data, columns=real_data.columns)
    
    # Calculate metrics
    mse = mean_squared_error(real_data, synthetic_data)
    mae = mean_absolute_error(real_data, synthetic_data)
    
    # Calculate per-feature metrics
    feature_metrics = {}
    for column in real_data.columns:
        feature_metrics[column] = {
            'mse': mean_squared_error(real_data[column], synthetic_df[column]),
            'mae': mean_absolute_error(real_data[column], synthetic_df[column])
        }
    
    # Log results
    logging.info(f"Overall MSE: {mse:.4f}")
    logging.info(f"Overall MAE: {mae:.4f}")
    
    # Plot feature distributions
    plt.figure(figsize=(15, 10))
    for i, column in enumerate(real_data.columns[:9]):  # Plot first 9 features
        plt.subplot(3, 3, i+1)
        plt.hist(real_data[column], bins=50, alpha=0.5, label='Real', density=True)
        plt.hist(synthetic_df[column], bins=50, alpha=0.5, label='Synthetic', density=True)
        plt.title(f'{column}\nMSE: {feature_metrics[column]["mse"]:.4f}')
        plt.legend()
    plt.tight_layout()
    plt.savefig('reports/feature_distributions.png')
    plt.close()
    
    # Save metrics to CSV
    metrics_df = pd.DataFrame([
        {'metric': 'overall_mse', 'value': mse},
        {'metric': 'overall_mae', 'value': mae}
    ])
    
    feature_metrics_df = pd.DataFrame([
        {'feature': col, 'mse': metrics['mse'], 'mae': metrics['mae']}
        for col, metrics in feature_metrics.items()
    ])
    
    os.makedirs('reports', exist_ok=True)
    metrics_df.to_csv('reports/overall_metrics.csv', index=False)
    feature_metrics_df.to_csv('reports/feature_metrics.csv', index=False)
    
    # Save synthetic data
    synthetic_df.to_csv('data/processed/synthetic_data.csv', index=False)
    logging.info("Synthetic data saved to data/processed/synthetic_data.csv")
    
    logging.info("Validation completed successfully")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', type=str, default='data/processed/test_data.csv')
    parser.add_argument('--generator', type=str, default='data/models/generator.pt')
    parser.add_argument('--num_samples', type=int, default=100000)
    args = parser.parse_args()
    
    validate_gan(args.data, args.generator, args.num_samples) 