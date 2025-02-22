"""
Main entry point for the InSDN Traffic Analysis project.
This script orchestrates the data preprocessing, feature extraction,
LLM-based analysis, and agent-based adaptation components.
"""

import os
import logging
from datetime import datetime
import yaml
from pathlib import Path
import kagglehub
import pandas as pd
from data_preprocessing.preprocessor import DataPreprocessor
from visualization.visualizer import NetworkTrafficVisualizer
import openai
from config import API_KEY

# Set the OpenAI API key
openai.api_key = API_KEY

# Setup logging
log_dir = Path('experiments/logs')
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / f'run_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def load_config(config_path: str = 'config/config.yaml') -> dict:
    """Load configuration from YAML file."""
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        logger.info(f"Successfully loaded configuration from {config_path}")
        return config
    except Exception as e:
        logger.error(f"Error loading configuration: {str(e)}")
        raise

def download_dataset() -> str:
    """Download the InSDN dataset from Kaggle."""
    try:
        logger.info("Downloading InSDN dataset from Kaggle...")
        path = kagglehub.dataset_download("badcodebuilder/insdn-dataset")
        logger.info(f"Dataset downloaded successfully to: {path}")
        return path
    except Exception as e:
        logger.error(f"Error downloading dataset: {str(e)}")
        raise

def load_and_process_data(data_path: str, preprocessor: DataPreprocessor):
    """Load and process the InSDN dataset."""
    try:
        # Find all CSV files in the dataset directory
        csv_files = list(Path(data_path).rglob("*.csv"))
        if not csv_files:
            raise FileNotFoundError("No CSV files found in the dataset")
        
        logger.info(f"Found {len(csv_files)} CSV files in the dataset")
        
        # Process each CSV file
        processed_dfs = []
        for csv_file in csv_files:
            logger.info(f"Processing file: {csv_file}")
            df = preprocessor.process(str(csv_file))
            processed_dfs.append(df)
        
        # Combine all processed dataframes
        final_df = pd.concat(processed_dfs, ignore_index=True)
        logger.info(f"Final processed dataset shape: {final_df.shape}")
        logger.info(f"Processed Data Columns: {final_df.columns.tolist()}")
        logger.info(f"Final DataFrame Columns after processing: {final_df.columns.tolist()}")
        
        return final_df
        
    except Exception as e:
        logger.error(f"Error processing data: {str(e)}")
        raise

def extract_features(data):
    # Extract relevant features from the incoming data
    features = {
        'Flow ID': data['Flow ID'],
        'Src IP': data['Src IP'],
        'Src Port': data['Src Port'],
        'Dst IP': data['Dst IP'],
        'Dst Port': data['Dst Port'],
        'Protocol': data['Protocol'],
        'Timestamp': data['Timestamp'],
        'Flow Duration': data['Flow Duration'],
        'Tot Fwd Pkts': data['Tot Fwd Pkts'],
        'Tot Bwd Pkts': data['Tot Bwd Pkts'],
        'TotLen Fwd Pkts': data['TotLen Fwd Pkts'],
        'TotLen Bwd Pkts': data['TotLen Bwd Pkts'],
        'Fwd Pkt Len Max': data['Fwd Pkt Len Max'],
        'Fwd Pkt Len Min': data['Fwd Pkt Len Min'],
        'Fwd Pkt Len Mean': data['Fwd Pkt Len Mean'],
        'Fwd Pkt Len Std': data['Fwd Pkt Len Std'],
        'Bwd Pkt Len Max': data['Bwd Pkt Len Max'],
        'Bwd Pkt Len Min': data['Bwd Pkt Len Min'],
        'Bwd Pkt Len Mean': data['Bwd Pkt Len Mean'],
        'Bwd Pkt Len Std': data['Bwd Pkt Len Std'],
        'Flow Byts/s': data['Flow Byts/s'],
        'Flow Pkts/s': data['Flow Pkts/s'],
        'Flow IAT Mean': data['Flow IAT Mean'],
        'Flow IAT Std': data['Flow IAT Std'],
        'Flow IAT Max': data['Flow IAT Max'],
        'Flow IAT Min': data['Flow IAT Min'],
        'Fwd IAT Tot': data['Fwd IAT Tot'],
        'Fwd IAT Mean': data['Fwd IAT Mean'],
        'Fwd IAT Std': data['Fwd IAT Std'],
        'Fwd IAT Max': data['Fwd IAT Max'],
        'Fwd IAT Min': data['Fwd IAT Min'],
        'Bwd IAT Tot': data['Bwd IAT Tot'],
        'Bwd IAT Mean': data['Bwd IAT Mean'],
        'Bwd IAT Std': data['Bwd IAT Std'],
        'Bwd IAT Max': data['Bwd IAT Max'],
        'Bwd IAT Min': data['Bwd IAT Min'],
        'Fwd PSH Flags': data['Fwd PSH Flags'],
        'Bwd PSH Flags': data['Bwd PSH Flags'],
        'Fwd URG Flags': data['Fwd URG Flags'],
        'Bwd URG Flags': data['Bwd URG Flags'],
        'Fwd Header Len': data['Fwd Header Len'],
        'Bwd Header Len': data['Bwd Header Len'],
        'Fwd Pkts/s': data['Fwd Pkts/s'],
        'Bwd Pkts/s': data['Bwd Pkts/s'],
        'Pkt Len Min': data['Pkt Len Min'],
        'Pkt Len Max': data['Pkt Len Max'],
        'Pkt Len Mean': data['Pkt Len Mean'],
        'Pkt Len Std': data['Pkt Len Std'],
        'Pkt Len Var': data['Pkt Len Var'],
        'FIN Flag Cnt': data['FIN Flag Cnt'],
        'SYN Flag Cnt': data['SYN Flag Cnt'],
        'RST Flag Cnt': data['RST Flag Cnt'],
        'PSH Flag Cnt': data['PSH Flag Cnt'],
        'ACK Flag Cnt': data['ACK Flag Cnt'],
        'URG Flag Cnt': data['URG Flag Cnt'],
        'CWE Flag Count': data['CWE Flag Count'],
        'ECE Flag Cnt': data['ECE Flag Cnt'],
        'Down/Up Ratio': data['Down/Up Ratio'],
        'Pkt Size Avg': data['Pkt Size Avg'],
        'Fwd Seg Size Avg': data['Fwd Seg Size Avg'],
        'Bwd Seg Size Avg': data['Bwd Seg Size Avg'],
        'Fwd Byts/b Avg': data['Fwd Byts/b Avg'],
        'Fwd Pkts/b Avg': data['Fwd Pkts/b Avg'],
        'Fwd Blk Rate Avg': data['Fwd Blk Rate Avg'],
        'Bwd Byts/b Avg': data['Bwd Byts/b Avg'],
        'Bwd Pkts/b Avg': data['Bwd Pkts/b Avg'],
        'Bwd Blk Rate Avg': data['Bwd Blk Rate Avg'],
        'Subflow Fwd Pkts': data['Subflow Fwd Pkts'],
        'Subflow Fwd Byts': data['Subflow Fwd Byts'],
        'Subflow Bwd Pkts': data['Subflow Bwd Pkts'],
        'Subflow Bwd Byts': data['Subflow Bwd Byts'],
        'Init Fwd Win Byts': data['Init Fwd Win Byts'],
        'Init Bwd Win Byts': data['Init Bwd Win Byts'],
        'Fwd Act Data Pkts': data['Fwd Act Data Pkts'],
        'Fwd Seg Size Min': data['Fwd Seg Size Min'],
        'Active Mean': data['Active Mean'],
        'Active Std': data['Active Std'],
        'Active Max': data['Active Max'],
        'Active Min': data['Active Min'],
        'Idle Mean': data['Idle Mean'],
        'Idle Std': data['Idle Std'],
        'Idle Max': data['Idle Max'],
        'Idle Min': data['Idle Min'],
        # 'Label': data['Label']  # Include the label for attack indication
    }
    return features

