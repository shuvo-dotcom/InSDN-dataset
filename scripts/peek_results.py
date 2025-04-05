import json

def peek_file(file_path, num_lines=10):
    """Print the first few lines of a file to understand its structure."""
    print(f"\nExamining file: {file_path}")
    print("-" * 80)
    with open(file_path, 'r') as f:
        for i, line in enumerate(f):
            if i >= num_lines:
                break
            print(line.strip())
    print("-" * 80)

if __name__ == "__main__":
    # Look at the most recent results file
    peek_file('reports/attack_verification_20250331_172230/results.json') 