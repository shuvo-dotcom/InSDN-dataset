import json
import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from glob import glob
from collections import defaultdict

def process_results_file(file_path):
    """Process results file line by line to extract OpenAI scores."""
    scores = []
    with open(file_path, 'r') as f:
        for line in f:
            if '"Score:' in line:
                try:
                    score = float(line.split(':')[1].strip().rstrip('",'))
                    scores.append(score)
                except (ValueError, IndexError):
                    continue
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
        'max_score': np.max(scores),
        'score_distribution': defaultdict(int)
    }

def plot_accuracy_metrics(scores, save_dir='reports/openai_accuracy'):
    """Create visualizations for OpenAI accuracy metrics."""
    os.makedirs(save_dir, exist_ok=True)
    
    # Set style
    plt.style.use('default')
    sns.set_theme()
    
    # Plot 1: Score Distribution
    plt.figure(figsize=(12, 6))
    sns.histplot(data=scores, bins=50, kde=True)
    plt.axvline(x=0.98, color='r', linestyle='--', label='98% Threshold')
    plt.title('Distribution of OpenAI Detection Scores')
    plt.xlabel('Score')
    plt.ylabel('Count')
    plt.legend()
    plt.savefig(os.path.join(save_dir, 'score_distribution.png'))
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
    plt.title('Distribution of Score Ranges')
    plt.xlabel('Score Range')
    plt.ylabel('Number of Samples')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, 'score_ranges.png'))
    plt.close()
    
    # Plot 3: Cumulative Distribution
    plt.figure(figsize=(10, 6))
    sorted_scores = np.sort(scores)
    cumulative = np.arange(1, len(sorted_scores) + 1) / len(sorted_scores)
    plt.plot(sorted_scores, cumulative)
    plt.axvline(x=0.98, color='r', linestyle='--', label='98% Threshold')
    plt.title('Cumulative Distribution of Scores')
    plt.xlabel('Score')
    plt.ylabel('Cumulative Proportion')
    plt.grid(True)
    plt.legend()
    plt.savefig(os.path.join(save_dir, 'cumulative_distribution.png'))
    plt.close()

def main():
    # Find all verification results
    verification_dirs = glob('reports/attack_verification_*')
    if not verification_dirs:
        print("No verification results found")
        return
    
    all_scores = []
    for dir_path in verification_dirs:
        results_file = os.path.join(dir_path, 'results.json')
        if os.path.exists(results_file):
            print(f"Processing: {results_file}")
            scores = process_results_file(results_file)
            all_scores.extend(scores)
    
    if not all_scores:
        print("No scores found in the results")
        return
    
    # Analyze scores
    analysis = analyze_scores(all_scores)
    
    # Print summary
    print("\nOpenAI Accuracy Analysis:")
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
    print("\nVisualizations saved to reports/openai_accuracy/")

if __name__ == "__main__":
    main() 