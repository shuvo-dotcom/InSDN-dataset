package com.insdn.app.security;

import android.content.Context;
import android.util.Log;
import com.insdn.app.network.NetworkMonitor;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.CompletableFuture;

public class NetworkIntrusionDetector {
    private static final String TAG = "NetworkIntrusionDetector";
    private static final float INTRUSION_THRESHOLD = 0.7f;

    private final Context context;
    private final NetworkMonitor networkMonitor;
    private final ModelManager modelManager;
    private final OpenAIVerifier openaiVerifier;
    private final ExecutorService executor;
    private IntrusionDetectionCallback callback;

    public interface IntrusionDetectionCallback {
        void onIntrusionDetected(IntrusionEvent event);
        void onNormalStatus();
    }

    public static class IntrusionEvent {
        private final String sourceIP;
        private final String destinationIP;
        private final int sourcePort;
        private final int destinationPort;
        private final String protocol;
        private final float confidence;
        private final String details;
        private final long timestamp;

        public IntrusionEvent(String sourceIP, String destinationIP, int sourcePort, 
                             int destinationPort, String protocol, float confidence, 
                             String details, long timestamp) {
            this.sourceIP = sourceIP;
            this.destinationIP = destinationIP;
            this.sourcePort = sourcePort;
            this.destinationPort = destinationPort;
            this.protocol = protocol;
            this.confidence = confidence;
            this.details = details;
            this.timestamp = timestamp;
        }

        public String getSourceIP() { return sourceIP; }
        public String getDestinationIP() { return destinationIP; }
        public int getSourcePort() { return sourcePort; }
        public int getDestinationPort() { return destinationPort; }
        public String getProtocol() { return protocol; }
        public float getConfidence() { return confidence; }
        public String getDetails() { return details; }
        public long getTimestamp() { return timestamp; }
    }

    public NetworkIntrusionDetector(Context context, NetworkMonitor networkMonitor) {
        this.context = context;
        this.networkMonitor = networkMonitor;
        this.modelManager = new ModelManager(context);
        this.openaiVerifier = new OpenAIVerifier(context);
        this.executor = Executors.newSingleThreadExecutor();
    }

    public void setCallback(IntrusionDetectionCallback callback) {
        this.callback = callback;
    }

    public void setOpenAIKey(String apiKey) {
        openaiVerifier.setApiKey(apiKey);
    }

    public void startMonitoring() {
        // Start monitoring network traffic
        executor.execute(() -> {
            while (!Thread.currentThread().isInterrupted()) {
                try {
                    // Create NetworkTrafficData from current network metrics
                    NetworkTrafficData trafficData = createTrafficDataFromMetrics();
                    analyzeTraffic(trafficData);
                    Thread.sleep(1000); // Check every second
                } catch (InterruptedException e) {
                    break;
                } catch (Exception e) {
                    Log.e(TAG, "Error in monitoring loop", e);
                }
            }
        });
    }

    private NetworkTrafficData createTrafficDataFromMetrics() {
        // Create a NetworkTrafficData object from the current network metrics
        // This is a simplified version - in a real app, you would get actual traffic data
        return new NetworkTrafficData.Builder()
                .setBandwidth(100.0) // Example value
                .setLatency(50.0)    // Example value
                .setPacketLoss(0.1)  // Example value
                .setPacketCount(1000)
                .setFlowDuration(5000)
                .setSourceIP("192.168.1.100")
                .setDestinationIP("192.168.1.1")
                .setSourcePort(12345)
                .setDestinationPort(80)
                .setProtocol("TCP")
                .build();
    }

    private void analyzeTraffic(NetworkTrafficData trafficData) {
        modelManager.detectIntrusion(trafficData, new ModelManager.DetectionCallback() {
            @Override
            public void onDetectionResult(boolean isIntrusion, float confidence, String details) {
                if (isIntrusion && confidence >= INTRUSION_THRESHOLD) {
                    // Create an intrusion event
                    IntrusionEvent event = new IntrusionEvent(
                            trafficData.getSourceIP(),
                            trafficData.getDestinationIP(),
                            trafficData.getSourcePort(),
                            trafficData.getDestinationPort(),
                            trafficData.getProtocol(),
                            confidence,
                            details,
                            System.currentTimeMillis()
                    );
                    
                    // Notify callback
                    if (callback != null) {
                        callback.onIntrusionDetected(event);
                    }
                    
                    // Log the intrusion
                    Log.w(TAG, "Intrusion detected: " + details + 
                          " (Confidence: " + (confidence * 100) + "%)");
                } else {
                    // Normal traffic
                    if (callback != null) {
                        callback.onNormalStatus();
                    }
                }
            }
        });
    }

    public void stopMonitoring() {
        executor.shutdownNow();
    }
} 