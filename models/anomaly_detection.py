import numpy as np
from tensorflow.keras.models import load_model

model = tf.keras.models.load_model('lstm_autoencoder.keras')

def detect(sequence, threshold):
    reconstruction = model.predict(sequence.reshape(1, *sequence.shape))
    error = np.mean((sequence - reconstruction)**2)
    return error > threshold
