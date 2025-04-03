import SwiftUI

struct MetricsCardView: View {
    @State private var metrics: NetworkMetrics = NetworkMetrics()
    
    var body: some View {
        VStack(spacing: 16) {
            MetricRow(
                title: "Bandwidth",
                value: String(format: "%.2f Mbps", metrics.bandwidth),
                color: Color("bandwidth_color")
            )
            
            MetricRow(
                title: "Latency",
                value: String(format: "%.2f ms", metrics.latency),
                color: Color("latency_color")
            )
            
            MetricRow(
                title: "Packet Loss",
                value: String(format: "%.2f%%", metrics.packetLoss),
                color: Color("packet_loss_color")
            )
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(12)
        .shadow(radius: 4)
    }
    
    func updateMetrics(_ newMetrics: NetworkMetrics) {
        metrics = newMetrics
    }
}

struct MetricRow: View {
    let title: String
    let value: String
    let color: Color
    
    var body: some View {
        HStack {
            Text(title)
                .foregroundColor(.secondary)
            Spacer()
            Text(value)
                .foregroundColor(color)
                .bold()
        }
    }
}

#Preview {
    MetricsCardView()
        .padding()
        .background(Color(.systemGroupedBackground))
} 