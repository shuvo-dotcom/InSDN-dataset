import json
import os
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

def analyze_high_accuracy(scores):
    """Analyze samples with accuracy above 90%."""
    if not scores:
        return None
    
    above_90 = [s for s in scores if s >= 0.90]
    above_95 = [s for s in scores if s >= 0.95]
    above_98 = [s for s in scores if s >= 0.98]
    
    return {
        'total_samples': len(scores),
        'above_90_count': len(above_90),
        'above_90_percentage': (len(above_90) / len(scores)) * 100,
        'above_95_count': len(above_95),
        'above_95_percentage': (len(above_95) / len(scores)) * 100,
        'above_98_count': len(above_98),
        'above_98_percentage': (len(above_98) / len(scores)) * 100
    }

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
    
    # Analyze high accuracy samples
    analysis = analyze_high_accuracy(all_scores)
    
    # Print summary
    print("\nHigh Accuracy Analysis:")
    print(f"Total samples analyzed: {analysis['total_samples']:,}")
    print(f"\nSamples with accuracy ≥90%: {analysis['above_90_count']:,}")
    print(f"Percentage of samples ≥90%: {analysis['above_90_percentage']:.2f}%")
    print(f"\nSamples with accuracy ≥95%: {analysis['above_95_count']:,}")
    print(f"Percentage of samples ≥95%: {analysis['above_95_percentage']:.2f}%")
    print(f"\nSamples with accuracy ≥98%: {analysis['above_98_count']:,}")
    print(f"Percentage of samples ≥98%: {analysis['above_98_percentage']:.2f}%")

if __name__ == "__main__":
    main() 