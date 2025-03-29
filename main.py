# main.py
from scripts.data_preprocess import preprocess_data
import subprocess
import argparse
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def main(epochs, data_path=None):
    print("Starting data preprocessing...")
    # preprocess_data()
    print("Data preprocessing finished successfully.")

    if data_path is None:
        data_path = os.path.join(BASE_DIR, 'data', 'processed', 'train_data.csv')

    print(f"Starting GAN training for {epochs} epochs...")
    subprocess.run(["python", os.path.join(BASE_DIR, "scripts", "train_gan.py"), 
                    "--epochs", str(epochs), 
                    "--data", data_path])
    print("GAN training finished successfully.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run preprocessing and GAN training.')
    parser.add_argument('--epochs', type=int, default=50, help='Number of epochs for GAN training')
    parser.add_argument('--data', type=str, default=None, help='Optional path to processed training data')

    args = parser.parse_args()
    main(args.epochs, args.data)
