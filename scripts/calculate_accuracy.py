import json
import os
import pandas as pd
from glob import glob
import logging

logging.basicConfig(level=logging.INFO)

def load_latest_verification_results():
    """Load the most recent verification results."""
    reports_dir = 'reports'
    verification_dirs = glob(os.path.join(reports_dir, 'attack_verification_*'))
    if not verification_dirs:
        raise FileNotFoundError("No verification results found")
    
    # Get the most recent directory
    latest_dir = max(verification_dirs, key=os.path.getctime)
    summary_file = os.path.join(latest_dir, 'verification_summary.json')
    
    with open(summary_file, 'r') as f:
        return json.load(f), latest_dir

def load_actual_labels(data_path):
    """Load actual labels from the dataset."""
    df = pd.read_csv(data_path)
    # Convert labels to binary (attack/normal)
    df['is_attack'] = df['Label'].apply(lambda x: 0 if x.lower() == 'normal' else 1)
    return df

def calculate_accuracy_metrics(predictions, actual_labels):
    """Calculate accuracy metrics."""
    total = len(predictions)
    correct = 0
    true_positives = 0
    true_negatives = 0
    false_positives = 0
    false_negatives = 0
    
    for pred, actual in zip(predictions, actual_labels):
        if pred == actual:
            correct += 1
            if pred == 1:
                true_positives += 1
            else:
                true_negatives += 1
        else:
            if pred == 1:
                false_positives += 1
            else:
                false_negatives += 1
    
    accuracy = (correct / total) * 100 if total > 0 else 0
    precision = (true_positives / (true_positives + false_positives)) * 100 if (true_positives + false_positives) > 0 else 0
    recall = (true_positives / (true_positives + false_negatives)) * 100 if (true_positives + false_negatives) > 0 else 0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    return {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1_score': f1_score,
        'confusion_matrix': {
            'true_positives': true_positives,
            'true_negatives': true_negatives,
            'false_positives': false_positives,
            'false_negatives': false_negatives
        }
    }

def analyze_attack_types(predictions, actual_labels):
    """Analyze accuracy for different attack types."""
    attack_type_accuracy = {}
    for pred_type, actual_type in zip(predictions, actual_labels):
        if actual_type not in attack_type_accuracy:
            attack_type_accuracy[actual_type] = {'correct': 0, 'total': 0}
        
        attack_type_accuracy[actual_type]['total'] += 1
        if pred_type == actual_type:
            attack_type_accuracy[actual_type]['correct'] += 1
    
    # Calculate percentages
    for attack_type in attack_type_accuracy:
        total = attack_type_accuracy[attack_type]['total']
        correct = attack_type_accuracy[attack_type]['correct']
        accuracy = (correct / total) * 100 if total > 0 else 0
        attack_type_accuracy[attack_type]['accuracy'] = accuracy
    
    return attack_type_accuracy

def main():
    try:
        # Load verification results
        results, latest_dir = load_latest_verification_results()
        logging.info(f"Analyzing results from: {latest_dir}")
        
        # Load actual labels
        data_path = 'data/processed/test_data.csv'
        df = load_actual_labels(data_path)
        
        # Extract predictions and actual labels
        predictions = []
        actual_labels = []
        
        for result in results['detailed_results']:
            sample_index = result['sample_index']
            # Get actual label
            actual_label = df.iloc[sample_index]['is_attack']
            actual_labels.append(actual_label)
            
            # Get prediction
            metrics = result['metrics']
            # Consider it an attack if confidence > 50%
            is_attack_prediction = 1 if metrics['malicious_confidence'] and metrics['malicious_confidence'] > 50 else 0
            predictions.append(is_attack_prediction)
        
        # Calculate metrics
        metrics = calculate_accuracy_metrics(predictions, actual_labels)
        
        # Print results
        logging.info("\n=== Accuracy Analysis ===")
        logging.info(f"Overall Accuracy: {metrics['accuracy']:.2f}%")
        logging.info(f"Precision: {metrics['precision']:.2f}%")
        logging.info(f"Recall: {metrics['recall']:.2f}%")
        logging.info(f"F1 Score: {metrics['f1_score']:.2f}%")
        
        logging.info("\nConfusion Matrix:")
        logging.info(f"True Positives: {metrics['confusion_matrix']['true_positives']}")
        logging.info(f"True Negatives: {metrics['confusion_matrix']['true_negatives']}")
        logging.info(f"False Positives: {metrics['confusion_matrix']['false_positives']}")
        logging.info(f"False Negatives: {metrics['confusion_matrix']['false_negatives']}")
        
        # Save detailed analysis
        output_file = os.path.join(latest_dir, 'accuracy_analysis.json')
        with open(output_file, 'w') as f:
            json.dump(metrics, f, indent=2)
        logging.info(f"\nDetailed analysis saved to: {output_file}")
        
    except Exception as e:
        logging.error(f"Error calculating accuracy: {str(e)}")
        raise

if __name__ == "__main__":
    main() 