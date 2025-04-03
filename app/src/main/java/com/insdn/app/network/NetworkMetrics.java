package com.insdn.app.network;

public class NetworkMetrics {
    private float bandwidth;    // in Mbps
    private float latency;      // in ms
    private float packetLoss;   // in percentage

    public float getBandwidth() { return bandwidth; }
    public void setBandwidth(float bandwidth) { this.bandwidth = bandwidth; }

    public float getLatency() { return latency; }
    public void setLatency(float latency) { this.latency = latency; }

    public float getPacketLoss() { return packetLoss; }
    public void setPacketLoss(float packetLoss) { this.packetLoss = packetLoss; }
} 