import SwiftUI
import Charts

struct MetricsGraphView: View {
    @State private var bandwidthData: [MetricPoint] = []
    @State private var latencyData: [MetricPoint] = []
    @State private var packetLossData: [MetricPoint] = []
    private let maxDataPoints = 50
    
    struct MetricPoint: Identifiable {
        let id = UUID()
        let timestamp: Date
        let value: Double
    }
    
    var body: some View {
        VStack {
            Chart {
                ForEach(bandwidthData) { point in
                    LineMark(
                        x: .value("Time", point.timestamp),
                        y: .value("Bandwidth", point.value)
                    )
                    .foregroundStyle(Color("bandwidth_color"))
                }
                
                ForEach(latencyData) { point in
                    LineMark(
                        x: .value("Time", point.timestamp),
                        y: .value("Latency", point.value)
                    )
                    .foregroundStyle(Color("latency_color"))
                }
                
                ForEach(packetLossData) { point in
                    LineMark(
                        x: .value("Time", point.timestamp),
                        y: .value("Packet Loss", point.value)
                    )
                    .foregroundStyle(Color("packet_loss_color"))
                }
            }
            .frame(height: 300)
            .chartXAxis {
                AxisMarks(position: .bottom)
            }
            .chartYAxis {
                AxisMarks(position: .leading)
            }
            
            // Legend
            HStack(spacing: 16) {
                LegendItem(color: Color("bandwidth_color"), label: "Bandwidth")
                LegendItem(color: Color("latency_color"), label: "Latency")
                LegendItem(color: Color("packet_loss_color"), label: "Packet Loss")
            }
            .padding(.top, 8)
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(12)
        .shadow(radius: 4)
    }
    
    func updateMetrics(_ metrics: NetworkMetrics) {
        let now = Date()
        
        // Add new data points
        bandwidthData.append(MetricPoint(timestamp: now, value: metrics.bandwidth))
        latencyData.append(MetricPoint(timestamp: now, value: metrics.latency))
        packetLossData.append(MetricPoint(timestamp: now, value: metrics.packetLoss))
        
        // Limit the number of data points
        if bandwidthData.count > maxDataPoints {
            bandwidthData.removeFirst()
            latencyData.removeFirst()
            packetLossData.removeFirst()
        }
    }
}

struct LegendItem: View {
    let color: Color
    let label: String
    
    var body: some View {
        HStack(spacing: 4) {
            Circle()
                .fill(color)
                .frame(width: 8, height: 8)
            Text(label)
                .font(.caption)
                .foregroundColor(.secondary)
        }
    }
}

#Preview {
    MetricsGraphView()
} 