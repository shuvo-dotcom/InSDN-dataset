package com.insdn.app.security;

import android.content.Context;
import android.util.Log;
import org.json.JSONObject;
import java.io.IOException;
import okhttp3.*;
import java.util.concurrent.TimeUnit;

public class OpenAIVerifier {
    private static final String TAG = "OpenAIVerifier";
    private static final String OPENAI_API_URL = "https://api.openai.com/v1/chat/completions";
    private static final int TIMEOUT_SECONDS = 30;
    
    private final Context context;
    private final OkHttpClient client;
    private String apiKey;
    
    public interface VerificationCallback {
        void onVerificationComplete(boolean isIntrusion, float confidence, String details);
        void onError(String error);
    }
    
    public OpenAIVerifier(Context context) {
        this.context = context;
        this.client = new OkHttpClient.Builder()
            .connectTimeout(TIMEOUT_SECONDS, TimeUnit.SECONDS)
            .readTimeout(TIMEOUT_SECONDS, TimeUnit.SECONDS)
            .writeTimeout(TIMEOUT_SECONDS, TimeUnit.SECONDS)
            .build();
    }
    
    public void setApiKey(String apiKey) {
        this.apiKey = apiKey;
    }
    
    public void verifyTraffic(NetworkTrafficData trafficData, float ganConfidence, VerificationCallback callback) {
        if (apiKey == null || apiKey.isEmpty()) {
            callback.onError("OpenAI API key not set");
            return;
        }
        
        // Prepare the prompt
        String prompt = String.format(
            "Analyze this network traffic pattern for potential intrusions:\n" +
            "Bandwidth: %.2f Mbps\n" +
            "Latency: %.2f ms\n" +
            "Packet Loss: %.2f%%\n" +
            "Packet Count: %d\n" +
            "Flow Duration: %.2f seconds\n" +
            "GAN Model Confidence: %.2f%%\n\n" +
            "Please provide:\n" +
            "1. Is this traffic malicious? (yes/no)\n" +
            "2. Confidence level (0-1)\n" +
            "3. Key indicators\n" +
            "4. Potential attack type",
            trafficData.getBandwidth(),
            trafficData.getLatency(),
            trafficData.getPacketLoss(),
            trafficData.getPacketCount(),
            trafficData.getFlowDuration(),
            ganConfidence * 100
        );
        
        // Create JSON request body
        JSONObject requestBody = new JSONObject();
        try {
            requestBody.put("model", "gpt-4");
            requestBody.put("messages", new JSONObject[]{
                new JSONObject()
                    .put("role", "system")
                    .put("content", "You are a network security expert analyzing traffic patterns."),
                new JSONObject()
                    .put("role", "user")
                    .put("content", prompt)
            });
            requestBody.put("temperature", 0.3);
            requestBody.put("max_tokens", 500);
            
            // Create request
            Request request = new Request.Builder()
                .url(OPENAI_API_URL)
                .addHeader("Authorization", "Bearer " + apiKey)
                .addHeader("Content-Type", "application/json")
                .post(RequestBody.create(
                    MediaType.parse("application/json"),
                    requestBody.toString()
                ))
                .build();
            
            // Execute request asynchronously
            client.newCall(request).enqueue(new Callback() {
                @Override
                public void onFailure(Call call, IOException e) {
                    Log.e(TAG, "OpenAI API request failed", e);
                    callback.onError("API request failed: " + e.getMessage());
                }
                
                @Override
                public void onResponse(Call call, Response response) throws IOException {
                    if (!response.isSuccessful()) {
                        callback.onError("API error: " + response.code());
                        return;
                    }
                    
                    try {
                        String responseBody = response.body().string();
                        JSONObject jsonResponse = new JSONObject(responseBody);
                        String content = jsonResponse.getJSONArray("choices")
                            .getJSONObject(0)
                            .getJSONObject("message")
                            .getString("content");
                        
                        // Parse OpenAI response
                        parseAndCallback(content, callback);
                    } catch (Exception e) {
                        Log.e(TAG, "Error parsing OpenAI response", e);
                        callback.onError("Error parsing response: " + e.getMessage());
                    }
                }
            });
            
        } catch (Exception e) {
            Log.e(TAG, "Error creating OpenAI request", e);
            callback.onError("Error creating request: " + e.getMessage());
        }
    }
    
    private void parseAndCallback(String response, VerificationCallback callback) {
        try {
            boolean isIntrusion = false;
            float confidence = 0.0f;
            StringBuilder details = new StringBuilder();
            
            String[] lines = response.split("\n");
            for (String line : lines) {
                line = line.toLowerCase().trim();
                if (line.contains("malicious")) {
                    isIntrusion = line.contains("yes");
                } else if (line.contains("confidence")) {
                    try {
                        confidence = Float.parseFloat(line.replaceAll("[^0-9.]", ""));
                    } catch (NumberFormatException e) {
                        confidence = 0.5f;
                    }
                } else if (line.contains("indicator") || line.contains("attack")) {
                    details.append(line).append("\n");
                }
            }
            
            callback.onVerificationComplete(isIntrusion, confidence, details.toString());
            
        } catch (Exception e) {
            Log.e(TAG, "Error parsing OpenAI response", e);
            callback.onError("Error parsing response: " + e.getMessage());
        }
    }
} 