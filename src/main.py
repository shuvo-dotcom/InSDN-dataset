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
from data_preprocessing.preprocessor import DataPreprocessor

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

def main():
    """Main function to run the InSDN traffic analysis pipeline."""
    logger.info("Starting InSDN Traffic Analysis...")
    
    try:
        # Load configuration
        config = load_config()
        
        # Initialize preprocessor
        preprocessor_config = config.get('preprocessing', {})
        preprocessor = DataPreprocessor(preprocessor_config)
        
        # Process sample data
        input_file = 'data/raw/sample_network_traffic.csv'
        processed_data = preprocessor.process(input_file)
        
        # Save processed data
        output_file = 'data/processed/processed_network_traffic.csv'
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        processed_data.to_csv(output_file, index=False)
        
        logger.info(f"Successfully processed data. Shape: {processed_data.shape}")
        logger.info(f"Processed data saved to: {output_file}")
        
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
