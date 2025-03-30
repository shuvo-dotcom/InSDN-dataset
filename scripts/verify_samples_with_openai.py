import os
import pandas as pd
import numpy as np
from openai import OpenAI
import json
import logging
from datetime import datetime
from openai import OpenAIError
from tqdm import tqdm
import re
import time

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/openai_sample_verification.log'),
        logging.StreamHandler()
    ]
)

def load_config():
    """Load configuration from config.json file."""
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        if not config.get('openai_api_key'):
            raise ValueError("OpenAI API key not found in config.json")
        return config
    except FileNotFoundError:
        logging.error("config.json file not found. Please create it with your OpenAI API key.")
        raise
    except json.JSONDecodeError:
        logging.error("Invalid JSON format in config.json file.")
        raise

def load_data(real_data_path, synthetic_data_path, sample_size=100):
    """Load both real and synthetic data, and select random samples."""
    try:
        # Read data with error handling
        logging.info(f"Loading real data from {real_data_path}")
        real_data = pd.read_csv(real_data_path, on_bad_lines='skip')
        logging.info(f"Loading synthetic data from {synthetic_data_path}")
        synthetic_data = pd.read_csv(synthetic_data_path, on_bad_lines='skip')
        
        # Log data info
        logging.info(f"Real data shape: {real_data.shape}")
        logging.info(f"Synthetic data shape: {synthetic_data.shape}")
        logging.info(f"Real data columns: {real_data.columns.tolist()}")
        logging.info(f"Synthetic data columns: {synthetic_data.columns.tolist()}")
        
        # Ensure both datasets have the same columns
        common_columns = list(set(real_data.columns) & set(synthetic_data.columns))
        if not common_columns:
            raise ValueError("No common columns found between real and synthetic data")
        
        real_data = real_data[common_columns]
        synthetic_data = synthetic_data[common_columns]
        
        # Convert to numeric, coercing errors to NaN
        real_data = real_data.apply(pd.to_numeric, errors='coerce')
        synthetic_data = synthetic_data.apply(pd.to_numeric, errors='coerce')
        
        # Select random samples
        if len(real_data) > sample_size:
            real_indices = np.random.choice(len(real_data), sample_size, replace=False)
            real_samples = real_data.iloc[real_indices]
            synthetic_samples = synthetic_data.iloc[real_indices]
        else:
            real_samples = real_data
            synthetic_samples = synthetic_data
        
        logging.info(f"Selected {len(real_samples)} samples for verification")
        return real_samples, synthetic_samples
    except Exception as e:
        logging.error(f"Error loading data: {str(e)}")
        raise

def prepare_sample_verification_prompt(real_sample, synthetic_sample, feature_metrics=None):
    """Prepare a prompt for verifying a single sample."""
    try:
        # Convert samples to dictionaries for better formatting
        real_dict = real_sample.to_dict()
        synthetic_dict = synthetic_sample.to_dict()
        
        # Calculate differences
        differences = {}
        for key in real_dict.keys():
            if isinstance(real_dict[key], (int, float)) and isinstance(synthetic_dict[key], (int, float)):
                diff = abs(real_dict[key] - synthetic_dict[key])
                if real_dict[key] != 0:
                    diff_percent = (diff / abs(real_dict[key])) * 100
                else:
                    diff_percent = 100 if diff != 0 else 0
                differences[key] = {
                    'real_value': real_dict[key],
                    'synthetic_value': synthetic_dict[key],
                    'absolute_difference': diff,
                    'percentage_difference': diff_percent
                }
        
        prompt = f"""As a network traffic analysis expert, verify the following synthetic network traffic sample against its real counterpart.

Real Sample:
{json.dumps(real_dict, indent=2)}

Synthetic Sample:
{json.dumps(synthetic_dict, indent=2)}

Feature-wise Differences:
{json.dumps(differences, indent=2)}

Please provide a detailed analysis including:

1. Overall Quality Assessment
- Is this synthetic sample a good representation of the real sample?
- What is the overall accuracy score (0-100)?
- Are there any significant discrepancies?

2. Feature-specific Analysis
- Which features are accurately generated?
- Which features show significant deviation?
- Are the deviations acceptable for network traffic analysis?

3. Practical Implications
- Would this synthetic sample be suitable for:
  * Network traffic analysis
  * Anomaly detection
  * Security testing
  * Training purposes
- What are the potential risks or limitations?

4. Recommendations
- What improvements could be made?
- Are there specific features that need attention?
- Should this sample be included in the final dataset?

Please provide numerical scores and specific examples where relevant."""
        
        return prompt
    except Exception as e:
        logging.error(f"Error preparing verification prompt: {str(e)}")
        raise

def verify_sample_with_openai(client, real_sample, synthetic_sample, feature_metrics=None):
    """Verify a single sample using OpenAI."""
    try:
        # Prepare prompt
        prompt = prepare_sample_verification_prompt(real_sample, synthetic_sample, feature_metrics)
        
        # Get OpenAI analysis
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are an expert in network traffic analysis and data verification. Focus on providing precise numerical metrics and practical implications."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2000
        )
        
        return response.choices[0].message.content
    except OpenAIError as e:
        logging.error(f"OpenAI API error: {str(e)}")
        raise

