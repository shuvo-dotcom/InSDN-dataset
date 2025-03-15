import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.layers import Input, LSTM, RepeatVector, TimeDistributed, Dense
from tensorflow.keras.models import Model

X = np.load('../data/X_sequences.npy')

timesteps, features = X.shape[1], X.shape[2]

# Model Definition
inputs = Input(shape=(timesteps, features))
encoded = LSTM(64, activation='relu', return_sequences=True)(inputs)
encoded = LSTM(32, activation='relu', return_sequences=False)(encoded)
decoded = RepeatVector(timesteps)(encoded)
decoded = LSTM(32, activation='relu', return_sequences=True)(decoded)
decoded = LSTM(64, activation='relu', return_sequences=True)(decoded)
outputs = TimeDistributed(Dense(features))(decoded)

autoencoder = Model(inputs, outputs=decoded)
autoencoder.compile(optimizer='adam', loss='mse')

# Training
autoencoder.fit(X_train, X_train, epochs=50, batch_size=64, validation_split=0.2,
                callbacks=[tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)])

autoencoder.save('lstm_autoencoder.keras')
