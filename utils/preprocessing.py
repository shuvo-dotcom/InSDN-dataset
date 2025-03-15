import pandas as pd

# Load raw data
data = pd.read_csv('data/OVS.csv')

# Drop irrelevant columns
columns_to_drop = ['Flow ID', 'Timestamp', 'Src IP', 'Dst IP', 'Src Port', 'Dst Port']
data.drop(columns=columns_to_drop, inplace=True, errors='ignore')

# Encode label as binary (Normal=0, Attack=1)
data['Label'] = data['Label'].apply(lambda x: 0 if x.lower() == 'normal' else 1)

# Confirm label distribution
print("Label Distribution:")
print(data['Label'].value_counts())

# Check for missing values
print("\nMissing Values:")
print(data.isnull().sum().sum())

# Save processed data for next step
data.to_csv('data/InSDN_preprocessed.csv', index=False)
print("\nPreprocessed data saved successfully!")
