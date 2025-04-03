package com.insdn.app.ui;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.util.AttributeSet;
import android.view.View;
import com.insdn.app.network.WifiDeviceManager.WifiDevice;
import java.util.ArrayList;
import java.util.List;

public class ConnectedDevicesView extends View {
    private final Paint headerPaint;
    private final Paint rowPaint;
    private final Paint textPaint;
    private final Paint linePaint;
    private final List<WifiDevice> devices;
    private final float rowHeight = 40f;
    private final float padding = 16f;
    private final String[] headers = {"Device Name", "IP Address", "MAC Address", "Type"};
    private final float[] columnWidths = {0.3f, 0.25f, 0.25f, 0.2f};

    public ConnectedDevicesView(Context context) {
        this(context, null);
    }

    public ConnectedDevicesView(Context context, AttributeSet attrs) {
        this(context, attrs, 0);
    }

    public ConnectedDevicesView(Context context, AttributeSet attrs, int defStyleAttr) {
        super(context, attrs, defStyleAttr);

        headerPaint = new Paint();
        headerPaint.setColor(Color.rgb(33, 150, 243));
        headerPaint.setStyle(Paint.Style.FILL);

        rowPaint = new Paint();
        rowPaint.setColor(Color.WHITE);
        rowPaint.setStyle(Paint.Style.FILL);

        textPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        textPaint.setColor(Color.BLACK);
        textPaint.setTextSize(16f);
        textPaint.setTextAlign(Paint.Align.LEFT);

        linePaint = new Paint();
        linePaint.setColor(Color.LTGRAY);
        linePaint.setStyle(Paint.Style.STROKE);
        linePaint.setStrokeWidth(1f);

        devices = new ArrayList<>();
    }

    public void updateDevices(List<WifiDevice> newDevices) {
        devices.clear();
        devices.addAll(newDevices);
        invalidate();
    }

    @Override
    protected void onDraw(Canvas canvas) {
        super.onDraw(canvas);

        float width = getWidth();
        float currentY = 0;

        // Draw header
        canvas.drawRect(0, currentY, width, rowHeight, headerPaint);
        
        // Draw header text
        textPaint.setColor(Color.WHITE);
        for (int i = 0; i < headers.length; i++) {
            float x = getColumnX(i, width);
            canvas.drawText(headers[i], x + padding, currentY + rowHeight - padding, textPaint);
            
            // Draw vertical lines
            if (i > 0) {
                canvas.drawLine(x, 0, x, getHeight(), linePaint);
            }
        }

        currentY += rowHeight;
        textPaint.setColor(Color.BLACK);

        // Draw rows
        for (WifiDevice device : devices) {
            // Draw row background
            canvas.drawRect(0, currentY, width, currentY + rowHeight, rowPaint);
            
            // Draw device data
            float x = padding;
            canvas.drawText(device.getName(), x, currentY + rowHeight - padding, textPaint);
            
            x = getColumnX(1, width) + padding;
            canvas.drawText(device.getIpAddress(), x, currentY + rowHeight - padding, textPaint);
            
            x = getColumnX(2, width) + padding;
            canvas.drawText(device.getMacAddress(), x, currentY + rowHeight - padding, textPaint);
            
            x = getColumnX(3, width) + padding;
            canvas.drawText(device.getConnectionType(), x, currentY + rowHeight - padding, textPaint);
            
            // Draw horizontal line
            canvas.drawLine(0, currentY, width, currentY, linePaint);
            
            currentY += rowHeight;
        }

        // Draw final horizontal line
        canvas.drawLine(0, currentY, width, currentY, linePaint);
        
        // Draw border
        canvas.drawRect(0, 0, width, getHeight(), linePaint);
    }

    private float getColumnX(int columnIndex, float totalWidth) {
        float x = 0;
        for (int i = 0; i < columnIndex; i++) {
            x += totalWidth * columnWidths[i];
        }
        return x;
    }
} 