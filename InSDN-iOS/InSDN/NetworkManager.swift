import Foundation
import Network
import NetworkExtension
import os.log

class NetworkManager {
    static let shared = NetworkManager()
    private var monitor: NWPathMonitor?
    private var queue = DispatchQueue(label: "NetworkMonitoring")
    private var metricsTimer: Timer?
    private let logger = Logger(subsystem: "com.insdn.app", category: "NetworkManager")
    
    var connectedDevicesHandler: (([ConnectedDevice]) -> Void)?
    var metricsHandler: ((NetworkMetrics) -> Void)?
    var topologyHandler: ((TopologyData) -> Void)?
    var errorHandler: ((String) -> Void)?
    
    struct ConnectedDevice {
        let name: String
        let ipAddress: String
        let macAddress: String
        let connectionType: String
    }
    
    private init() {
        setupNetworkMonitoring()
        startMetricsMonitoring()
    }
    
    private func setupNetworkMonitoring() {
        monitor = NWPathMonitor()
        monitor?.pathUpdateHandler = { [weak self] path in
            self?.handleNetworkPathUpdate(path)
        }
        monitor?.start(queue: queue)
    }
    
    private func startMetricsMonitoring() {
        metricsTimer = Timer.scheduledTimer(withTimeInterval: 1.0, repeats: true) { [weak self] _ in
            self?.updateMetrics()
        }
    }
    
    private func updateMetrics() {
        let metrics = NetworkMetrics(
            bandwidth: Double.random(in: 50...150),
            latency: Double.random(in: 10...100),
            packetLoss: Double.random(in: 0...5)
        )
        
        logger.debug("Updated metrics: bandwidth=\(metrics.bandwidth), latency=\(metrics.latency), packetLoss=\(metrics.packetLoss)")
        
        DispatchQueue.main.async {
            self.metricsHandler?(metrics)
        }
    }
    
    private func handleNetworkPathUpdate(_ path: NWPath) {
        logger.debug("Network path updated: \(path.status)")
        
        if path.status == .satisfied {
            self.scanNetwork()
            self.updateTopology()
        } else {
            DispatchQueue.main.async {
                self.errorHandler?("Network connection lost")
            }
        }
    }
    
    private func updateTopology() {
        // Simulate topology for demo purposes
        // In a real app, you would get this from your SDN controller
        let nodes = [
            "Switch1": "OpenFlow Switch 1",
            "Switch2": "OpenFlow Switch 2",
            "Switch3": "OpenFlow Switch 3"
        ]
        
        let links = [
            TopologyData.Link(source: "Switch1", destination: "Switch2", bandwidth: 100),
            TopologyData.Link(source: "Switch2", destination: "Switch3", bandwidth: 100),
            TopologyData.Link(source: "Switch3", destination: "Switch1", bandwidth: 100)
        ]
        
        let topology = TopologyData(nodes: nodes, links: links)
        
        DispatchQueue.main.async {
            self.topologyHandler?(topology)
        }
    }
    
    private func scanNetwork() {
        logger.debug("Starting network scan")
        
        NEHotspotNetwork.fetchCurrent { [weak self] network in
            guard let network = network else {
                self?.logger.error("Not connected to WiFi")
                DispatchQueue.main.async {
                    self?.errorHandler?("Not connected to WiFi")
                }
                return
            }
            
            self?.logger.debug("Connected to network: \(network.ssid)")
            
            var devices: [ConnectedDevice] = []
            
            // Add current device
            if let deviceIP = self?.getDeviceIP() {
                devices.append(ConnectedDevice(
                    name: network.ssid,
                    ipAddress: deviceIP,
                    macAddress: network.bssid,
                    connectionType: "WiFi"
                ))
            }
            
            // Add router
            devices.append(ConnectedDevice(
                name: "Gateway",
                ipAddress: network.router?.description ?? "Unknown",
                macAddress: "Unknown",
                connectionType: "Router"
            ))
            
            DispatchQueue.main.async {
                self?.connectedDevicesHandler?(devices)
            }
        }
    }
    
    private func getDeviceIP() -> String? {
        var address: String?
        var ifaddr: UnsafeMutablePointer<ifaddrs>?
        
        guard getifaddrs(&ifaddr) == 0 else {
            return nil
        }
        defer { freeifaddrs(ifaddr) }
        
        var ptr = ifaddr
        while ptr != nil {
            defer { ptr = ptr?.pointee.ifa_next }
            
            let interface = ptr?.pointee
            let addrFamily = interface?.ifa_addr.pointee.sa_family
            
            if addrFamily == UInt8(AF_INET) {
                let name = String(cString: (interface?.ifa_name)!)
                if name == "en0" {
                    var hostname = [CChar](repeating: 0, count: Int(NI_MAXHOST))
                    getnameinfo(interface?.ifa_addr,
                              socklen_t((interface?.ifa_addr.pointee.sa_len)!),
                              &hostname,
                              socklen_t(hostname.count),
                              nil,
                              0,
                              NI_NUMERICHOST)
                    address = String(cString: hostname)
                }
            }
        }
        return address
    }
    
    func startMonitoring() {
        monitor?.start(queue: queue)
        startMetricsMonitoring()
    }
    
    func stopMonitoring() {
        monitor?.cancel()
        metricsTimer?.invalidate()
        metricsTimer = nil
    }
} 