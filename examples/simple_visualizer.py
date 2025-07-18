#!/usr/bin/env python3
"""
Simple Text-based Visualization for Stress Test Results
Creates ASCII charts and exports data for external plotting tools
"""

import math
import statistics
from typing import List, Tuple, Optional

class SimpleVisualizer:
    """Create simple text-based visualizations"""
    
    @staticmethod
    def create_histogram(data: List[float], title: str, bins: int = 20, width: int = 60) -> str:
        """Create ASCII histogram"""
        if not data:
            return f"{title}\n(No data to display)"
        
        min_val, max_val = min(data), max(data)
        if min_val == max_val:
            return f"{title}\nAll values: {min_val:.3f}"
        
        # Create bins
        bin_width = (max_val - min_val) / bins
        bin_counts = [0] * bins
        
        for value in data:
            bin_idx = min(int((value - min_val) / bin_width), bins - 1)
            bin_counts[bin_idx] += 1
        
        # Scale to display width
        max_count = max(bin_counts)
        scale = width / max_count if max_count > 0 else 1
        
        # Build histogram
        result = [f"\n{title}"]
        result.append("─" * (width + 20))
        
        for i, count in enumerate(bin_counts):
            bin_start = min_val + i * bin_width
            bin_end = bin_start + bin_width
            bar_length = int(count * scale)
            bar = "█" * bar_length
            
            result.append(f"{bin_start:8.3f}-{bin_end:8.3f} │{bar:<{width}} │ {count:4d}")
        
        result.append("─" * (width + 20))
        result.append(f"Total samples: {len(data)}")
        result.append(f"Range: {min_val:.3f} - {max_val:.3f}")
        result.append(f"Mean: {statistics.mean(data):.3f}")
        
        return "\n".join(result)
    
    @staticmethod
    def create_time_series(data: List[float], timestamps: List[float], 
                          title: str, width: int = 80, height: int = 20) -> str:
        """Create ASCII time series plot"""
        if not data or len(data) != len(timestamps):
            return f"{title}\n(No data to display)"
        
        if len(data) < 2:
            return f"{title}\nInsufficient data for time series"
        
        # Normalize timestamps to start from 0
        start_time = min(timestamps)
        norm_times = [(t - start_time) for t in timestamps]
        
        min_val, max_val = min(data), max(data)
        min_time, max_time = min(norm_times), max(norm_times)
        
        if min_val == max_val:
            return f"{title}\nConstant value: {min_val:.3f}"
        
        # Create 2D grid
        grid = [[' ' for _ in range(width)] for _ in range(height)]
        
        # Plot points
        for i, (time_val, data_val) in enumerate(zip(norm_times, data)):
            x = int((time_val - min_time) / (max_time - min_time) * (width - 1))
            y = int((1 - (data_val - min_val) / (max_val - min_val)) * (height - 1))
            
            if 0 <= x < width and 0 <= y < height:
                grid[y][x] = '●'
        
        # Build output
        result = [f"\n{title}"]
        result.append("─" * width)
        
        # Y-axis labels and plot
        for i, row in enumerate(grid):
            y_val = max_val - (i / (height - 1)) * (max_val - min_val)
            y_label = f"{y_val:8.3f} │"
            result.append(y_label + "".join(row))
        
        # X-axis
        result.append(" " * 10 + "─" * width)
        x_labels = f"{'0.000':>10} {'':<{width-16}} {max_time:>8.3f}"
        result.append(x_labels)
        result.append(f"{'':>10} Time (seconds)")
        
        return "\n".join(result)
    
    @staticmethod
    def create_comparison_chart(serial_data: List[float], modbus_data: List[float], 
                               title: str, unit: str = "") -> str:
        """Create side-by-side comparison"""
        if not serial_data and not modbus_data:
            return f"{title}\n(No data to compare)"
        
        result = [f"\n{title}"]
        result.append("=" * 60)
        
        # Calculate statistics for both
        if serial_data:
            serial_stats = {
                'count': len(serial_data),
                'mean': statistics.mean(serial_data),
                'min': min(serial_data),
                'max': max(serial_data),
                'std': statistics.stdev(serial_data) if len(serial_data) > 1 else 0
            }
        else:
            serial_stats = {'count': 0, 'mean': 0, 'min': 0, 'max': 0, 'std': 0}
        
        if modbus_data:
            modbus_stats = {
                'count': len(modbus_data),
                'mean': statistics.mean(modbus_data),
                'min': min(modbus_data),
                'max': max(modbus_data),
                'std': statistics.stdev(modbus_data) if len(modbus_data) > 1 else 0
            }
        else:
            modbus_stats = {'count': 0, 'mean': 0, 'min': 0, 'max': 0, 'std': 0}
        
        # Format comparison table
        result.append(f"{'Metric':<15} {'Serial':<15} {'Modbus':<15} {'Winner':<10}")
        result.append("─" * 60)
        
        # Sample count
        result.append(f"{'Samples':<15} {serial_stats['count']:<15} {modbus_stats['count']:<15} {'─':<10}")
        
        # Mean comparison
        if serial_stats['count'] > 0 and modbus_stats['count'] > 0:
            mean_winner = "Serial" if serial_stats['mean'] < modbus_stats['mean'] else "Modbus"
        else:
            mean_winner = "Serial" if serial_stats['count'] > 0 else "Modbus" if modbus_stats['count'] > 0 else "─"
        
        result.append(f"{'Mean ' + unit:<15} {serial_stats['mean']:<15.3f} {modbus_stats['mean']:<15.3f} {mean_winner:<10}")
        
        # Min comparison
        if serial_stats['count'] > 0 and modbus_stats['count'] > 0:
            min_winner = "Serial" if serial_stats['min'] < modbus_stats['min'] else "Modbus"
        else:
            min_winner = "─"
        
        result.append(f"{'Min ' + unit:<15} {serial_stats['min']:<15.3f} {modbus_stats['min']:<15.3f} {min_winner:<10}")
        
        # Max comparison
        if serial_stats['count'] > 0 and modbus_stats['count'] > 0:
            max_winner = "Serial" if serial_stats['max'] < modbus_stats['max'] else "Modbus"
        else:
            max_winner = "─"
        
        result.append(f"{'Max ' + unit:<15} {serial_stats['max']:<15.3f} {modbus_stats['max']:<15.3f} {max_winner:<10}")
        
        # Std dev comparison
        if serial_stats['count'] > 1 and modbus_stats['count'] > 1:
            std_winner = "Serial" if serial_stats['std'] < modbus_stats['std'] else "Modbus"
        else:
            std_winner = "─"
        
        result.append(f"{'Std Dev ' + unit:<15} {serial_stats['std']:<15.3f} {modbus_stats['std']:<15.3f} {std_winner:<10}")
        
        return "\n".join(result)
    
    @staticmethod
    def export_csv_data(serial_metrics, modbus_metrics, filename: str = "stress_test_data.csv"):
        """Export data to CSV for external plotting tools"""
        try:
            with open(filename, 'w') as f:
                # Header
                f.write("interface,timestamp,latency_ms,throughput_bps,success\n")
                
                # Serial data
                for i, (ts, lat, thr) in enumerate(zip(
                    serial_metrics.timestamps, 
                    serial_metrics.latencies, 
                    serial_metrics.throughput_bps
                )):
                    f.write(f"serial,{ts},{lat*1000},{thr},1\n")
                
                # Modbus data
                for i, (ts, lat, thr) in enumerate(zip(
                    modbus_metrics.timestamps, 
                    modbus_metrics.latencies, 
                    modbus_metrics.throughput_bps
                )):
                    f.write(f"modbus,{ts},{lat*1000},{thr},1\n")
            
            print(f"📊 Data exported to {filename}")
            print(f"   Use Excel, Python, or R to create advanced plots")
            
        except Exception as e:
            print(f"❌ Failed to export CSV: {e}")

