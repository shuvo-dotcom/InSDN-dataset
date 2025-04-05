import json
import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from glob import glob

def load_verification_results(results_dir):
    """Load verification results from JSON files."""
    results = []
    for file in glob(os.path.join(results_dir, 'results.json')):
        try:
            # Read the file in chunks
            with open(file, 'r') as f:
                content = ''
                for line in f:
                    if line.strip().startswith('{'):
                        try:
                            result = json.loads(line.strip().rstrip(','))
                            results.append(result)
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            print(f"Error reading file {file}: {str(e)}")
            continue
    return results

def extract_accuracy_metrics(results):
    """Extract accuracy metrics from results."""
    scores = []
    confidences = []
    severities = []
    
    for result in results:
        if isinstance(result, dict):
            # Extract score from key_indicators
            for indicator in result.get('key_indicators', []):
                if isinstance(indicator, str):
                    if 'Score:' in indicator:
                        try:
                            score = float(indicator.split(':')[1].strip())
                            scores.append(score)
                        except (ValueError, IndexError):
                            continue
                    elif 'GAN confidence:' in indicator:
                        try:
                            confidence = float(indicator.split(':')[1].strip())
                            confidences.append(confidence)
                        except (ValueError, IndexError):
                            continue
            
            # Extract severity
            severity = result.get('severity')
            if severity:
                severities.append(severity)
    
    return {
        'scores': scores,
        'confidences': confidences,
        'severities': severities
    }

def plot_accuracy_metrics(metrics, save_dir='reports/accuracy_visualization'):
    """Plot accuracy metrics."""
    os.makedirs(save_dir, exist_ok=True)
    
    # Set style
    plt.style.use('default')
    sns.set_theme()
    
    # Plot 1: Score Distribution
    if metrics['scores']:
        plt.figure(figsize=(10, 6))
        sns.histplot(data=metrics['scores'], bins=50, kde=True)
        plt.title('Distribution of Detection Scores')
        plt.xlabel('Score')
        plt.ylabel('Count')
        plt.savefig(os.path.join(save_dir, 'score_distribution.png'))
        plt.close()
    
    # Plot 2: Confidence vs Score
    if metrics['confidences'] and metrics['scores']:
        plt.figure(figsize=(10, 6))
        plt.scatter(metrics['confidences'], metrics['scores'], alpha=0.5)
        plt.title('GAN Confidence vs Detection Score')
        plt.xlabel('GAN Confidence')
        plt.ylabel('Detection Score')
        plt.savefig(os.path.join(save_dir, 'confidence_vs_score.png'))
        plt.close()
    
    # Plot 3: Severity Distribution
    if metrics['severities']:
        plt.figure(figsize=(10, 6))
        severity_counts = {}
        for severity in metrics['severities']:
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        plt.bar(severity_counts.keys(), severity_counts.values())
        plt.title('Distribution of Attack Severities')
        plt.xlabel('Severity')
        plt.ylabel('Count')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join(save_dir, 'severity_distribution.png'))
        plt.close()
    
    # Plot 4: Score Boxplot by Severity
    if metrics['severities'] and metrics['scores']:
        plt.figure(figsize=(12, 6))
        severity_scores = {}
        for i, severity in enumerate(metrics['severities']):
            if i < len(metrics['scores']):
                if severity not in severity_scores:
                    severity_scores[severity] = []
                severity_scores[severity].append(metrics['scores'][i])
        
        if severity_scores:
            plt.boxplot([scores for scores in severity_scores.values()], 
                        labels=severity_scores.keys())
            plt.title('Score Distribution by Severity')
            plt.xlabel('Severity')
            plt.ylabel('Score')
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(os.path.join(save_dir, 'score_by_severity.png'))
            plt.close()

def main():
    # Find the most recent verification results directory
    verification_dirs = glob('reports/attack_verification_*')
    if not verification_dirs:
        print("No verification results found")
        return
    
    latest_dir = max(verification_dirs)
    print(f"Analyzing results from: {latest_dir}")
    
    # Load and process results
    results = load_verification_results(latest_dir)
    metrics = extract_accuracy_metrics(results)
    
    # Print summary statistics
    print("\nAccuracy Metrics Summary:")
    print(f"Number of samples: {len(metrics['scores'])}")
    if metrics['scores']:
        scores = np.array(metrics['scores'])
        high_scores = scores[scores >= 0.98]  # Scores >= 98%
        print(f"Average score: {np.mean(scores):.4f}")
        print(f"Median score: {np.median(scores):.4f}")
        print(f"Score standard deviation: {np.std(scores):.4f}")
        print(f"Maximum score: {np.max(scores):.4f}")
        print(f"Minimum score: {np.min(scores):.4f}")
        print(f"\nHigh Accuracy Analysis (>= 98%):")
        print(f"Number of high accuracy samples: {len(high_scores)}")
        print(f"Percentage of high accuracy samples: {(len(high_scores) / len(scores)) * 100:.2f}%")
    
    # Plot metrics
    plot_accuracy_metrics(metrics)
    print("\nVisualizations saved to reports/accuracy_visualization/")

if __name__ == "__main__":
    main() 