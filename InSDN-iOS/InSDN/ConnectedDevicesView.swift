import SwiftUI

struct ConnectedDevicesView: View {
    @State private var devices: [NetworkManager.ConnectedDevice] = []
    @State private var errorMessage: String?
    
    private let columns = [
        GridItem(.flexible(minimum: 100), spacing: 10),
        GridItem(.flexible(minimum: 100), spacing: 10),
        GridItem(.flexible(minimum: 100), spacing: 10),
        GridItem(.flexible(minimum: 80), spacing: 10)
    ]
    
    var body: some View {
        VStack {
            // Header
            LazyVGrid(columns: columns, spacing: 10) {
                Text("Device Name")
                    .font(.headline)
                Text("IP Address")
                    .font(.headline)
                Text("MAC Address")
                    .font(.headline)
                Text("Type")
                    .font(.headline)
            }
            .padding()
            .background(Color.blue)
            .foregroundColor(.white)
            
            // Device List
            ScrollView {
                LazyVStack(spacing: 0) {
                    ForEach(devices, id: \.ipAddress) { device in
                        DeviceRow(device: device)
                            .padding(.vertical, 8)
                        Divider()
                    }
                }
            }
            
            if let error = errorMessage {
                Text(error)
                    .foregroundColor(.red)
                    .padding()
            }
        }
        .onAppear {
            setupNetworkManager()
        }
    }
    
    private func setupNetworkManager() {
        NetworkManager.shared.connectedDevicesHandler = { devices in
            self.devices = devices
        }
        
        NetworkManager.shared.errorHandler = { error in
            self.errorMessage = error
        }
        
        NetworkManager.shared.startMonitoring()
    }
}

struct DeviceRow: View {
    let device: NetworkManager.ConnectedDevice
    
    var body: some View {
        LazyVGrid(columns: [
            GridItem(.flexible(minimum: 100), spacing: 10),
            GridItem(.flexible(minimum: 100), spacing: 10),
            GridItem(.flexible(minimum: 100), spacing: 10),
            GridItem(.flexible(minimum: 80), spacing: 10)
        ], spacing: 10) {
            Text(device.name)
                .lineLimit(1)
            Text(device.ipAddress)
                .lineLimit(1)
            Text(device.macAddress)
                .lineLimit(1)
            Text(device.connectionType)
                .lineLimit(1)
        }
        .padding(.horizontal)
    }
}

#Preview {
    ConnectedDevicesView()
} 