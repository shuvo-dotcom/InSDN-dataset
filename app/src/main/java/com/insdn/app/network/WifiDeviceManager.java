package com.insdn.app.network;

import android.content.Context;
import android.net.wifi.WifiManager;
import android.net.wifi.WifiInfo;
import android.net.DhcpInfo;
import android.os.Handler;
import android.os.Looper;
import java.util.ArrayList;
import java.util.List;

public class WifiDeviceManager {
    private final Context context;
    private final WifiManager wifiManager;
    private final Handler handler;
    private DeviceListener deviceListener;
    private boolean isScanning = false;
    private static final long SCAN_INTERVAL = 5000; // 5 seconds

    public interface DeviceListener {
        void onDevicesFound(List<WifiDevice> devices);
        void onError(String error);
    }

    public static class WifiDevice {
        private final String name;
        private final String ipAddress;
        private final String macAddress;
        private final String connectionType;

        public WifiDevice(String name, String ipAddress, String macAddress, String connectionType) {
            this.name = name;
            this.ipAddress = ipAddress;
            this.macAddress = macAddress;
            this.connectionType = connectionType;
        }

        public String getName() { return name; }
        public String getIpAddress() { return ipAddress; }
        public String getMacAddress() { return macAddress; }
        public String getConnectionType() { return connectionType; }
    }

    public WifiDeviceManager(Context context) {
        this.context = context;
        this.wifiManager = (WifiManager) context.getApplicationContext().getSystemService(Context.WIFI_SERVICE);
        this.handler = new Handler(Looper.getMainLooper());
    }

    public void setDeviceListener(DeviceListener listener) {
        this.deviceListener = listener;
    }

    public void startScanning() {
        if (!isScanning) {
            isScanning = true;
            scanDevices();
        }
    }

    public void stopScanning() {
        isScanning = false;
        handler.removeCallbacksAndMessages(null);
    }

    private void scanDevices() {
        if (!isScanning) return;

        List<WifiDevice> devices = new ArrayList<>();

        try {
            // Get current WiFi connection info
            WifiInfo wifiInfo = wifiManager.getConnectionInfo();
            if (wifiInfo != null && wifiInfo.getNetworkId() != -1) {
                String deviceName = wifiInfo.getSSID().replace("\"", "");
                String ipAddress = intToIp(wifiInfo.getIpAddress());
                String macAddress = wifiInfo.getMacAddress();
                
                // Add connected device info
                devices.add(new WifiDevice(
                    deviceName,
                    ipAddress,
                    macAddress != null ? macAddress : "Unknown",
                    "WiFi"
                ));

                // Get DHCP info
                DhcpInfo dhcpInfo = wifiManager.getDhcpInfo();
                if (dhcpInfo != null) {
                    // Add gateway device
                    devices.add(new WifiDevice(
                        "Gateway",
                        intToIp(dhcpInfo.gateway),
                        "Unknown",
                        "Router"
                    ));
                }
            }

            if (deviceListener != null) {
                deviceListener.onDevicesFound(devices);
            }
        } catch (Exception e) {
            if (deviceListener != null) {
                deviceListener.onError("Error scanning devices: " + e.getMessage());
            }
        }

        // Schedule next scan
        handler.postDelayed(this::scanDevices, SCAN_INTERVAL);
    }

    private String intToIp(int ip) {
        return String.format("%d.%d.%d.%d",
            (ip & 0xff),
            (ip >> 8 & 0xff),
            (ip >> 16 & 0xff),
            (ip >> 24 & 0xff));
    }
} 