package com.insdn.app.ui;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.Path;
import android.util.AttributeSet;
import android.view.View;
import java.util.ArrayList;
import java.util.List;

public class MetricsGraphView extends View {
    private static final int MAX_DATA_POINTS = 50;
    private static final float LINE_WIDTH = 3f;
    private static final float TEXT_SIZE = 30f;
    private static final int BANDWIDTH_COLOR = Color.BLUE;
    private static final int LATENCY_COLOR = Color.RED;
    private static final int PACKET_LOSS_COLOR = Color.GREEN;

    private final Paint bandwidthPaint;
    private final Paint latencyPaint;
    private final Paint packetLossPaint;
    private final Paint textPaint;
    private final Path bandwidthPath;
    private final Path latencyPath;
    private final Path packetLossPath;

    private final List<DataPoint> dataPoints;
    private float maxBandwidth = 100f;
    private float maxLatency = 100f;
    private float maxPacketLoss = 100f;

    private static class DataPoint {
        final float bandwidth;
        final float latency;
        final float packetLoss;

        DataPoint(float bandwidth, float latency, float packetLoss) {
            this.bandwidth = bandwidth;
            this.latency = latency;
            this.packetLoss = packetLoss;
        }
    }

    public MetricsGraphView(Context context) {
        this(context, null);
    }

    public MetricsGraphView(Context context, AttributeSet attrs) {
        this(context, attrs, 0);
    }

    public MetricsGraphView(Context context, AttributeSet attrs, int defStyleAttr) {
        super(context, attrs, defStyleAttr);

        bandwidthPaint = new Paint();
        bandwidthPaint.setColor(BANDWIDTH_COLOR);
        bandwidthPaint.setStyle(Paint.Style.STROKE);
        bandwidthPaint.setStrokeWidth(LINE_WIDTH);

        latencyPaint = new Paint();
        latencyPaint.setColor(LATENCY_COLOR);
        latencyPaint.setStyle(Paint.Style.STROKE);
        latencyPaint.setStrokeWidth(LINE_WIDTH);

        packetLossPaint = new Paint();
        packetLossPaint.setColor(PACKET_LOSS_COLOR);
        packetLossPaint.setStyle(Paint.Style.STROKE);
        packetLossPaint.setStrokeWidth(LINE_WIDTH);

        textPaint = new Paint();
        textPaint.setColor(Color.BLACK);
        textPaint.setTextSize(TEXT_SIZE);
        textPaint.setTextAlign(Paint.Align.LEFT);

        bandwidthPath = new Path();
        latencyPath = new Path();
        packetLossPath = new Path();

        dataPoints = new ArrayList<>();
    }

    public void addDataPoint(float bandwidth, float latency, float packetLoss) {
        dataPoints.add(new DataPoint(bandwidth, latency, packetLoss));
        
        // Update max values
        maxBandwidth = Math.max(maxBandwidth, bandwidth);
        maxLatency = Math.max(maxLatency, latency);
        maxPacketLoss = Math.max(maxPacketLoss, packetLoss);

        // Remove old data points if exceeding maximum
        while (dataPoints.size() > MAX_DATA_POINTS) {
            dataPoints.remove(0);
        }

        invalidate();
    }

    @Override
    protected void onDraw(Canvas canvas) {
        super.onDraw(canvas);
        drawGraph(canvas);
        drawLegend(canvas);
    }

    private void drawGraph(Canvas canvas) {
        if (dataPoints.isEmpty()) return;

        float width = getWidth();
        float height = getHeight();
        float padding = 50f;
        float graphWidth = width - 2 * padding;
        float graphHeight = height - 2 * padding;

        // Clear paths
        bandwidthPath.reset();
        latencyPath.reset();
        packetLossPath.reset();

        // Calculate x step
        float xStep = graphWidth / (MAX_DATA_POINTS - 1);

        // Draw each metric
        for (int i = 0; i < dataPoints.size(); i++) {
            DataPoint point = dataPoints.get(i);
            float x = padding + i * xStep;
            
            // Calculate y values (inverted because y=0 is at top)
            float bandwidthY = height - padding - (point.bandwidth / maxBandwidth * graphHeight);
            float latencyY = height - padding - (point.latency / maxLatency * graphHeight);
            float packetLossY = height - padding - (point.packetLoss / maxPacketLoss * graphHeight);

            // Move to first point or line to subsequent points
            if (i == 0) {
                bandwidthPath.moveTo(x, bandwidthY);
                latencyPath.moveTo(x, latencyY);
                packetLossPath.moveTo(x, packetLossY);
            } else {
                bandwidthPath.lineTo(x, bandwidthY);
                latencyPath.lineTo(x, latencyY);
                packetLossPath.lineTo(x, packetLossY);
            }
        }

        // Draw the paths
        canvas.drawPath(bandwidthPath, bandwidthPaint);
        canvas.drawPath(latencyPath, latencyPaint);
        canvas.drawPath(packetLossPath, packetLossPaint);
    }

    private void drawLegend(Canvas canvas) {
        float padding = 20f;
        float textSize = TEXT_SIZE;
        float y = padding + textSize;

        // Draw bandwidth legend
        textPaint.setColor(BANDWIDTH_COLOR);
        canvas.drawText("Bandwidth", padding, y, textPaint);

        // Draw latency legend
        textPaint.setColor(LATENCY_COLOR);
        canvas.drawText("Latency", padding + 200, y, textPaint);

        // Draw packet loss legend
        textPaint.setColor(PACKET_LOSS_COLOR);
        canvas.drawText("Packet Loss", padding + 400, y, textPaint);
    }
} 