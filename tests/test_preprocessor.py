"""
Tests for the data preprocessing module.
"""

import pytest
import pandas as pd
import numpy as np
from src.data_preprocessing.preprocessor import DataPreprocessor

@pytest.fixture
def sample_config():
    """Fixture for test configuration."""
    return {
        'remove_duplicates': True,
        'handle_missing': True,
        'handle_outliers': True,
        'outlier_threshold': 3.0
    }

@pytest.fixture
def sample_data():
    """Fixture for sample test data."""
    return pd.DataFrame({
        'packet_length': [100, 200, 300, np.nan, 500, 1000000, 200],  # Added outlier and duplicate
        'flow_duration': [10, 20, 30, 40, 50, 60, 20],
        'protocol': ['TCP', 'UDP', 'TCP', None, 'UDP', 'HTTP', 'UDP'],
        'flow_type': ['normal', 'attack', 'normal', 'attack', 'normal', 'attack', 'attack']
    })

def test_preprocessor_initialization(sample_config):
    """Test if preprocessor initializes correctly."""
    preprocessor = DataPreprocessor(sample_config)
    assert preprocessor.config == sample_config
    assert hasattr(preprocessor, 'numerical_scaler')
    assert hasattr(preprocessor, 'label_encoders')

def test_data_loading(tmp_path, sample_data):
    """Test data loading functionality."""
    # Create a temporary CSV file
    file_path = tmp_path / "test_data.csv"
    sample_data.to_csv(file_path, index=False)
    
    preprocessor = DataPreprocessor({})
    loaded_data = preprocessor.load_data(str(file_path))
    
    assert isinstance(loaded_data, pd.DataFrame)
    assert len(loaded_data) == len(sample_data)
    assert all(loaded_data.columns == sample_data.columns)
    
    # Test error handling
    with pytest.raises(Exception):
        preprocessor.load_data("nonexistent_file.csv")

def test_data_cleaning(sample_config, sample_data):
    """Test data cleaning functionality."""
    preprocessor = DataPreprocessor(sample_config)
    cleaned_data = preprocessor.clean_data(sample_data)
    
    # Test missing value handling
    assert cleaned_data['packet_length'].isna().sum() == 0
    assert cleaned_data['protocol'].isna().sum() == 0
    
    # Test duplicate removal
    assert len(cleaned_data) < len(sample_data)
    
    # Test outlier handling
    max_packet_length = cleaned_data['packet_length'].max()
    assert max_packet_length < 1000000  # The outlier should have been capped
    
    # Verify data integrity
    assert isinstance(cleaned_data, pd.DataFrame)
    assert all(col in cleaned_data.columns for col in sample_data.columns)

def test_feature_normalization(sample_config, sample_data):
    """Test feature normalization functionality."""
    preprocessor = DataPreprocessor(sample_config)
    
    # First clean the data
    cleaned_data = preprocessor.clean_data(sample_data)
    
    # Then normalize
    normalized_data = preprocessor.normalize_features(cleaned_data)
    
    # Test numerical feature normalization
    numerical_cols = ['packet_length', 'flow_duration']
    for col in numerical_cols:
        assert normalized_data[col].mean() == pytest.approx(0, abs=1e-10)
        assert normalized_data[col].std() == pytest.approx(1, abs=1e-10)
    
    # Test categorical feature encoding
    categorical_cols = ['protocol', 'flow_type']
    for col in categorical_cols:
        assert normalized_data[col].dtype in [np.int32, np.int64]
        assert len(preprocessor.label_encoders[col].classes_) == len(cleaned_data[col].unique())

def test_complete_pipeline(tmp_path, sample_config, sample_data):
    """Test the complete preprocessing pipeline."""
    # Create a temporary CSV file
    file_path = tmp_path / "test_data.csv"
    sample_data.to_csv(file_path, index=False)
    
    preprocessor = DataPreprocessor(sample_config)
    processed_data = preprocessor.process(str(file_path))
    
    # Verify final output
    assert isinstance(processed_data, pd.DataFrame)
    assert len(processed_data) < len(sample_data)  # Due to duplicate removal
    assert all(col in processed_data.columns for col in sample_data.columns)
    assert processed_data.isna().sum().sum() == 0  # No missing values
    
    # Verify numerical features are normalized
    numerical_cols = ['packet_length', 'flow_duration']
    for col in numerical_cols:
        assert processed_data[col].mean() == pytest.approx(0, abs=1e-10)
        assert processed_data[col].std() == pytest.approx(1, abs=1e-10)
    
    # Verify categorical features are encoded
    categorical_cols = ['protocol', 'flow_type']
    for col in categorical_cols:
        assert processed_data[col].dtype in [np.int32, np.int64]

def test_config_variations(sample_data):
    """Test preprocessor with different configurations."""
    # Test with outlier handling disabled
    config_no_outliers = {
        'remove_duplicates': True,
        'handle_missing': True,
        'handle_outliers': False
    }
    preprocessor = DataPreprocessor(config_no_outliers)
    cleaned_data = preprocessor.clean_data(sample_data)
    assert cleaned_data['packet_length'].max() == 1000000  # Outlier should remain
    
    # Test with duplicate removal disabled
    config_keep_duplicates = {
        'remove_duplicates': False,
        'handle_missing': True,
        'handle_outliers': True
    }
    preprocessor = DataPreprocessor(config_keep_duplicates)
    cleaned_data = preprocessor.clean_data(sample_data)
    assert len(cleaned_data) == len(sample_data)  # No rows should be removed
