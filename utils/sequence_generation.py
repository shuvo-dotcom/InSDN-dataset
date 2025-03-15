import pandas as pd
import numpy as np

# Load scaled and selected data
data = pd.read_csv('data/scaled_selected_data.csv')

WINDOW_SIZE = 30  # recommended sequence length

def create_sequences(df, window_size):
    sequences, labels = [], []
    data_array = df.drop('Label', axis=1).values
    label_array = df['Label'].values

    for i in range(len(df) - window_size):
        seq = data_array[i:i+window_size]
        lbl = label_array[i+window_size-1]  # Label at the end of sequence
        sequences.append(seq)
        labels.append(lbl)

    return np.array(sequences), np.array(labels)

# Generate sequences
df = pd.read_csv('data/scaled_selected_data.csv')
window_size = 30

X_sequences, y_sequences = create_sequences(df, window_size=window_size)

# Save sequences for model training
np.save('data/X_sequences.npy', X_sequences)
np.save('data/y_labels.npy', y_sequences)

print(f"Generated sequences shape: {X_sequences.shape}")
print("Sequence generation completed.")
