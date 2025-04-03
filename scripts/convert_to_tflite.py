import torch
import tensorflow as tf
import numpy as np
from gan_model import Discriminator
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def convert_pytorch_to_tflite(pytorch_model_path, input_shape, output_path):
    """Convert PyTorch model to TensorFlow Lite format"""
    try:
        # Load PyTorch model
        logger.info(f"Loading PyTorch model from {pytorch_model_path}")
        model = Discriminator(input_dim=input_shape[1])
        model.load_state_dict(torch.load(pytorch_model_path))
        model.eval()

        # Create TensorFlow model
        logger.info("Creating TensorFlow model")
        class TFLiteModel(tf.Module):
            def __init__(self, pytorch_model):
                super(TFLiteModel, self).__init__()
                self.pytorch_model = pytorch_model

            @tf.function(input_signature=[tf.TensorSpec(shape=input_shape, dtype=tf.float32)])
            def __call__(self, x):
                # Convert TF tensor to PyTorch tensor
                x_torch = torch.from_numpy(x.numpy())
                with torch.no_grad():
                    # Get PyTorch model output
                    output = self.pytorch_model(x_torch)
                # Convert back to TF tensor
                return tf.convert_to_tensor(output.numpy())

        # Create TF model instance
        tf_model = TFLiteModel(model)

        # Convert to TensorFlow Lite
        logger.info("Converting to TensorFlow Lite")
        converter = tf.lite.TFLiteConverter.from_keras_model(tf_model)
        converter.optimizations = [tf.lite.Optimize.DEFAULT]
        converter.target_spec.supported_types = [tf.float32]
        tflite_model = converter.convert()

        # Save the model
        logger.info(f"Saving TFLite model to {output_path}")
        with open(output_path, 'wb') as f:
            f.write(tflite_model)

        logger.info("Conversion completed successfully")
        return True

    except Exception as e:
        logger.error(f"Error during conversion: {str(e)}")
        return False

def main():
    # Define paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    models_dir = os.path.join(base_dir, 'data', 'models')
    assets_dir = os.path.join(base_dir, 'app', 'src', 'main', 'assets')
    
    # Create assets directory if it doesn't exist
    os.makedirs(assets_dir, exist_ok=True)
    
    # Define input shape (based on your model's requirements)
    input_shape = (1, 84)  # Batch size of 1, 84 features
    
    # Convert discriminator model
    discriminator_path = os.path.join(models_dir, 'discriminator.pt')
    tflite_output_path = os.path.join(assets_dir, 'intrusion_detection.tflite')
    
    success = convert_pytorch_to_tflite(
        discriminator_path,
        input_shape,
        tflite_output_path
    )
    
    if success:
        logger.info("Model conversion completed successfully")
    else:
        logger.error("Model conversion failed")

if __name__ == "__main__":
    main() 