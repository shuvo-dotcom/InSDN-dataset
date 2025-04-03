import Foundation

struct NetworkMetrics {
    let bandwidth: Double
    let latency: Double
    let packetLoss: Double
    
    init(bandwidth: Double = 0.0, latency: Double = 0.0, packetLoss: Double = 0.0) {
        self.bandwidth = bandwidth
        self.latency = latency
        self.packetLoss = packetLoss
    }
} 