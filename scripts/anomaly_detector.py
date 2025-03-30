# anomaly_detector.py
import torch
import pandas as pd
from gan_model import Discriminator
import openai
import argparse
import os

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Argument parsing
parser = argparse.ArgumentParser(description='GAN-based anomaly detection with GPT verification.')
parser.add_argument('--test_data', type=str, default=os.path.join(BASE_DIR, '..', 'data', 'processed', 'test_data.csv'), help='Path to test data')
parser.add_argument('--threshold', type=float, default=0.5, help='Threshold for anomaly detection')
parser.add_argument('--openai_key', type=str, required=True, help='OpenAI API key')
args = parser.parse_args()

# Load test data
test_data = pd.read_csv(args.test_data)
print(test_data.columns)
features = test_data.drop('label', axis=1).apply(pd.to_numeric, errors='coerce').fillna(0)
test_tensor = torch.tensor(features.values, dtype=torch.float32)

# Load discriminator
feature_dim = features.shape[1]
discriminator = Discriminator(feature_dim)
discriminator.load_state_dict(torch.load(os.path.join(BASE_DIR, '..', 'data', 'models', 'discriminator.pt')))
discriminator.eval()

# GPT API setup
openai.api_key = args.openai_key

# Detect anomalies
with torch.no_grad():
    scores = discriminator(test_tensor).numpy().flatten()

anomalies = test_data[scores < args.threshold]

print(f"Total anomalies detected: {len(anomalies)}")

# GPT-based verification
for idx, anomaly in anomalies.iterrows():
    anomaly_info = anomaly.to_dict()
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "Verify if the following network traffic pattern indicates a genuine anomaly."},
            {"role": "user", "content": str(anomaly_info)}
        ]
    )

    verification_result = response.choices[0].message.content
    print(f"Anomaly ID {idx}: GPT Verification Result: {verification_result}\n")

print("Anomaly detection and GPT verification complete.")
