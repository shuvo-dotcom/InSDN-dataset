import SwiftUI

struct ContentView: View {
    @State private var metricsCard = MetricsCardView()
    @State private var metricsGraph = MetricsGraphView()
    @State private var topologyView = TopologyView()
    @State private var connectedDevicesView = ConnectedDevicesView()
    
    var body: some View {
        ScrollView {
            VStack(spacing: 16) {
                metricsCard
                    .padding(.horizontal)
                
                metricsGraph
                    .padding(.horizontal)
                    .frame(height: 350)
                
                topologyView
                    .padding(.horizontal)
                    .frame(height: 300)
                
                connectedDevicesView
                    .padding(.horizontal)
            }
            .padding(.vertical)
        }
        .onAppear {
            setupNetworkManager()
        }
    }
    
    private func setupNetworkManager() {
        let manager = NetworkManager.shared
        
        manager.metricsHandler = { metrics in
            metricsCard.updateMetrics(metrics)
            metricsGraph.updateMetrics(metrics)
        }
        
        manager.topologyHandler = { topology in
            topologyView.updateTopology(topology)
        }
        
        manager.startMonitoring()
    }
}

#Preview {
    ContentView()
} 