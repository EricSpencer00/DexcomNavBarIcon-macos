import csv
import json
import os
from datetime import datetime, timedelta
import logging
from typing import List, Dict, Optional
import pandas as pd
import numpy as np

class GlucoseDataManager:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        self.data_file = os.path.join(data_dir, "glucose_data.csv")
        self._initialize_data_file()

    def _initialize_data_file(self):
        """Initialize the CSV file with headers if it doesn't exist."""
        if not os.path.exists(self.data_file):
            with open(self.data_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'value', 'trend_arrow'])

    def save_reading(self, value: float, trend_arrow: str):
        """Save a new glucose reading to the data file."""
        try:
            with open(self.data_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([datetime.now().isoformat(), value, trend_arrow])
        except Exception as e:
            logging.error(f"Error saving reading: {e}")

    def get_readings(self, hours: int = 24) -> pd.DataFrame:
        """Get glucose readings for the specified time period."""
        try:
            df = pd.read_csv(self.data_file)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            cutoff = datetime.now() - timedelta(hours=hours)
            return df[df['timestamp'] >= cutoff]
        except Exception as e:
            logging.error(f"Error getting readings: {e}")
            return pd.DataFrame()

    def calculate_statistics(self, hours: int = 24) -> Dict:
        """Calculate statistics for the specified time period."""
        df = self.get_readings(hours)
        if df.empty:
            return {}

        stats = {
            'average': df['value'].mean(),
            'min': df['value'].min(),
            'max': df['value'].max(),
            'std_dev': df['value'].std(),
            'time_in_range': self._calculate_time_in_range(df),
            'readings_count': len(df)
        }
        return stats

    def _calculate_time_in_range(self, df: pd.DataFrame, 
                               low: float = 70.0, 
                               high: float = 180.0) -> float:
        """Calculate percentage of time in range."""
        if df.empty:
            return 0.0
        in_range = ((df['value'] >= low) & (df['value'] <= high)).mean()
        return in_range * 100

    def export_data(self, format: str = 'csv', 
                   start_date: Optional[datetime] = None,
                   end_date: Optional[datetime] = None) -> str:
        """Export data in the specified format."""
        try:
            df = pd.read_csv(self.data_file)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            if start_date:
                df = df[df['timestamp'] >= start_date]
            if end_date:
                df = df[df['timestamp'] <= end_date]

            export_dir = os.path.join(self.data_dir, 'exports')
            if not os.path.exists(export_dir):
                os.makedirs(export_dir)

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            if format.lower() == 'csv':
                filename = os.path.join(export_dir, f'glucose_data_{timestamp}.csv')
                df.to_csv(filename, index=False)
            elif format.lower() == 'json':
                filename = os.path.join(export_dir, f'glucose_data_{timestamp}.json')
                df.to_json(filename, orient='records', date_format='iso')
            else:
                raise ValueError(f"Unsupported export format: {format}")

            return filename
        except Exception as e:
            logging.error(f"Error exporting data: {e}")
            return ""

    def cleanup_old_data(self, retention_days: int):
        """Remove data older than the specified retention period."""
        try:
            df = pd.read_csv(self.data_file)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            cutoff = datetime.now() - timedelta(days=retention_days)
            df = df[df['timestamp'] >= cutoff]
            df.to_csv(self.data_file, index=False)
        except Exception as e:
            logging.error(f"Error cleaning up old data: {e}")

    def get_trend_analysis(self, hours: int = 24) -> Dict:
        """Analyze glucose trends over time."""
        df = self.get_readings(hours)
        if df.empty:
            return {}

        # Calculate rate of change
        df['time_diff'] = df['timestamp'].diff().dt.total_seconds() / 60  # minutes
        df['value_diff'] = df['value'].diff()
        df['rate_of_change'] = df['value_diff'] / df['time_diff']

        analysis = {
            'average_rate_of_change': df['rate_of_change'].mean(),
            'max_rate_of_change': df['rate_of_change'].max(),
            'min_rate_of_change': df['rate_of_change'].min(),
            'trend_direction': self._determine_trend_direction(df),
            'volatility': df['value'].std()
        }
        return analysis

    def _determine_trend_direction(self, df: pd.DataFrame) -> str:
        """Determine the overall trend direction."""
        if df.empty:
            return "unknown"
        
        # Calculate the slope of a linear regression
        x = np.arange(len(df))
        y = df['value'].values
        slope = np.polyfit(x, y, 1)[0]
        
        if slope > 0.5:
            return "rising"
        elif slope < -0.5:
            return "falling"
        else:
            return "stable" 