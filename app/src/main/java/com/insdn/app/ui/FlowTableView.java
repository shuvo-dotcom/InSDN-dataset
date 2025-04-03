package com.insdn.app.ui;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.util.AttributeSet;
import android.view.View;
import com.insdn.app.network.NetworkMonitor.FlowEntry;
import java.util.ArrayList;
import java.util.List;

public class FlowTableView extends View {
    private static final float TEXT_SIZE = 30f;
    private static final float ROW_HEIGHT = 60f;
    private static final float PADDING = 10f;
    private static final int HEADER_COLOR = Color.BLUE;
    private static final int ROW_COLOR = Color.WHITE;
    private static final int TEXT_COLOR = Color.BLACK;

    private final Paint headerPaint;
    private final Paint rowPaint;
    private final Paint textPaint;
    private final List<FlowEntry> flowEntries;

    public FlowTableView(Context context) {
        this(context, null);
    }

    public FlowTableView(Context context, AttributeSet attrs) {
        this(context, attrs, 0);
    }

    public FlowTableView(Context context, AttributeSet attrs, int defStyleAttr) {
        super(context, attrs, defStyleAttr);

        headerPaint = new Paint();
        headerPaint.setColor(HEADER_COLOR);
        headerPaint.setStyle(Paint.Style.FILL);

        rowPaint = new Paint();
        rowPaint.setColor(ROW_COLOR);
        rowPaint.setStyle(Paint.Style.FILL);

        textPaint = new Paint();
        textPaint.setColor(TEXT_COLOR);
        textPaint.setTextSize(TEXT_SIZE);
        textPaint.setTextAlign(Paint.Align.LEFT);

        flowEntries = new ArrayList<>();
    }

    public void updateFlowTable(List<FlowEntry> entries) {
        flowEntries.clear();
        flowEntries.addAll(entries);
        invalidate();
    }

    @Override
    protected void onDraw(Canvas canvas) {
        super.onDraw(canvas);
        drawHeader(canvas);
        drawFlowEntries(canvas);
    }

    private void drawHeader(Canvas canvas) {
        float y = ROW_HEIGHT;
        canvas.drawRect(0, 0, getWidth(), y, headerPaint);
        
        textPaint.setColor(Color.WHITE);
        float textY = y - PADDING;
        
        // Draw header text
        canvas.drawText("Flow ID", PADDING, textY, textPaint);
        canvas.drawText("Source IP", getWidth() / 4f, textY, textPaint);
        canvas.drawText("Dest IP", getWidth() / 2f, textY, textPaint);
        canvas.drawText("Ports", 3 * getWidth() / 4f, textY, textPaint);
        canvas.drawText("Bandwidth", getWidth() - 100, textY, textPaint);
    }

    private void drawFlowEntries(Canvas canvas) {
        textPaint.setColor(TEXT_COLOR);
        float y = ROW_HEIGHT;

        for (FlowEntry entry : flowEntries) {
            // Draw row background
            canvas.drawRect(0, y, getWidth(), y + ROW_HEIGHT, rowPaint);
            
            // Draw entry details
            float textY = y + ROW_HEIGHT - PADDING;
            canvas.drawText(entry.getFlowId(), PADDING, textY, textPaint);
            canvas.drawText(entry.getSourceIp(), getWidth() / 4f, textY, textPaint);
            canvas.drawText(entry.getDestinationIp(), getWidth() / 2f, textY, textPaint);
            canvas.drawText(entry.getSourcePort() + "->" + entry.getDestinationPort(), 3 * getWidth() / 4f, textY, textPaint);
            canvas.drawText(entry.getBandwidth() + " Mbps", getWidth() - 100, textY, textPaint);

            y += ROW_HEIGHT;
        }
    }
} 