package com.insdn.app.security;

public class NetworkTrafficData {
    private final double bandwidth;
    private final double latency;
    private final double packetLoss;
    private final int packetCount;
    private final long flowDuration;
    private final String sourceIP;
    private final String destinationIP;
    private final int sourcePort;
    private final int destinationPort;
    private final String protocol;

    private NetworkTrafficData(Builder builder) {
        this.bandwidth = builder.bandwidth;
        this.latency = builder.latency;
        this.packetLoss = builder.packetLoss;
        this.packetCount = builder.packetCount;
        this.flowDuration = builder.flowDuration;
        this.sourceIP = builder.sourceIP;
        this.destinationIP = builder.destinationIP;
        this.sourcePort = builder.sourcePort;
        this.destinationPort = builder.destinationPort;
        this.protocol = builder.protocol;
    }

    // Getters
    public double getBandwidth() { return bandwidth; }
    public double getLatency() { return latency; }
    public double getPacketLoss() { return packetLoss; }
    public int getPacketCount() { return packetCount; }
    public long getFlowDuration() { return flowDuration; }
    public String getSourceIP() { return sourceIP; }
    public String getDestinationIP() { return destinationIP; }
    public int getSourcePort() { return sourcePort; }
    public int getDestinationPort() { return destinationPort; }
    public String getProtocol() { return protocol; }

    // Builder pattern for easy construction
    public static class Builder {
        private double bandwidth;
        private double latency;
        private double packetLoss;
        private int packetCount;
        private long flowDuration;
        private String sourceIP;
        private String destinationIP;
        private int sourcePort;
        private int destinationPort;
        private String protocol;

        public Builder setBandwidth(double bandwidth) {
            this.bandwidth = bandwidth;
            return this;
        }

        public Builder setLatency(double latency) {
            this.latency = latency;
            return this;
        }

        public Builder setPacketLoss(double packetLoss) {
            this.packetLoss = packetLoss;
            return this;
        }

        public Builder setPacketCount(int packetCount) {
            this.packetCount = packetCount;
            return this;
        }

        public Builder setFlowDuration(long flowDuration) {
            this.flowDuration = flowDuration;
            return this;
        }

        public Builder setSourceIP(String sourceIP) {
            this.sourceIP = sourceIP;
            return this;
        }

        public Builder setDestinationIP(String destinationIP) {
            this.destinationIP = destinationIP;
            return this;
        }

        public Builder setSourcePort(int sourcePort) {
            this.sourcePort = sourcePort;
            return this;
        }

        public Builder setDestinationPort(int destinationPort) {
            this.destinationPort = destinationPort;
            return this;
        }

        public Builder setProtocol(String protocol) {
            this.protocol = protocol;
            return this;
        }

        public NetworkTrafficData build() {
            return new NetworkTrafficData(this);
        }
    }
} 