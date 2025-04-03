package com.insdn.app.network;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class TopologyData {
    private Map<String, String> nodes; // nodeName -> MAC address
    private List<Link> links;

    public TopologyData() {
        nodes = new HashMap<>();
        links = new ArrayList<>();
    }

    public void addNode(String name, String macAddress) {
        nodes.put(name, macAddress);
    }

    public void addLink(String source, String destination, int bandwidth) {
        links.add(new Link(source, destination, bandwidth));
    }

    public Map<String, String> getNodes() {
        return nodes;
    }

    public List<Link> getLinks() {
        return links;
    }

    public static class Link {
        private String source;
        private String destination;
        private int bandwidth;

        public Link(String source, String destination, int bandwidth) {
            this.source = source;
            this.destination = destination;
            this.bandwidth = bandwidth;
        }

        public String getSource() { return source; }
        public String getDestination() { return destination; }
        public int getBandwidth() { return bandwidth; }
    }
} 