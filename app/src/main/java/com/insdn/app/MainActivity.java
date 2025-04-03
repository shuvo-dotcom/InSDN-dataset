package com.insdn.app;

import android.Manifest;
import android.content.pm.PackageManager;
import android.os.Bundle;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;
import com.insdn.app.ui.MetricsCardView;
import com.insdn.app.ui.MetricsGraphView;
import com.insdn.app.ui.TopologyView;
import com.insdn.app.ui.FlowTableView;
import com.insdn.app.ui.IntrusionDetectionView;
import com.insdn.app.network.NetworkMonitor;
import com.insdn.app.security.NetworkIntrusionDetector;
import com.insdn.app.wifi.WifiDeviceManager;
import java.util.ArrayList;
import java.util.List;

public class MainActivity extends AppCompatActivity implements NetworkMonitor.MetricsListener,
        NetworkMonitor.TopologyListener, NetworkMonitor.FlowTableListener,
        WifiDeviceManager.DeviceListener, NetworkIntrusionDetector.IntrusionDetectionCallback {
    
    private static final int PERMISSION_REQUEST_CODE = 1001;
    private static final String[] REQUIRED_PERMISSIONS = {
        Manifest.permission.ACCESS_FINE_LOCATION,
        Manifest.permission.ACCESS_COARSE_LOCATION,
        Manifest.permission.ACCESS_WIFI_STATE,
        Manifest.permission.CHANGE_WIFI_STATE
    };

    private MetricsCardView metricsCard;
    private MetricsGraphView metricsGraph;
    private TopologyView topologyView;
    private FlowTableView flowTableView;
    private IntrusionDetectionView intrusionDetectionView;
    private NetworkMonitor networkMonitor;
    private NetworkIntrusionDetector intrusionDetector;
    private WifiDeviceManager wifiDeviceManager;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // Initialize views
        metricsCard = findViewById(R.id.metricsCard);
        metricsGraph = findViewById(R.id.metricsGraph);
        topologyView = findViewById(R.id.topologyView);
        flowTableView = findViewById(R.id.flowTableView);
        intrusionDetectionView = findViewById(R.id.intrusionDetectionView);

        // Initialize network monitor
        networkMonitor = new NetworkMonitor();
        networkMonitor.setMetricsListener(this);
        networkMonitor.setTopologyListener(this);
        networkMonitor.setFlowTableListener(this);

        // Initialize intrusion detector
        intrusionDetector = new NetworkIntrusionDetector(this, networkMonitor);
        intrusionDetector.setCallback(this);

        // Initialize WiFi device manager
        wifiDeviceManager = new WifiDeviceManager(this);
        wifiDeviceManager.setListener(this);

        // Check and request permissions
        if (!hasRequiredPermissions()) {
            requestPermissions();
        } else {
            startMonitoring();
        }
    }

    private boolean hasRequiredPermissions() {
        for (String permission : REQUIRED_PERMISSIONS) {
            if (ContextCompat.checkSelfPermission(this, permission) != PackageManager.PERMISSION_GRANTED) {
                return false;
            }
        }
        return true;
    }

    private void requestPermissions() {
        ActivityCompat.requestPermissions(this, REQUIRED_PERMISSIONS, PERMISSION_REQUEST_CODE);
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == PERMISSION_REQUEST_CODE) {
            boolean allGranted = true;
            for (int result : grantResults) {
                if (result != PackageManager.PERMISSION_GRANTED) {
                    allGranted = false;
                    break;
                }
            }
            if (allGranted) {
                startMonitoring();
            } else {
                Toast.makeText(this, "Required permissions not granted", Toast.LENGTH_LONG).show();
            }
        }
    }

    private void startMonitoring() {
        networkMonitor.startMonitoring();
        wifiDeviceManager.startScanning();
        intrusionDetector.startMonitoring();
    }

    @Override
    public void onMetricsUpdate(float bandwidth, float latency, float packetLoss) {
        runOnUiThread(() -> {
            metricsCard.updateMetrics(bandwidth, latency, packetLoss);
            metricsGraph.addDataPoint(bandwidth, latency, packetLoss);
        });
    }

    @Override
    public void onTopologyUpdate(List<NetworkMonitor.Device> devices) {
        runOnUiThread(() -> topologyView.updateTopology(devices));
    }

    @Override
    public void onFlowTableUpdate(List<NetworkMonitor.FlowEntry> flows) {
        runOnUiThread(() -> flowTableView.updateFlowTable(flows));
    }

    @Override
    public void onDevicesFound(List<WifiDeviceManager.WifiDevice> devices) {
        // Update UI with found devices if needed
    }

    @Override
    public void onIntrusionDetected(NetworkIntrusionDetector.IntrusionEvent event) {
        runOnUiThread(() -> {
            intrusionDetectionView.showIntrusionDetected(event);
        });
    }

    @Override
    public void onNormalStatus() {
        runOnUiThread(() -> intrusionDetectionView.showNormalStatus());
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        if (networkMonitor != null) {
            networkMonitor.stopMonitoring();
        }
        if (wifiDeviceManager != null) {
            wifiDeviceManager.stopScanning();
        }
        if (intrusionDetector != null) {
            intrusionDetector.stopMonitoring();
        }
    }
} 