package com.insdn.app.ui;

import android.content.Context;
import android.util.AttributeSet;
import android.widget.LinearLayout;
import android.widget.TextView;
import com.insdn.app.R;

public class MetricsCardView extends LinearLayout {
    private TextView bandwidthText;
    private TextView latencyText;
    private TextView packetLossText;

    public MetricsCardView(Context context) {
        super(context);
        init(context);
    }

    public MetricsCardView(Context context, AttributeSet attrs) {
        super(context, attrs);
        init(context);
    }

    public MetricsCardView(Context context, AttributeSet attrs, int defStyleAttr) {
        super(context, attrs, defStyleAttr);
        init(context);
    }

    private void init(Context context) {
        inflate(context, R.layout.view_metrics_card, this);
        bandwidthText = findViewById(R.id.bandwidthText);
        latencyText = findViewById(R.id.latencyText);
        packetLossText = findViewById(R.id.packetLossText);
    }

    public void updateMetrics(float bandwidth, float latency, float packetLoss) {
        bandwidthText.setText(String.format("Bandwidth: %.2f Mbps", bandwidth));
        latencyText.setText(String.format("Latency: %.2f ms", latency));
        packetLossText.setText(String.format("Packet Loss: %.2f%%", packetLoss));
    }
} 