def analyze_with_llm(features, model="o3-mini"):
    # Prepare the prompt for the LLM
    prompt = f"Analyze the following network traffic features and determine if they indicate an attack:\n{features}\nIs this an attack?"
    
    # Call the OpenAI API using the specified model
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    # Extract the response
    result = response['choices'][0]['message']['content']
    return result

def analyze_and_visualize_data(df: pd.DataFrame):
    """Analyze and visualize the processed data."""
    try:
        logger.info("Starting data analysis and visualization...")
        visualizer = NetworkTrafficVisualizer()
        
        # Plot attack distribution
        logger.info("Generating attack distribution plot...")
        visualizer.plot_attack_distribution(df)
        
        # Plot feature correlations
        logger.info("Generating feature correlation plot...")
        visualizer.plot_feature_correlations(df)
        
        # Plot feature importance using PCA
        logger.info("Generating PCA analysis plots...")
        visualizer.plot_feature_importance(df)
        
        # Plot missing values distribution
        logger.info("Generating missing values plot...")
        visualizer.plot_missing_values(df)
        
        logger.info("Data analysis and visualization completed successfully")
        
    except Exception as e:
        logger.error(f"Error in data analysis and visualization: {str(e)}")
        raise

def main():
    """Main function to run the InSDN traffic analysis pipeline."""
    logger.info("Starting InSDN Traffic Analysis...")
    
    try:
        # Load configuration
        config = load_config()
        
        # Initialize preprocessor
        preprocessor_config = config.get('preprocessing', {})
        preprocessor = DataPreprocessor(preprocessor_config)
        
        # Download and process dataset
        dataset_path = download_dataset()
        processed_data = load_and_process_data(dataset_path, preprocessor)
        
        # Save processed data
        output_dir = Path('data/processed')
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / 'processed_network_traffic.csv'
        processed_data.to_csv(output_file, index=False)
        
        logger.info(f"Successfully processed data. Shape: {processed_data.shape}")
        logger.info(f"Processed data saved to: {output_file}")
        
        # Analyze and visualize the data
        analyze_and_visualize_data(processed_data)
        
        # Compare specific features between normal and attack traffic
        features_to_compare = ['Packet_Length', 'Flow_Duration', 'Bytes_per_Second']
        visualizer = NetworkTrafficVisualizer()
        for feature in features_to_compare:
            logger.info(f"Comparing feature: {feature}")
            visualizer.plot_feature_comparison(processed_data, feature)
        
        # Display sample statistics
        logger.info("\nProcessed Data Statistics:")
        logger.info("\nNumerical Features:")
        numerical_stats = processed_data.describe()
        for col in numerical_stats.columns:
            logger.info(f"\n{col}:")
            logger.info(numerical_stats[col].to_string())
        
        logger.info("\nCategorical Features:")
        categorical_cols = processed_data.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            logger.info(f"\n{col}:")
            logger.info(processed_data[col].value_counts().to_string())
        
    except Exception as e:
        logger.error(f"Error in main pipeline: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main()
