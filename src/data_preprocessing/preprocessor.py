"""
Data preprocessing module for InSDN traffic analysis.
Handles data cleaning, normalization, and feature preparation.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any
import logging
from sklearn.preprocessing import StandardScaler, LabelEncoder

logger = logging.getLogger(__name__)

class DataPreprocessor:
    """Handles preprocessing of network traffic data."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the preprocessor with configuration parameters.
        
        Args:
            config: Dictionary containing preprocessing parameters
        """
        self.config = config
        self.numerical_scaler = StandardScaler()
        self.label_encoders = {}
        logger.info("Initialized DataPreprocessor")
    
    def load_data(self, file_path: str) -> pd.DataFrame:
        """
        Load raw data from the specified path.
        
        Args:
            file_path: Path to the raw data file
            
        Returns:
            DataFrame containing the loaded data
        """
        try:
            data = pd.read_csv(file_path)
            logger.info(f"Successfully loaded data from {file_path} with shape {data.shape}")
            return data
        except Exception as e:
            logger.error(f"Error loading data from {file_path}: {str(e)}")
            raise
    
    def clean_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Clean the raw data by handling missing values and outliers.
        
        Args:
            data: Raw DataFrame to clean
            
        Returns:
            Cleaned DataFrame
        """
        try:
            # Make a copy to avoid modifying the original data
            cleaned_data = data.copy()
            
            # Convert all numerical columns to float64 to avoid dtype issues
            numerical_cols = cleaned_data.select_dtypes(include=['int64', 'float64']).columns
            for col in numerical_cols:
                cleaned_data[col] = cleaned_data[col].astype('float64')
            
            # Handle missing values
            if self.config.get('handle_missing', True):
                # For numerical columns, fill with median
                for col in numerical_cols:
                    median_value = cleaned_data[col].median()
                    cleaned_data[col] = cleaned_data[col].fillna(median_value)
                
                # For categorical columns, fill with mode
                categorical_cols = cleaned_data.select_dtypes(include=['object']).columns
                for col in categorical_cols:
                    mode_value = cleaned_data[col].mode()[0]
                    cleaned_data[col] = cleaned_data[col].fillna(mode_value)
            
            # Remove duplicates if configured
            if self.config.get('remove_duplicates', True):
                initial_rows = len(cleaned_data)
                cleaned_data = cleaned_data.drop_duplicates()
                dropped_rows = initial_rows - len(cleaned_data)
                logger.info(f"Removed {dropped_rows} duplicate rows")
            
            # Handle outliers using IQR method if configured
            if self.config.get('handle_outliers', True):
                outlier_threshold = self.config.get('outlier_threshold', 3.0)
                
                for col in numerical_cols:
                    Q1 = cleaned_data[col].quantile(0.25)
                    Q3 = cleaned_data[col].quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - outlier_threshold * IQR
                    upper_bound = Q3 + outlier_threshold * IQR
                    
                    # Replace outliers with bounds
                    cleaned_data.loc[cleaned_data[col] < lower_bound, col] = lower_bound
                    cleaned_data.loc[cleaned_data[col] > upper_bound, col] = upper_bound
            
            logger.info(f"Successfully cleaned data, new shape: {cleaned_data.shape}")
            return cleaned_data
            
        except Exception as e:
            logger.error(f"Error cleaning data: {str(e)}")
            raise
    
    def normalize_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize numerical features and encode categorical variables.
        
        Args:
            data: DataFrame with features to normalize
            
        Returns:
            DataFrame with normalized features
        """
        try:
            normalized_data = data.copy()
            
            # Normalize numerical features using StandardScaler
            numerical_cols = normalized_data.select_dtypes(include=['float64']).columns
            if len(numerical_cols) > 0:
                # Fit and transform the data
                scaled_data = self.numerical_scaler.fit_transform(normalized_data[numerical_cols])
                
                # Convert back to DataFrame and verify statistics
                scaled_df = pd.DataFrame(scaled_data, columns=numerical_cols, index=normalized_data.index)
                
                # Ensure exact mean=0 and std=1
                for col in numerical_cols:
                    scaled_df[col] = (scaled_df[col] - scaled_df[col].mean()) / scaled_df[col].std()
                
                normalized_data[numerical_cols] = scaled_df
            
            # Encode categorical features
            categorical_cols = normalized_data.select_dtypes(include=['object']).columns
            for col in categorical_cols:
                if col not in self.label_encoders:
                    self.label_encoders[col] = LabelEncoder()
                normalized_data[col] = self.label_encoders[col].fit_transform(normalized_data[col].astype(str))
            
            logger.info(f"Successfully normalized features. Numerical columns: {len(numerical_cols)}, Categorical columns: {len(categorical_cols)}")
            return normalized_data
            
        except Exception as e:
            logger.error(f"Error normalizing features: {str(e)}")
            raise
    
    def process(self, file_path: str) -> pd.DataFrame:
        """
        Execute the complete preprocessing pipeline.
        
        Args:
            file_path: Path to the raw data file
            
        Returns:
            Processed DataFrame ready for analysis
        """
        try:
            logger.info("Starting preprocessing pipeline...")
            
            # Load data
            data = self.load_data(file_path)
            logger.info(f"Loaded data with shape: {data.shape}")
            
            # Clean data
            data = self.clean_data(data)
            logger.info(f"Cleaned data shape: {data.shape}")
            
            # Normalize features
            data = self.normalize_features(data)
            logger.info(f"Normalized data shape: {data.shape}")
            
            logger.info("Successfully completed preprocessing pipeline")
            return data
            
        except Exception as e:
            logger.error(f"Error in preprocessing pipeline: {str(e)}")
            raise
