import SwiftUI

struct IntrusionDetectionView: View {
    @State private var statusText: String = "Normal Network Status"
    @State private var detailsText: String = ""
    @State private var timestampText: String = ""
    @State private var isIntrusionDetected: Bool = false
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(statusText)
                .font(.headline)
                .foregroundColor(isIntrusionDetected ? .red : .green)
            
            if isIntrusionDetected {
                Text(detailsText)
                    .font(.subheadline)
                    .foregroundColor(.primary)
            }
            
            Text(timestampText)
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .padding()
        .background(isIntrusionDetected ? Color.red.opacity(0.1) : Color.green.opacity(0.1))
        .cornerRadius(10)
        .padding()
    }
    
    func showIntrusionDetected(event: IntrusionEvent) {
        statusText = "INTRUSION DETECTED!"
        detailsText = String(format: "Protocol: %@\nConfidence: %.1f%%\nSource: %@:%d\nDestination: %@:%d\nDetails: %@",
                           event.protocol,
                           event.confidence * 100,
                           event.sourceIP,
                           event.sourcePort,
                           event.destinationIP,
                           event.destinationPort,
                           event.details)
        timestampText = formatTimestamp(event.timestamp)
        isIntrusionDetected = true
    }
    
    func showNormalStatus() {
        statusText = "Normal Network Status"
        detailsText = ""
        timestampText = formatTimestamp(Date().timeIntervalSince1970)
        isIntrusionDetected = false
    }
    
    private func formatTimestamp(_ timestamp: TimeInterval) -> String {
        let date = Date(timeIntervalSince1970: timestamp)
        let formatter = DateFormatter()
        formatter.dateFormat = "HH:mm:ss"
        return formatter.string(from: date)
    }
}

struct IntrusionEvent {
    let sourceIP: String
    let destinationIP: String
    let sourcePort: Int
    let destinationPort: Int
    let protocol: String
    let confidence: Float
    let details: String
    let timestamp: TimeInterval
} 