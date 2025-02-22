import sys
import os
import logging
import pandas as pd
import json
import kagglehub
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from flask import Flask, request, jsonify
import openai
from main import extract_features, analyze_with_llm

# Setup logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

# Load the entire dataset for sending
dataset_path = '/Users/apple/.cache/kagglehub/datasets/badcodebuilder/insdn-dataset/versions/2/InSDN_DatasetCSV/'

# Function to download dataset if not present
def download_dataset():
    try:
        path = kagglehub.dataset_download("badcodebuilder/insdn-dataset")
        logging.info(f"Dataset downloaded to: {path}")
    except Exception as e:
        logging.error(f"Error downloading dataset: {e}")

@app.route('/analyze', methods=['GET'])
def analyze():
    download_dataset()  # Ensure dataset is downloaded
    logging.info("/analyze endpoint hit.")

    # Load the dataset by concatenating all CSV files in the dataset path
    df = pd.concat([pd.read_csv(dataset_path + file) 
                    for file in os.listdir(dataset_path) if file.endswith('.csv')])
    logging.info("First row label: " + str(df.head(1)['Label'].values[0]))

    # Extract features for each row in the dataset
    rows_features = []
    for index, row in df.iterrows():
        features = extract_features(row)
        rows_features.append(features)
        logging.info(f"Extracted features for row {index}: {features}")
        if index == 20:
            break

    # Define batch size (e.g., 100 rows per batch)
    batch_size = 20
    all_results = []
    correct_predictions = 0
    # total_batches = (len(rows_features) + batch_size - 1) // batch_size
    total_batches = 1

    # Process features in batches
    for batch_start in range(0, len(rows_features), batch_size):
        batch_features = rows_features[batch_start:batch_start + batch_size]

        # Prepare the prompt for the current batch
        prompt = (
            "Analyze the following network traffic features for each row and determine if they indicate an attack.\n"
            "For each row, return a JSON object with the following keys:\n"
            "  \"attack\": an integer where 1 indicates an attack and 0 indicates no attack,\n"
            "  \"reason\": a string providing a detailed explanation for your decision.\n"
            "Return your output as a JSON array where each element corresponds to a row in the input, in the same order.\n"
            "Features:\n" + str(batch_features)
        )

        # Call the LLM API for the current batch
        response = analyze_with_llm(prompt, model="o3-mini")
        logging.info(f"LLM response for batch {(batch_start // batch_size) + 1} of {total_batches}: {response}")

        # Process the response
        try:
            response_array = json.loads(response)
            for j, result in enumerate(response_array):
                attack_status = result.get('attack', 0)
                reason = result.get('reason', 'No reason provided')
                all_results.append({'index': batch_start + j, 'result': attack_status, 'reason': reason})
                if attack_status == 1:
                    correct_predictions += 1
        except json.JSONDecodeError:
            logging.error(f"Failed to decode JSON response for batch starting at row {batch_start}: {response}")
            # Log an error for each row in the batch if JSON decoding fails
            for j in range(len(batch_features)):
                all_results.append({'index': batch_start + j, 'result': 'error', 'reason': 'Invalid JSON response'})

    # Calculate accuracy and other metrics
    accuracy = (correct_predictions / len(all_results)) * 100 if all_results else 0
    metrics = {'accuracy': accuracy, 'total_analyzed': len(all_results)}

    return jsonify({'results': all_results, 'metrics': metrics})

@app.route('/dataset', methods=['GET'])
def get_dataset():
    df = pd.concat([pd.read_csv(dataset_path + file) for file in os.listdir(dataset_path) if file.endswith('.csv')])
    return df.to_json(orient='records')  # Return dataset as JSON

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)  # Changed port to 5002
