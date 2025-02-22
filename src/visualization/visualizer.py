"""
Visualization module for InSDN Traffic Analysis.
Provides functions to visualize network traffic patterns and attack distributions.
"""

import logging
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)

class NetworkTrafficVisualizer:
    def __init__(self, output_dir: str = 'experiments/visualizations'):
        """Initialize the visualizer with output directory."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def plot_attack_distribution(self, df: pd.DataFrame, save: bool = True):
        """Plot the distribution of attack types."""
        plt.figure(figsize=(12, 6))
        attack_counts = df['Label'].value_counts().sort_index()
        
        # Map numeric labels to attack types
        label_mapping = {
            0: 'Normal',
            1: 'DoS',
            2: 'Probe',
            3: 'R2L',
            4: 'U2R',
            5: 'Unknown'
        }
        
        attack_counts.index = attack_counts.index.map(label_mapping)
        sns.barplot(x=attack_counts.index, y=attack_counts.values)
        plt.title('Distribution of Network Traffic Types')
        plt.xlabel('Traffic Type')
        plt.ylabel('Number of Instances')
        plt.xticks(rotation=45)
        
        if save:
            plt.savefig(self.output_dir / 'attack_distribution.png', bbox_inches='tight')
            logger.info(f"Saved attack distribution plot to {self.output_dir / 'attack_distribution.png'}")
        plt.close()
    
    def plot_feature_correlations(self, df: pd.DataFrame, n_features: int = 15, save: bool = True):
        """Plot correlation matrix of top n most correlated features."""
        # Select only numeric columns
        numeric_df = df.select_dtypes(include=[np.number])
        
        # Calculate correlation matrix
        corr_matrix = numeric_df.corr()
        
        # Get the most correlated features
        correlations = {}
        for i in range(len(corr_matrix.columns)):
            for j in range(i):
                if abs(corr_matrix.iloc[i, j]) > 0.5:  # Correlation threshold
                    correlations[f"{corr_matrix.columns[i]}_{corr_matrix.columns[j]}"] = abs(corr_matrix.iloc[i, j])
        
        # Sort correlations and get top n
        top_correlations = dict(sorted(correlations.items(), key=lambda x: x[1], reverse=True)[:n_features])
        
        # Create correlation plot
        plt.figure(figsize=(12, 8))
        plt.bar(range(len(top_correlations)), list(top_correlations.values()))
        plt.xticks(range(len(top_correlations)), list(top_correlations.keys()), rotation=90)
        plt.title(f'Top {n_features} Feature Correlations')
        plt.xlabel('Feature Pairs')
        plt.ylabel('Absolute Correlation')
        
        if save:
            plt.savefig(self.output_dir / 'feature_correlations.png', bbox_inches='tight')
            logger.info(f"Saved feature correlations plot to {self.output_dir / 'feature_correlations.png'}")
        plt.close()
    
    def plot_feature_importance(self, df: pd.DataFrame, n_components: int = 2, save: bool = True):
        """Plot feature importance using PCA."""
        # Select only numeric columns with no missing values
        numeric_df = df.select_dtypes(include=[np.number])
        numeric_df = numeric_df.dropna(axis=1)
        
        # Standardize the features
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(numeric_df)
        
        # Apply PCA
        pca = PCA(n_components=n_components)
        pca_result = pca.fit_transform(scaled_data)
        
        # Plot explained variance ratio
        plt.figure(figsize=(10, 6))
        plt.plot(range(1, n_components + 1), np.cumsum(pca.explained_variance_ratio_), 'bo-')
        plt.title('Cumulative Explained Variance Ratio vs Number of Components')
        plt.xlabel('Number of Components')
        plt.ylabel('Cumulative Explained Variance Ratio')
        
        if save:
            plt.savefig(self.output_dir / 'pca_variance.png', bbox_inches='tight')
            logger.info(f"Saved PCA variance plot to {self.output_dir / 'pca_variance.png'}")
        plt.close()
        
        # Plot feature loadings
        plt.figure(figsize=(12, 6))
        loadings = pd.DataFrame(
            pca.components_.T,
            columns=[f'PC{i+1}' for i in range(n_components)],
            index=numeric_df.columns
        )
        sns.heatmap(loadings, cmap='coolwarm', center=0)
        plt.title('PCA Feature Loadings')
        
        if save:
            plt.savefig(self.output_dir / 'pca_loadings.png', bbox_inches='tight')
            logger.info(f"Saved PCA loadings plot to {self.output_dir / 'pca_loadings.png'}")
        plt.close()
    
    def plot_missing_values(self, df: pd.DataFrame, save: bool = True):
        """Plot the percentage of missing values for each feature."""
        missing_percentages = (df.isnull().sum() / len(df) * 100).sort_values(ascending=False)
        missing_percentages = missing_percentages[missing_percentages > 0]
        
        if len(missing_percentages) > 0:
            plt.figure(figsize=(12, 6))
            sns.barplot(x=missing_percentages.index, y=missing_percentages.values)
            plt.title('Percentage of Missing Values by Feature')
            plt.xlabel('Features')
            plt.ylabel('Percentage Missing')
            plt.xticks(rotation=90)
            
            if save:
                plt.savefig(self.output_dir / 'missing_values.png', bbox_inches='tight')
                logger.info(f"Saved missing values plot to {self.output_dir / 'missing_values.png'}")
            plt.close()
        else:
            logger.info("No missing values found in the dataset")
    
    def plot_feature_comparison(self, df: pd.DataFrame, feature: str, save: bool = True):
        """Plot comparison of a specific feature between normal and attack traffic."""
        try:
            plt.figure(figsize=(12, 6))
            sns.boxplot(x='Label', y='Fwd Pkt Len Mean', data=df)
            plt.title(f'Comparison of {feature} Between Normal and Attack Traffic')
            plt.xlabel('Traffic Type')
            plt.ylabel(feature)
            plt.xticks(rotation=45)
            
            if save:
                plt.savefig(self.output_dir / f'{feature}_comparison.png', bbox_inches='tight')
                logger.info(f"Saved {feature} comparison plot to {self.output_dir / f'{feature}_comparison.png'}")
            plt.close()
        except Exception as e:
            logger.error(f"Error plotting feature comparison: {str(e)}")
            raise