def extract_accuracy_score(analysis_text):
    """Extract accuracy score from the analysis text."""
    try:
        # Look for accuracy score in the text
        accuracy_pattern = r"accuracy score.*?(\d+)"
        match = re.search(accuracy_pattern, analysis_text.lower())
        if match:
            return int(match.group(1))
        return None
    except Exception as e:
        logging.error(f"Error extracting accuracy score: {str(e)}")
        return None

def extract_feature_accuracy(analysis_text):
    """Extract feature-specific accuracy information."""
    try:
        # Look for feature-specific information
        features = {}
        feature_pattern = r"([a-zA-Z_]+).*?(\d+)%"
        matches = re.finditer(feature_pattern, analysis_text.lower())
        for match in matches:
            feature = match.group(1)
            accuracy = int(match.group(2))
            features[feature] = accuracy
        return features
    except Exception as e:
        logging.error(f"Error extracting feature accuracy: {str(e)}")
        return {}

def verify_samples_with_openai(real_data_path, synthetic_data_path, sample_size=100):
    """Verify multiple samples using OpenAI."""
    try:
        # Load configuration
        config = load_config()
        logging.info("Configuration loaded successfully")
        
        # Initialize OpenAI client
        client = OpenAI(api_key=config['openai_api_key'])
        logging.info("OpenAI client initialized")
        
        # Load data
        real_samples, synthetic_samples = load_data(real_data_path, synthetic_data_path, sample_size)
        
        # Create results directory if it doesn't exist
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_dir = f'reports/sample_verification_{timestamp}'
        os.makedirs(results_dir, exist_ok=True)
        
        # Initialize results storage
        all_results = []
        accuracy_summary = {
            'overall_accuracy': [],
            'feature_accuracy': {},
            'sample_details': []
        }
        
        # Process each sample
        for idx in tqdm(range(len(real_samples)), desc="Verifying samples"):
            try:
                # Get verification for this sample
                analysis = verify_sample_with_openai(
                    client,
                    real_samples.iloc[idx],
                    synthetic_samples.iloc[idx]
                )
                
                # Extract accuracy metrics
                accuracy_score = extract_accuracy_score(analysis)
                feature_accuracy = extract_feature_accuracy(analysis)
                
                # Save individual analysis
                sample_result = {
                    'sample_index': idx,
                    'analysis': analysis,
                    'accuracy_score': accuracy_score,
                    'feature_accuracy': feature_accuracy,
                    'timestamp': datetime.now().strftime("%Y%m%d_%H%M%S")
                }
                
                # Update accuracy summary
                if accuracy_score is not None:
                    accuracy_summary['overall_accuracy'].append(accuracy_score)
                
                for feature, acc in feature_accuracy.items():
                    if feature not in accuracy_summary['feature_accuracy']:
                        accuracy_summary['feature_accuracy'][feature] = []
                    accuracy_summary['feature_accuracy'][feature].append(acc)
                
                accuracy_summary['sample_details'].append({
                    'sample_index': idx,
                    'accuracy_score': accuracy_score,
                    'feature_accuracy': feature_accuracy
                })
                
                # Save to file
                with open(f'{results_dir}/sample_{idx}_analysis.txt', 'w') as f:
                    f.write(analysis)
                
                all_results.append(sample_result)
                
                # Add a small delay to avoid rate limits
                time.sleep(1)
                
            except Exception as e:
                logging.error(f"Error processing sample {idx}: {str(e)}")
                continue
        
        # Calculate average accuracies
        if accuracy_summary['overall_accuracy']:
            accuracy_summary['average_overall_accuracy'] = sum(accuracy_summary['overall_accuracy']) / len(accuracy_summary['overall_accuracy'])
        
        for feature in accuracy_summary['feature_accuracy']:
            if accuracy_summary['feature_accuracy'][feature]:
                accuracy_summary['feature_accuracy'][feature] = {
                    'values': accuracy_summary['feature_accuracy'][feature],
                    'average': sum(accuracy_summary['feature_accuracy'][feature]) / len(accuracy_summary['feature_accuracy'][feature])
                }
        
        # Save summary
        summary = {
            'timestamp': timestamp,
            'total_samples': len(real_samples),
            'successful_verifications': len(all_results),
            'sample_results': all_results,
            'accuracy_summary': accuracy_summary
        }
        
        with open(f'{results_dir}/verification_summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        # Print accuracy summary
        logging.info("\nAccuracy Summary:")
        logging.info(f"Average Overall Accuracy: {accuracy_summary.get('average_overall_accuracy', 'N/A')}")
        logging.info("\nFeature-wise Average Accuracy:")
        for feature, data in accuracy_summary['feature_accuracy'].items():
            logging.info(f"{feature}: {data['average']:.2f}%")
        
        logging.info(f"\nSample verification completed. Results saved to {results_dir}")
        return summary
        
    except Exception as e:
        logging.error(f"Error in sample verification: {str(e)}")
        raise

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--real_data', type=str, default='data/processed/test_data.csv')
    parser.add_argument('--synthetic_data', type=str, default='data/processed/synthetic_data.csv')
    parser.add_argument('--sample_size', type=int, default=20)  # Changed default to 20
    args = parser.parse_args()
    
    verify_samples_with_openai(args.real_data, args.synthetic_data, args.sample_size) 