package com.insdn.app.ui;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.PointF;
import android.util.AttributeSet;
import android.view.View;
import com.insdn.app.network.NetworkMonitor.Device;
import com.insdn.app.network.NetworkMonitor.DeviceType;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class TopologyView extends View {
    private static final int SWITCH_COLOR = Color.BLUE;
    private static final int ROUTER_COLOR = Color.GREEN;
    private static final int HOST_COLOR = Color.RED;
    private static final int LINE_COLOR = Color.GRAY;
    private static final float NODE_RADIUS = 30f;
    private static final float TEXT_SIZE = 30f;

    private final Paint nodePaint;
    private final Paint linePaint;
    private final Paint textPaint;
    private final Map<String, PointF> nodePositions;
    private final List<Device> devices;

    public TopologyView(Context context) {
        this(context, null);
    }

    public TopologyView(Context context, AttributeSet attrs) {
        this(context, attrs, 0);
    }

    public TopologyView(Context context, AttributeSet attrs, int defStyleAttr) {
        super(context, attrs, defStyleAttr);

        nodePaint = new Paint();
        nodePaint.setStyle(Paint.Style.FILL);

        linePaint = new Paint();
        linePaint.setColor(LINE_COLOR);
        linePaint.setStyle(Paint.Style.STROKE);
        linePaint.setStrokeWidth(3f);

        textPaint = new Paint();
        textPaint.setColor(Color.BLACK);
        textPaint.setTextSize(TEXT_SIZE);
        textPaint.setTextAlign(Paint.Align.CENTER);

        nodePositions = new HashMap<>();
        devices = new ArrayList<>();
    }

    public void updateTopology(List<Device> newDevices) {
        devices.clear();
        devices.addAll(newDevices);
        calculateNodePositions();
        invalidate();
    }

    private void calculateNodePositions() {
        nodePositions.clear();
        int width = getWidth();
        int height = getHeight();
        int padding = 100;

        // Simple layout algorithm
        int numDevices = devices.size();
        if (numDevices == 0) return;

        float centerX = width / 2f;
        float centerY = height / 2f;
        float radius = Math.min(width, height) / 3f - padding;

        for (int i = 0; i < numDevices; i++) {
            double angle = 2 * Math.PI * i / numDevices;
            float x = centerX + (float) (radius * Math.cos(angle));
            float y = centerY + (float) (radius * Math.sin(angle));
            nodePositions.put(devices.get(i).getId(), new PointF(x, y));
        }
    }

    @Override
    protected void onDraw(Canvas canvas) {
        super.onDraw(canvas);
        drawConnections(canvas);
        drawNodes(canvas);
    }

    private void drawNodes(Canvas canvas) {
        for (Device device : devices) {
            PointF position = nodePositions.get(device.getId());
            if (position == null) continue;

            // Set node color based on device type
            switch (device.getType()) {
                case SWITCH:
                    nodePaint.setColor(SWITCH_COLOR);
                    break;
                case ROUTER:
                    nodePaint.setColor(ROUTER_COLOR);
                    break;
                case HOST:
                    nodePaint.setColor(HOST_COLOR);
                    break;
            }

            // Draw node
            canvas.drawCircle(position.x, position.y, NODE_RADIUS, nodePaint);

            // Draw device name
            canvas.drawText(device.getName(), position.x, position.y + NODE_RADIUS + TEXT_SIZE, textPaint);
        }
    }

    private void drawConnections(Canvas canvas) {
        // Draw connections between devices
        for (int i = 0; i < devices.size(); i++) {
            Device device1 = devices.get(i);
            PointF pos1 = nodePositions.get(device1.getId());
            if (pos1 == null) continue;

            for (int j = i + 1; j < devices.size(); j++) {
                Device device2 = devices.get(j);
                PointF pos2 = nodePositions.get(device2.getId());
                if (pos2 == null) continue;

                // Draw line between devices
                canvas.drawLine(pos1.x, pos1.y, pos2.x, pos2.y, linePaint);
            }
        }
    }
} 