class EnhancedReporter:
    """Enhanced reporting with text-based visualizations"""
    
    def __init__(self, serial_metrics, modbus_metrics):
        self.serial_metrics = serial_metrics
        self.modbus_metrics = modbus_metrics
        self.visualizer = SimpleVisualizer()
    
    def generate_visual_report(self):
        """Generate comprehensive report with ASCII visualizations"""
        print("\n" + "="*80)
        print("VISUAL STRESS TEST REPORT")
        print("="*80)
        
        # 1. Latency histograms
        if self.serial_metrics.latencies:
            latency_ms = [l * 1000 for l in self.serial_metrics.latencies]
            print(self.visualizer.create_histogram(
                latency_ms, "Serial Interface - Latency Distribution (ms)", bins=15
            ))
        
        if self.modbus_metrics.latencies:
            latency_ms = [l * 1000 for l in self.modbus_metrics.latencies]
            print(self.visualizer.create_histogram(
                latency_ms, "Modbus Interface - Latency Distribution (ms)", bins=15
            ))
        
        # 2. Latency comparison
        serial_latencies_ms = [l * 1000 for l in self.serial_metrics.latencies]
        modbus_latencies_ms = [l * 1000 for l in self.modbus_metrics.latencies]
        
        print(self.visualizer.create_comparison_chart(
            serial_latencies_ms, modbus_latencies_ms, 
            "LATENCY COMPARISON", "ms"
        ))
        
        # 3. Throughput comparison
        print(self.visualizer.create_comparison_chart(
            self.serial_metrics.throughput_bps, self.modbus_metrics.throughput_bps,
            "THROUGHPUT COMPARISON", "bytes/s"
        ))
        
        # 4. Time series (if sufficient data)
        if len(self.serial_metrics.latencies) > 10:
            serial_latencies_ms = [l * 1000 for l in self.serial_metrics.latencies]
            print(self.visualizer.create_time_series(
                serial_latencies_ms, self.serial_metrics.timestamps,
                "Serial Interface - Latency Over Time (ms)"
            ))
        
        if len(self.modbus_metrics.latencies) > 10:
            modbus_latencies_ms = [l * 1000 for l in self.modbus_metrics.latencies]
            print(self.visualizer.create_time_series(
                modbus_latencies_ms, self.modbus_metrics.timestamps,
                "Modbus Interface - Latency Over Time (ms)"
            ))
        
        # 5. Performance summary box
        self._print_summary_box()
        
        # 6. Export data for external tools
        self.visualizer.export_csv_data(self.serial_metrics, self.modbus_metrics)
        
        # 7. Advanced plotting suggestions
        self._print_plotting_suggestions()
    
    def _print_summary_box(self):
        """Print a neat summary box"""
        print("\n┌─ PERFORMANCE SUMMARY " + "─" * 50 + "┐")
        
        # Calculate key metrics
        if self.serial_metrics.latencies and self.modbus_metrics.latencies:
            serial_avg = statistics.mean(self.serial_metrics.latencies) * 1000
            modbus_avg = statistics.mean(self.modbus_metrics.latencies) * 1000
            
            faster_interface = "Serial" if serial_avg < modbus_avg else "Modbus"
            speed_diff = abs(serial_avg - modbus_avg)
            
            print(f"│ 🏆 Faster Interface: {faster_interface:<20} (by {speed_diff:.1f}ms) │")
        
        if self.serial_metrics.success_count and self.modbus_metrics.success_count:
            total_ops = (self.serial_metrics.success_count + self.serial_metrics.error_count + 
                        self.modbus_metrics.success_count + self.modbus_metrics.error_count)
            
            print(f"│ 📊 Total Operations: {total_ops:<30} │")
            
            serial_rate = self.serial_metrics.operations_per_second
            modbus_rate = self.modbus_metrics.operations_per_second
            
            print(f"│ ⚡ Serial Rate: {serial_rate:.1f} ops/sec {'':<18} │")
            print(f"│ ⚡ Modbus Rate: {modbus_rate:.1f} ops/sec {'':<18} │")
        
        # Overall assessment
        overall_errors = self.serial_metrics.error_count + self.modbus_metrics.error_count
        overall_success = self.serial_metrics.success_count + self.modbus_metrics.success_count
        
        if overall_success > 0:
            error_rate = overall_errors / (overall_errors + overall_success)
            
            if error_rate < 0.01:
                assessment = "✅ Excellent"
            elif error_rate < 0.05:
                assessment = "⚠️  Good"
            else:
                assessment = "❌ Poor"
            
            print(f"│ 🎯 Assessment: {assessment:<30} │")
        
        print("└" + "─" * 70 + "┘")
    
    def _print_plotting_suggestions(self):
        """Suggest external plotting tools and commands"""
        print("\n📈 ADVANCED PLOTTING SUGGESTIONS")
        print("─" * 50)
        print("For publication-quality plots, use the exported CSV data with:")
        print()
        print("🐍 Python (matplotlib/seaborn):")
        print("   import pandas as pd")
        print("   df = pd.read_csv('stress_test_data.csv')")
        print("   df.boxplot(column='latency_ms', by='interface')")
        print()
        print("📊 R (ggplot2):")
        print("   library(ggplot2)")
        print("   data <- read.csv('stress_test_data.csv')")
        print("   ggplot(data, aes(x=interface, y=latency_ms)) + geom_boxplot()")
        print()
        print("📋 Excel:")
        print("   Import CSV → Insert Chart → Scatter Plot with Smooth Lines")
        print()
        print("🌐 Online Tools:")
        print("   - Plot.ly: Upload CSV for interactive plots")
        print("   - Google Sheets: Import and use built-in charting")

if __name__ == "__main__":
    # Example usage
    print("Simple Visualization Utilities for Stress Test Results")
    print("This module provides ASCII-based charts and data export functionality")
    print("Import this module in your stress test scripts for enhanced reporting")
