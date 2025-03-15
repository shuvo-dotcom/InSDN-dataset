import numpy as np
import tensorflow as tf
from tensorflow.keras.layers import Input, LSTM, RepeatVector, TimeDistributed, Dense
from tensorflow.keras.models import Model
from sklearn.model_selection import train_test_split
# import os
# os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
# import tensorflow as tf
print("Num GPUs Available:", len(tf.config.list_physical_devices('GPU')))

# Load sequences
X_sequences = np.load('data/X_sequences.npy')
y_labels = np.load('data/y_labels.npy')

# Use only normal data (Label=0) for training
X_normal = X_sequences[y_labels == 0]

# Train-validation split
from sklearn.model_selection import train_test_split
X_train, X_val = train_test_split(X_normal, test_size=0.2, random_state=42)

# Define LSTM Autoencoder model
timesteps, features = X_train.shape[1], X_train.shape[2]

inputs = Input(shape=(timesteps, features))
encoded = LSTM(64, activation='relu', return_sequences=True)(inputs)
encoded = LSTM(32, activation='relu', return_sequences=False)(encoded)

decoded = RepeatVector(timesteps)(encoded)
decoded = LSTM(32, activation='relu', return_sequences=True)(decoded)
decoded = LSTM(64, activation='relu', return_sequences=True)(decoded)
outputs = TimeDistributed(Dense(features))(decoded)

autoencoder = Model(inputs, outputs)
autoencoder.compile(optimizer='adam', loss='mse')

autoencoder.summary()

# Training the model
import tensorflow as tf
history = autoencoder.fit(
    X_train, X_train,
    epochs=50,
    batch_size=64,
    validation_data=(X_val, X_val),
    callbacks=[
        tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
    ]
)

# Save trained model
autoencoder.save('models/lstm_autoencoder.keras')
print("Training completed and model saved.")
