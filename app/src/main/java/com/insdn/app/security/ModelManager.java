package com.insdn.app.security;

import android.content.Context;
import android.util.Log;
import org.tensorflow.lite.Interpreter;
import java.io.FileInputStream;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.MappedByteBuffer;
import java.nio.channels.FileChannel;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.CompletableFuture;

public class ModelManager {
    private static final String TAG = "ModelManager";
    private static final String MODEL_FILE = "intrusion_detection.tflite";
    private static final int INPUT_SIZE = 84;
    private static final int OUTPUT_SIZE = 1;
    private static final float GAN_THRESHOLD = 0.7f;
    private static final float OPENAI_THRESHOLD = 0.8f;

    private final Context context;
    private Interpreter tflite;
    private final ExecutorService executor;

    public interface DetectionCallback {
        void onDetectionResult(boolean isIntrusion, float confidence, String details);
    }

    public ModelManager(Context context) {
        this.context = context;
        this.executor = Executors.newSingleThreadExecutor();
        loadModel();
    }

    private void loadModel() {
        try {
            MappedByteBuffer modelBuffer = loadModelFile();
            tflite = new Interpreter(modelBuffer);
            Log.i(TAG, "Model loaded successfully");
        } catch (Exception e) {
            Log.e(TAG, "Error loading model", e);
        }
    }

    private MappedByteBuffer loadModelFile() throws Exception {
        String modelPath = MODEL_FILE;
        FileInputStream fileInputStream = new FileInputStream(context.getAssets().openFd(modelPath).getFileDescriptor());
        FileChannel fileChannel = fileInputStream.getChannel();
        long startOffset = context.getAssets().openFd(modelPath).getStartOffset();
        long declaredLength = context.getAssets().openFd(modelPath).getDeclaredLength();
        return fileChannel.map(FileChannel.MapMode.READ_ONLY, startOffset, declaredLength);
    }

    public void detectIntrusion(NetworkTrafficData trafficData, DetectionCallback callback) {
        if (tflite == null) {
            Log.e(TAG, "Model not loaded");
            callback.onDetectionResult(false, 0.0f, "Model not loaded");
            return;
        }

        executor.execute(() -> {
            try {
                // Prepare input data
                ByteBuffer inputBuffer = prepareInput(trafficData);
                
                // Prepare output buffer
                ByteBuffer outputBuffer = ByteBuffer.allocateDirect(4 * OUTPUT_SIZE);
                outputBuffer.order(ByteOrder.nativeOrder());
                
                // Run inference
                tflite.run(inputBuffer, outputBuffer);
                
                // Process output
                outputBuffer.rewind();
                float confidence = outputBuffer.getFloat();
                
                // Determine if this is an intrusion
                boolean isIntrusion = confidence >= GAN_THRESHOLD;
                
                // Generate details
                String details = generateDetails(trafficData, confidence);
                
                // Call callback on main thread
                callback.onDetectionResult(isIntrusion, confidence, details);
            } catch (Exception e) {
                Log.e(TAG, "Error during inference", e);
                callback.onDetectionResult(false, 0.0f, "Error during inference: " + e.getMessage());
            }
        });
    }

    private ByteBuffer prepareInput(NetworkTrafficData data) {
        ByteBuffer inputBuffer = ByteBuffer.allocateDirect(4 * INPUT_SIZE);
        inputBuffer.order(ByteOrder.nativeOrder());
        
        // Add network metrics
        inputBuffer.putFloat((float) data.getBandwidth());
        inputBuffer.putFloat((float) data.getLatency());
        inputBuffer.putFloat((float) data.getPacketLoss());
        inputBuffer.putFloat(data.getPacketCount());
        inputBuffer.putFloat(data.getFlowDuration());
        
        // Add IP addresses (convert to float array)
        float[] sourceIP = ipToFloatArray(data.getSourceIP());
        float[] destIP = ipToFloatArray(data.getDestinationIP());
        for (float f : sourceIP) inputBuffer.putFloat(f);
        for (float f : destIP) inputBuffer.putFloat(f);
        
        // Add ports
        inputBuffer.putFloat(data.getSourcePort());
        inputBuffer.putFloat(data.getDestinationPort());
        
        // Add protocol (one-hot encoding)
        String protocol = data.getProtocol().toUpperCase();
        if (protocol.equals("TCP")) {
            inputBuffer.putFloat(1.0f);
            inputBuffer.putFloat(0.0f);
            inputBuffer.putFloat(0.0f);
        } else if (protocol.equals("UDP")) {
            inputBuffer.putFloat(0.0f);
            inputBuffer.putFloat(1.0f);
            inputBuffer.putFloat(0.0f);
        } else {
            inputBuffer.putFloat(0.0f);
            inputBuffer.putFloat(0.0f);
            inputBuffer.putFloat(1.0f);
        }
        
        return inputBuffer;
    }

    private float[] ipToFloatArray(String ip) {
        float[] result = new float[4];
        String[] parts = ip.split("\\.");
        for (int i = 0; i < 4; i++) {
            result[i] = Float.parseFloat(parts[i]) / 255.0f;
        }
        return result;
    }

    private String generateDetails(NetworkTrafficData data, float confidence) {
        StringBuilder details = new StringBuilder();
        details.append("Potential intrusion detected:\n");
        details.append("Source: ").append(data.getSourceIP()).append(":").append(data.getSourcePort()).append("\n");
        details.append("Destination: ").append(data.getDestinationIP()).append(":").append(data.getDestinationPort()).append("\n");
        details.append("Protocol: ").append(data.getProtocol()).append("\n");
        details.append("Bandwidth: ").append(String.format("%.2f", data.getBandwidth())).append(" Mbps\n");
        details.append("Latency: ").append(String.format("%.2f", data.getLatency())).append(" ms\n");
        details.append("Packet Loss: ").append(String.format("%.2f", data.getPacketLoss())).append("%\n");
        details.append("Confidence: ").append(String.format("%.2f", confidence * 100)).append("%");
        return details.toString();
    }

    public void close() {
        if (tflite != null) {
            tflite.close();
            tflite = null;
        }
        executor.shutdown();
    }
} 