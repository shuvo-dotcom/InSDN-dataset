import pandas as pd
import numpy as np
from sklearn.feature_selection import mutual_info_classif
from sklearn.preprocessing import MinMaxScaler
import joblib

# Load preprocessed data
data = pd.read_csv('data/processed_data.csv')
columns_to_drop = ['Flow ID', 'Timestamp', 'Src IP', 'Dst IP', 'Src Port', 'Dst Port']
data.drop(columns=columns_to_drop, inplace=True, errors='ignore')

# Separate features and labels
X = data.drop('Label', axis=1)
y = data['Label']

# Feature Selection (Mutual Information)
print("Calculating mutual information scores...")
mi_scores = mutual_info_classif(X=X, y=y, random_state=42)

# Select top 20 features based on MI scores
top_k = 20
top_features_indices = np.argsort(mi_scores)[-top_k:]
top_features = X.columns[top_features_indices]
print(f"Selected Features ({top_k}):\n{top_features}")

# Extract selected features
X_selected = X[top_features]

# Scaling features using MinMaxScaler
from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(X_selected)

# Save scaled features and labels
scaled_df = pd.DataFrame(X_scaled, columns=top_features)
scaled_df['Label'] = y.values
scaled_df.to_csv('data/scaled_selected_data.csv', index=False)

print("Feature selection and scaling complete.")
print(f"Selected features saved: {list(top_features)}")
