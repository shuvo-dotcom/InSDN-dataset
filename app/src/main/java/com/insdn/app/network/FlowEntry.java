package com.insdn.app.network;

public class FlowEntry {
    private String flowId;
    private String sourcePort;
    private String destinationPort;
    private int bandwidth;

    public FlowEntry(String flowId, String sourcePort, String destinationPort, int bandwidth) {
        this.flowId = flowId;
        this.sourcePort = sourcePort;
        this.destinationPort = destinationPort;
        this.bandwidth = bandwidth;
    }

    public String getFlowId() { return flowId; }
    public String getSourcePort() { return sourcePort; }
    public String getDestinationPort() { return destinationPort; }
    public int getBandwidth() { return bandwidth; }
} 