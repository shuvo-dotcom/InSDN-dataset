import numpy as np

def create_sequences(data, window_size=30):
    sequences = []
    for i in range(len(data) - window_size):
        seq = data[i:i+window_size]
        sequences.append(seq)
    return np.array(sequences)
