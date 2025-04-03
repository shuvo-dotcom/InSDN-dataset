import SwiftUI

struct TopologyData {
    struct Link {
        let source: String
        let destination: String
        let bandwidth: Int
    }
    
    let nodes: [String: String]
    let links: [Link]
}

struct TopologyView: View {
    @State private var nodes: [String] = []
    @State private var links: [TopologyLink] = []
    @State private var nodePositions: [String: CGPoint] = [:]
    private let nodeRadius: CGFloat = 40
    
    struct TopologyLink: Identifiable {
        let id = UUID()
        let source: String
        let target: String
        let bandwidth: Int
    }
    
    var body: some View {
        GeometryReader { geometry in
            ZStack {
                // Draw links
                ForEach(links) { link in
                    if let sourcePos = nodePositions[link.source],
                       let targetPos = nodePositions[link.target] {
                        Path { path in
                            path.move(to: sourcePos)
                            path.addLine(to: targetPos)
                        }
                        .stroke(Color.gray, lineWidth: 2)
                        
                        // Draw bandwidth text
                        Text("\(link.bandwidth) Mbps")
                            .font(.caption)
                            .position(
                                x: (sourcePos.x + targetPos.x) / 2,
                                y: (sourcePos.y + targetPos.y) / 2 - 10
                            )
                    }
                }
                
                // Draw nodes
                ForEach(nodes, id: \.self) { node in
                    if let position = nodePositions[node] {
                        Circle()
                            .fill(Color.blue)
                            .frame(width: nodeRadius * 2, height: nodeRadius * 2)
                            .position(position)
                        
                        Text(node)
                            .foregroundColor(.white)
                            .position(position)
                    }
                }
            }
            .onAppear {
                calculateNodePositions(in: geometry.size)
            }
            .onChange(of: geometry.size) { newSize in
                calculateNodePositions(in: newSize)
            }
        }
        .background(Color(.systemBackground))
        .cornerRadius(12)
        .shadow(radius: 4)
    }
    
    private func calculateNodePosititions(in size: CGSize) {
        let centerX = size.width / 2
        let centerY = size.height / 2
        let radius = min(centerX, centerY) - nodeRadius - 20
        
        nodePositions.removeAll()
        
        for (index, node) in nodes.enumerated() {
            let angle = 2 * Double.pi * Double(index) / Double(nodes.count)
            let x = centerX + radius * cos(angle)
            let y = centerY + radius * sin(angle)
            nodePositions[node] = CGPoint(x: x, y: y)
        }
    }
    
    func updateTopology(_ topology: TopologyData) {
        nodes = Array(topology.nodes.keys)
        links = topology.links.map { link in
            TopologyLink(
                source: link.source,
                target: link.destination,
                bandwidth: link.bandwidth
            )
        }
    }
} 