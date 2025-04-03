package com.insdn.app.ui;

import android.content.Context;
import android.util.AttributeSet;
import android.widget.LinearLayout;
import android.widget.TextView;
import androidx.cardview.widget.CardView;
import com.insdn.app.R;
import com.insdn.app.security.NetworkIntrusionDetector.IntrusionEvent;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;

public class IntrusionDetectionView extends CardView {
    private TextView statusText;
    private TextView detailsText;
    private TextView timestampText;
    private SimpleDateFormat dateFormat;

    public IntrusionDetectionView(Context context) {
        super(context);
        init(context);
    }

    public IntrusionDetectionView(Context context, AttributeSet attrs) {
        super(context, attrs);
        init(context);
    }

    public IntrusionDetectionView(Context context, AttributeSet attrs, int defStyleAttr) {
        super(context, attrs, defStyleAttr);
        init(context);
    }

    private void init(Context context) {
        inflate(context, R.layout.view_intrusion_detection, this);
        statusText = findViewById(R.id.statusText);
        detailsText = findViewById(R.id.detailsText);
        timestampText = findViewById(R.id.timestampText);
        dateFormat = new SimpleDateFormat("HH:mm:ss", Locale.getDefault());
        showNormalStatus();
    }

    public void showIntrusionDetected(IntrusionEvent event) {
        statusText.setText("INTRUSION DETECTED!");
        statusText.setTextColor(getResources().getColor(android.R.color.holo_red_dark));
        detailsText.setVisibility(VISIBLE);
        detailsText.setText(String.format("Protocol: %s\nConfidence: %.1f%%\nSource: %s:%d\nDestination: %s:%d\nDetails: %s", 
            event.getProtocol(), 
            event.getConfidence() * 100,
            event.getSourceIP(),
            event.getSourcePort(),
            event.getDestinationIP(),
            event.getDestinationPort(),
            event.getDetails()));
        timestampText.setText(dateFormat.format(new Date(event.getTimestamp())));
        setCardBackgroundColor(getResources().getColor(android.R.color.holo_red_light));
    }

    public void showNormalStatus() {
        statusText.setText("Normal Network Status");
        statusText.setTextColor(getResources().getColor(android.R.color.holo_green_dark));
        detailsText.setVisibility(GONE);
        timestampText.setText(dateFormat.format(new Date()));
        setCardBackgroundColor(getResources().getColor(android.R.color.holo_green_light));
    }
} 