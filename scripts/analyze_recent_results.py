import json
import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from glob import glob
from collections import defaultdict

def process_results_file(file_path):
    """Process results file to extract scores."""
    scores = []
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            for result in data.get('results', []):
                for indicator in result.get('key_indicators', []):
                    if 'Score:' in indicator:
                        try:
                            score = float(indicator.split('Score:')[1].strip())
                            scores.append(score)
                        except (ValueError, IndexError):
                            continue
    except json.JSONDecodeError:
        print(f"Error decoding JSON in {file_path}")
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
    return scores

def analyze_scores(scores):
    """Analyze the distribution of scores."""
    if not scores:
        return None
    
    scores = np.array(scores)
    high_scores = scores[scores >= 0.98]
    
    return {
        'total_samples': len(scores),
        'high_accuracy_samples': len(high_scores),
        'high_accuracy_percentage': (len(high_scores) / len(scores)) * 100,
        'mean_score': np.mean(scores),
        'median_score': np.median(scores),
        'std_score': np.std(scores),
        'min_score': np.min(scores),
        'max_score': np.max(scores)
    }

def plot_accuracy_metrics(scores, save_dir='reports/recent_accuracy'):
    """Create visualizations for accuracy metrics."""
    os.makedirs(save_dir, exist_ok=True)
    
    # Set style
    plt.style.use('default')
    sns.set_theme()
    
    # Plot 1: Score Distribution
    plt.figure(figsize=(12, 6))
    sns.histplot(data=scores, bins=50, kde=True)
    plt.axvline(x=0.98, color='r', linestyle='--', label='98% Threshold')
    plt.title('Distribution of Recent Detection Scores')
    plt.xlabel('Score')
    plt.ylabel('Count')
    plt.legend()
    plt.savefig(os.path.join(save_dir, 'recent_score_distribution.png'))
    plt.close()
    
    # Plot 2: Score Range Distribution
    score_ranges = {
        '< 50%': len([s for s in scores if s < 0.5]),
        '50-70%': len([s for s in scores if 0.5 <= s < 0.7]),
        '70-90%': len([s for s in scores if 0.7 <= s < 0.9]),
        '90-98%': len([s for s in scores if 0.9 <= s < 0.98]),
        '≥ 98%': len([s for s in scores if s >= 0.98])
    }
    
    plt.figure(figsize=(10, 6))
    plt.bar(score_ranges.keys(), score_ranges.values())
    plt.title('Distribution of Recent Score Ranges')
    plt.xlabel('Score Range')
    plt.ylabel('Number of Samples')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, 'recent_score_ranges.png'))
    plt.close()
    
    # Plot 3: Cumulative Distribution
    plt.figure(figsize=(10, 6))
    sorted_scores = np.sort(scores)
    cumulative = np.arange(1, len(sorted_scores) + 1) / len(sorted_scores)
    plt.plot(sorted_scores, cumulative)
    plt.axvline(x=0.98, color='r', linestyle='--', label='98% Threshold')
    plt.title('Cumulative Distribution of Recent Scores')
    plt.xlabel('Score')
    plt.ylabel('Cumulative Proportion')
    plt.grid(True)
    plt.legend()
    plt.savefig(os.path.join(save_dir, 'recent_cumulative_distribution.png'))
    plt.close()

def main():
    # Find all verification results from March 31, 2025
    verification_dirs = glob('reports/attack_verification_20250331_*')
    if not verification_dirs:
        print("No recent verification results found")
        return
    
    all_scores = []
    for dir_path in verification_dirs:
        results_file = os.path.join(dir_path, 'results.json')
        if os.path.exists(results_file):
            print(f"Processing: {results_file}")
            scores = process_results_file(results_file)
            all_scores.extend(scores)
    
    if not all_scores:
        print("No scores found in the recent results")
        return
    
    # Analyze scores
    analysis = analyze_scores(all_scores)
    
    # Print summary
    print("\nRecent Accuracy Analysis:")
    print(f"Total samples analyzed: {analysis['total_samples']}")
    print(f"Samples with ≥98% accuracy: {analysis['high_accuracy_samples']}")
    print(f"Percentage of high accuracy samples: {analysis['high_accuracy_percentage']:.2f}%")
    print(f"\nScore Statistics:")
    print(f"Mean score: {analysis['mean_score']:.4f}")
    print(f"Median score: {analysis['median_score']:.4f}")
    print(f"Standard deviation: {analysis['std_score']:.4f}")
    print(f"Range: {analysis['min_score']:.4f} - {analysis['max_score']:.4f}")
    
    # Create visualizations
    plot_accuracy_metrics(all_scores)
    print("\nVisualizations saved to reports/recent_accuracy/")

if __name__ == "__main__":
    main() 