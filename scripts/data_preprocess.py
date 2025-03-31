# data_preprocess.py
import pandas as pd
from sklearn.model_selection import train_test_split
import os

def preprocess_data():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))

    # Load datasets
    normal_df = pd.read_csv(os.path.join(base_dir, 'raw', 'Normal_data.csv'))
    ovs_df = pd.read_csv(os.path.join(base_dir, 'raw', 'OVS.csv'))
    meta_df = pd.read_csv(os.path.join(base_dir, 'raw', 'metasploitable.csv'))

    # Combine anomaly datasets
    anomaly_df = pd.concat([ovs_df, meta_df])

    # Label encoding: Normal = 0, Anomaly = 1
    normal_df['label'] = 0
    anomaly_df['label'] = 1

    # Combine normal and anomaly data (adjust proportions as needed)
    combined_df = pd.concat([normal_df, anomaly_df])

    # Select exactly 84 features (excluding label)
    feature_columns = combined_df.columns.tolist()
    feature_columns.remove('label')
    feature_columns = feature_columns[:84]  # Ensure exactly 84 features
    combined_df = combined_df[feature_columns + ['label']]

    # Shuffle the dataset
    combined_df = combined_df.sample(frac=1).reset_index(drop=True)

    # Split into train (70%), validation (15%), and test (15%)
    train_df, temp_df = train_test_split(combined_df, test_size=0.3, random_state=42)
    validation_df, test_df = train_test_split(temp_df, test_size=0.5, random_state=42)

    # Save processed datasets
    train_df.to_csv(os.path.join(base_dir, 'processed', 'train_data.csv'), index=False)
    validation_df.to_csv(os.path.join(base_dir, 'processed', 'validation_data.csv'), index=False)
    test_df.to_csv(os.path.join(base_dir, 'processed', 'test_data.csv'), index=False)

    print(f"Data preprocessing complete. Files saved in '{os.path.join(base_dir, 'processed')}'.")
    print(f"Number of features: {len(feature_columns)}")

if __name__ == "__main__":
    preprocess_data()
