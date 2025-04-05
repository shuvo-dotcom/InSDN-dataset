import json
import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from glob import glob

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

def create_accuracy_heatmap(scores, save_dir='reports/accuracy_maps'):
    """Create a detailed heatmap of accuracy distribution."""
    os.makedirs(save_dir, exist_ok=True)
    
    # Set style
    plt.style.use('default')
    sns.set_theme()
    
    # Create figure with multiple subplots
    fig = plt.figure(figsize=(20, 15))
    
    # 1. Detailed Histogram with KDE
    plt.subplot(2, 2, 1)
    sns.histplot(data=scores, bins=100, kde=True)
    plt.title('Detailed Accuracy Distribution')
    plt.xlabel('Accuracy Score')
    plt.ylabel('Number of Samples')
    plt.axvline(x=0.90, color='g', linestyle='--', label='90%')
    plt.axvline(x=0.95, color='y', linestyle='--', label='95%')
    plt.axvline(x=0.98, color='r', linestyle='--', label='98%')
    plt.legend()
    
    # 2. Fine-grained Range Distribution
    plt.subplot(2, 2, 2)
    ranges = {
        '< 50%': len([s for s in scores if s < 0.5]),
        '50-60%': len([s for s in scores if 0.5 <= s < 0.6]),
        '60-70%': len([s for s in scores if 0.6 <= s < 0.7]),
        '70-80%': len([s for s in scores if 0.7 <= s < 0.8]),
        '80-85%': len([s for s in scores if 0.8 <= s < 0.85]),
        '85-90%': len([s for s in scores if 0.85 <= s < 0.9]),
        '90-92%': len([s for s in scores if 0.9 <= s < 0.92]),
        '92-94%': len([s for s in scores if 0.92 <= s < 0.94]),
        '94-96%': len([s for s in scores if 0.94 <= s < 0.96]),
        '96-98%': len([s for s in scores if 0.96 <= s < 0.98]),
        '≥ 98%': len([s for s in scores if s >= 0.98])
    }
    plt.bar(ranges.keys(), ranges.values())
    plt.title('Fine-grained Accuracy Distribution')
    plt.xlabel('Accuracy Range')
    plt.ylabel('Number of Samples')
    plt.xticks(rotation=45)
    
    # 3. Cumulative Distribution
    plt.subplot(2, 2, 3)
    sorted_scores = np.sort(scores)
    cumulative = np.arange(1, len(sorted_scores) + 1) / len(sorted_scores)
    plt.plot(sorted_scores, cumulative, 'b-', linewidth=2)
    plt.grid(True)
    plt.title('Cumulative Accuracy Distribution')
    plt.xlabel('Accuracy Score')
    plt.ylabel('Cumulative Proportion')
    plt.axvline(x=0.90, color='g', linestyle='--', label='90%')
    plt.axvline(x=0.95, color='y', linestyle='--', label='95%')
    plt.axvline(x=0.98, color='r', linestyle='--', label='98%')
    plt.legend()
    
    # 4. Box Plot with Violin Plot
    plt.subplot(2, 2, 4)
    sns.violinplot(data=scores)
    plt.title('Accuracy Distribution Shape')
    plt.xlabel('Samples')
    plt.ylabel('Accuracy Score')
    
    # Adjust layout and save
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, 'accuracy_distribution_map.png'))
    plt.close()
    
    # Print detailed statistics
    print("\nDetailed Accuracy Statistics:")
    print("-" * 50)
    print(f"Total Samples: {len(scores):,}")
    
    percentiles = [1, 5, 10, 25, 50, 75, 90, 95, 99]
    print("\nPercentile Distribution:")
    for p in percentiles:
        value = np.percentile(scores, p)
        print(f"{p}th percentile: {value:.4f}")
    
    print("\nAccuracy Range Distribution:")
    for range_name, count in ranges.items():
        percentage = (count / len(scores)) * 100
        print(f"{range_name}: {count:,} samples ({percentage:.2f}%)")

def main():
    # Find all verification results
    verification_dirs = glob('reports/attack_verification_20250331_*')
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
    
    # Create visualizations and print statistics
    create_accuracy_heatmap(all_scores)
    print("\nVisualization maps saved to reports/accuracy_maps/")

if __name__ == "__main__":
    main() 