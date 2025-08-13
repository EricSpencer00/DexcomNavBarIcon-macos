from Cocoa import (
    NSAlert, NSInformationalAlertStyle, NSApp, NSButton,
    NSView, NSTextField, NSFont, NSColor, NSMakeRect,
    NSStackView, NSLayoutConstraint, NSLayoutAttributeTop,
    NSLayoutAttributeLeading, NSLayoutAttributeTrailing,
    NSImage, NSBitmapImageRep, NSImageRep
)
import logging
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import io
import numpy as np

class StatisticsView:
    def __init__(self, data_manager):
        self.data_manager = data_manager
        
    def show(self):
        alert = NSAlert.alloc().init()
        alert.setMessageText_("Glucose Statistics")
        alert.setInformativeText_("Your glucose data analysis")
        alert.setAlertStyle_(NSInformationalAlertStyle)
        
        # Create main view
        view = NSView.alloc().initWithFrame_(NSMakeRect(0, 0, 600, 700))
        
        # Create scroll view for content
        scroll_view = NSScrollView.alloc().initWithFrame_(NSMakeRect(0, 0, 600, 700))
        content_view = NSView.alloc().initWithFrame_(NSMakeRect(0, 0, 600, 1000))
        
        # Get statistics and data
        stats = self.data_manager.calculate_statistics()
        trend = self.data_manager.get_trend_analysis()
        df = self.data_manager.get_readings()
        
        # Create graph
        if not df.empty:
            graph_view = self._create_graph_view(df)
            content_view.addSubview_(graph_view)
        
        # Create sections
        sections = [
            ("Current Statistics", self._format_current_stats(stats)),
            ("Trend Analysis", self._format_trend_analysis(trend)),
            ("Time in Range", self._format_time_in_range(stats))
        ]
        
        y_offset = 400  # Start below the graph
        for title, content in sections:
            section_view = self._create_section(title, content, y_offset)
            content_view.addSubview_(section_view)
            y_offset += 150  # Space between sections
        
        scroll_view.setDocumentView_(content_view)
        view.addSubview_(scroll_view)
        alert.setAccessoryView_(view)
        
        # Add buttons
        alert.addButtonWithTitle_("Export Data")
        alert.addButtonWithTitle_("Close")
        
        response = alert.runModal()
        
        if response == 1000:  # Export Data button
            self._handle_export()
    
    def _create_graph_view(self, df):
        """Create a graph view of glucose readings."""
        # Create matplotlib figure
        plt.figure(figsize=(8, 4))
        plt.plot(df['timestamp'], df['value'], 'b-', label='Glucose')
        
        # Add target range
        plt.axhspan(70, 180, color='g', alpha=0.2, label='Target Range')
        
        # Customize the plot
        plt.title('Glucose Readings Over Time')
        plt.xlabel('Time')
        plt.ylabel('Glucose (mg/dL)')
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        # Rotate x-axis labels for better readability
        plt.xticks(rotation=45)
        
        # Adjust layout
        plt.tight_layout()
        
        # Convert plot to NSImage
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        plt.close()
        
        # Create NSImage from the buffer
        image_data = buf.getvalue()
        image_rep = NSBitmapImageRep.alloc().initWithData_(image_data)
        image = NSImage.alloc().initWithData_(image_rep.TIFFRepresentation())
        
        # Create image view
        image_view = NSImageView.alloc().initWithFrame_(NSMakeRect(0, 0, 600, 300))
        image_view.setImage_(image)
        image_view.setImageScaling_(NSImageScaleProportionallyDown)
        
        return image_view
    
    def _create_section(self, title, content, y_offset):
        """Create a section with title and content."""
        section = NSView.alloc().initWithFrame_(NSMakeRect(0, y_offset, 600, 120))
        
        # Title
        title_label = NSTextField.alloc().initWithFrame_(NSMakeRect(20, 100, 560, 20))
        title_label.setStringValue_(title)
        title_label.setEditable_(False)
        title_label.setBordered_(False)
        title_label.setBackgroundColor_(NSColor.clearColor())
        title_label.setFont_(NSFont.boldSystemFontOfSize_(14))
        
        # Content
        content_label = NSTextField.alloc().initWithFrame_(NSMakeRect(20, 0, 560, 90))
        content_label.setStringValue_(content)
        content_label.setEditable_(False)
        content_label.setBordered_(False)
        content_label.setBackgroundColor_(NSColor.clearColor())
        
        section.addSubview_(title_label)
        section.addSubview_(content_label)
        return section
    
    def _format_current_stats(self, stats):
        """Format current statistics for display."""
        if not stats:
            return "No data available"
        
        return f"""Average: {stats.get('average', 'N/A'):.1f}
Min: {stats.get('min', 'N/A'):.1f}
Max: {stats.get('max', 'N/A'):.1f}
Standard Deviation: {stats.get('std_dev', 'N/A'):.1f}
Total Readings: {stats.get('readings_count', 'N/A')}"""
    
    def _format_trend_analysis(self, trend):
        """Format trend analysis for display."""
        if not trend:
            return "No trend data available"
        
        return f"""Trend Direction: {trend.get('trend_direction', 'N/A').title()}
Average Rate of Change: {trend.get('average_rate_of_change', 'N/A'):.1f} mg/dL/min
Max Rate of Change: {trend.get('max_rate_of_change', 'N/A'):.1f} mg/dL/min
Min Rate of Change: {trend.get('min_rate_of_change', 'N/A'):.1f} mg/dL/min
Volatility: {trend.get('volatility', 'N/A'):.1f}"""
    
    def _format_time_in_range(self, stats):
        """Format time in range statistics."""
        if not stats:
            return "No time in range data available"
        
        return f"""Time in Range: {stats.get('time_in_range', 'N/A'):.1f}%
Target Range: 70-180 mg/dL"""
    
    def _handle_export(self):
        """Handle data export."""
        try:
            filename = self.data_manager.export_data()
            if filename:
                alert = NSAlert.alloc().init()
                alert.setMessageText_("Export Successful")
                alert.setInformativeText_(f"Data exported to: {filename}")
                alert.runModal()
            else:
                alert = NSAlert.alloc().init()
                alert.setMessageText_("Export Failed")
                alert.setInformativeText_("Failed to export data. Please check the logs.")
                alert.runModal()
        except Exception as e:
            logging.error(f"Error exporting data: {e}")
            alert = NSAlert.alloc().init()
            alert.setMessageText_("Export Error")
            alert.setInformativeText_(f"An error occurred: {str(e)}")
            alert.runModal() 