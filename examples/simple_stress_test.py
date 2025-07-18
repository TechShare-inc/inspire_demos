#!/usr/bin/env python3
"""
Simple Communication Throughput Stress Test
Core implementation without external plotting dependencies
"""

import asyncio
import time
import statistics
import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from datetime import datetime

from inspire_demos.inspire_modbus import InspireHandModbus
from inspire_demos.inspire_serial import InspireHandSerial

# Import matplotlib for plotting (optional)
try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

# Import visualization (optional)
try:
    from .simple_visualizer import EnhancedReporter
    VISUALIZATION_AVAILABLE = True
except ImportError:
    try:
        from simple_visualizer import EnhancedReporter
        VISUALIZATION_AVAILABLE = True
    except ImportError:
        VISUALIZATION_AVAILABLE = False

@dataclass
class SimpleMetrics:
    """Lightweight metrics container"""
    latencies: List[float] = field(default_factory=list)
    throughput_bps: List[float] = field(default_factory=list)
    error_count: int = 0
    success_count: int = 0
    timestamps: List[float] = field(default_factory=list)
    
    def record_result(self, latency: float, data_size: int, success: bool):
        """Record a single operation result"""
        timestamp = time.time()
        self.timestamps.append(timestamp)
        
        if success:
            self.latencies.append(latency)
            self.throughput_bps.append(data_size / latency if latency > 0 else 0)
            self.success_count += 1
        else:
            self.error_count += 1
    
    @property
    def total_operations(self) -> int:
        return self.success_count + self.error_count
    
    @property
    def success_rate(self) -> float:
        return self.success_count / self.total_operations if self.total_operations > 0 else 0
    
    @property
    def avg_latency_ms(self) -> float:
        return statistics.mean(self.latencies) * 1000 if self.latencies else 0
    
    @property
    def max_latency_ms(self) -> float:
        return max(self.latencies) * 1000 if self.latencies else 0
    
    @property
    def min_latency_ms(self) -> float:
        return min(self.latencies) * 1000 if self.latencies else 0
    
    @property
    def avg_throughput(self) -> float:
        return statistics.mean(self.throughput_bps) if self.throughput_bps else 0
    
    @property
    def operations_per_second(self) -> float:
        if len(self.timestamps) < 2:
            return 0
        duration = max(self.timestamps) - min(self.timestamps)
        return self.total_operations / duration if duration > 0 else 0

class SimpleThroughputTester:
    """
    Core stress testing functionality with integrated plotting capabilities
    
    This class provides comprehensive stress testing for both Serial and Modbus
    communication interfaces, including:
    - Basic latency measurement
    - Burst capacity testing  
    - Sustained load testing
    - Comprehensive reporting
    - Optional matplotlib plotting (if available)
    - CSV data export for external analysis
    
    Features:
    - Independent connection management per test
    - Graceful fallback when matplotlib is not available
    - Multiple visualization options (histograms, time series, box plots)
    - Performance comparison between interfaces
    """
    
    def __init__(self, serial_port: str = "COM3", modbus_ip: str = "192.168.11.210"):
        self.serial_hand = InspireHandSerial(port=serial_port, generation=4)
        self.modbus_hand = InspireHandModbus(ip=modbus_ip, generation=4)
        
        self.serial_metrics = SimpleMetrics()
        self.modbus_metrics = SimpleMetrics()
        
        # Test configurations
        self.test_commands = [
            np.array([0, 0, 0, 0, 200, 1000], dtype=np.int32),      # Open
            np.array([1000, 1000, 1000, 1000, 1000, 1000], dtype=np.int32),  # Close
            np.array([500, 500, 500, 500, 600, 1000], dtype=np.int32),  # Half
        ]
    
    async def test_serial_latency(self, iterations: int = 100):
        """Test Serial interface latency and throughput"""
        print(f"\n🔍 Testing Serial Interface ({iterations} iterations)")
        
        # Connect Serial interface for this test
        print("  🔌 Connecting Serial interface...")
        loop = asyncio.get_event_loop()
        serial_connected = await loop.run_in_executor(None, self.serial_hand.connect)
        
        if not serial_connected:
            print("  ❌ Failed to connect Serial interface!")
            return
        
        print("  ✅ Serial interface connected")
        
        try:
            cmd_idx = 0
            
            for i in range(iterations):
                start_time = time.time()
                
                try:
                    # Send command
                    command = self.test_commands[cmd_idx]
                    await loop.run_in_executor(None, self.serial_hand.set_angle, command)
                    
                    # Get response
                    response = await loop.run_in_executor(None, self.serial_hand.get_angle_actual)
                    
                    latency = time.time() - start_time
                    data_size = len(command) * 4 + len(response) * 4  # Estimated bytes
                    
                    self.serial_metrics.record_result(latency, data_size, True)
                    
                    if (i + 1) % 10 == 0:
                        print(f"  Progress: {i+1}/{iterations} | Last latency: {latency*1000:.1f}ms")
                    
                except Exception as e:
                    latency = time.time() - start_time
                    self.serial_metrics.record_result(latency, 0, False)
                    print(f"  Error {i+1}: {e}")
                
                cmd_idx = (cmd_idx + 1) % len(self.test_commands)
                
                # Small delay to avoid overwhelming the interface
                await asyncio.sleep(0.01)
        
        finally:
            # Always disconnect after test
            print("  🔌 Disconnecting Serial interface...")
            await loop.run_in_executor(None, self.serial_hand.disconnect)
            print("  ✅ Serial interface disconnected")
    
    async def test_modbus_latency(self, iterations: int = 100):
        """Test Modbus interface latency and throughput"""
        print(f"\n🔍 Testing Modbus Interface ({iterations} iterations)")
        
        # Connect Modbus interface for this test
        print("  🔌 Connecting Modbus interface...")
        loop = asyncio.get_event_loop()
        modbus_connected = await loop.run_in_executor(None, self.modbus_hand.connect)
        
        if not modbus_connected:
            print("  ❌ Failed to connect Modbus interface!")
            return
        
        print("  ✅ Modbus interface connected")
        
        try:
            # Different types of Modbus operations
            operations = [
                ("get_angle", lambda: self.modbus_hand.get_angle_actual()),
                ("get_tactile", lambda: self.modbus_hand.get_tactile_data()),
                ("get_temp", lambda: self.modbus_hand.get_temperature()),
            ]
            
            for i in range(iterations):
                start_time = time.time()
                
                try:
                    # Cycle through different operations
                    op_name, operation = operations[i % len(operations)]
                    data = await loop.run_in_executor(None, operation)
                    
                    latency = time.time() - start_time
                    
                    # Estimate data size based on operation type
                    if op_name == "get_angle" and data is not None:
                        data_size = len(data) * 4
                    elif op_name == "get_tactile" and data:
                        data_size = sum(sensor.nbytes for sensor in data.values())
                    elif op_name == "get_temp" and data is not None:
                        data_size = len(data) * 4
                    else:
                        data_size = 0
                    
                    self.modbus_metrics.record_result(latency, data_size, True)
                    
                    if (i + 1) % 10 == 0:
                        print(f"  Progress: {i+1}/{iterations} | Last latency: {latency*1000:.1f}ms | Op: {op_name}")
                    
                except Exception as e:
                    latency = time.time() - start_time
                    self.modbus_metrics.record_result(latency, 0, False)
                    print(f"  Error {i+1}: {e}")
                
                # Small delay
                await asyncio.sleep(0.01)
        
        finally:
            # Always disconnect after test
            print("  🔌 Disconnecting Modbus interface...")
            await loop.run_in_executor(None, self.modbus_hand.disconnect)
            print("  ✅ Modbus interface disconnected")
    
    async def burst_test(self, interface: str, burst_size: int = 50):
        """Test maximum burst capacity with separate write and read phases"""
        print(f"\n🚀 Burst Test - {interface.upper()} ({burst_size} rapid requests)")
        
        loop = asyncio.get_event_loop()
        
        # Connect the specific interface for this test
        if interface == "serial":
            print("  🔌 Connecting Serial interface...")
            connected = await loop.run_in_executor(None, self.serial_hand.connect)
            if not connected:
                print("  ❌ Failed to connect Serial interface!")
                return 0
            print("  ✅ Serial interface connected")
        elif interface == "modbus":
            print("  🔌 Connecting Modbus interface...")
            connected = await loop.run_in_executor(None, self.modbus_hand.connect)
            if not connected:
                print("  ❌ Failed to connect Modbus interface!")
                return 0
            print("  ✅ Modbus interface connected")

        # reset to open position
        if interface == "serial":
            print("  Resetting Serial to open position...")
            await loop.run_in_executor(None, self.serial_hand.set_angle, np.array([1000, 1000, 1000, 1000, 1000, 1000], dtype=np.int32))
        elif interface == "modbus":
            print("  Resetting Modbus to open position...")
            await loop.run_in_executor(None, self.modbus_hand.set_angle, np.array([1000, 1000, 1000, 1000, 1000, 1000], dtype=np.int32))

        time.sleep(3)  # Wait for reset to complete

        try:
            # Part 1: Write burst test
            print(f"  📝 WRITE BURST: {burst_size} set_angle commands")
            write_start_time = time.time()
            test_cmd = np.array([500, 500, 500, 500, 500, 500], dtype=np.int32)
            
            if interface == "serial":
                for i in range(burst_size):
                    req_start = time.time()
                    try:
                        await loop.run_in_executor(None, self.serial_hand.set_angle, test_cmd)
                        latency = time.time() - req_start
                        self.serial_metrics.record_result(latency, len(test_cmd) * 4, True)
                    except Exception:
                        latency = time.time() - req_start
                        self.serial_metrics.record_result(latency, 0, False)
                    
                    if (i + 1) % 10 == 0:
                        print(f"    Write progress: {i+1}/{burst_size}")
                    time.sleep(0.005)  # Small delay between writes
            
            elif interface == "modbus":
                for i in range(burst_size):
                    req_start = time.time()
                    try:
                        await loop.run_in_executor(None, self.modbus_hand.set_angle, test_cmd)
                        latency = time.time() - req_start
                        self.modbus_metrics.record_result(latency, len(test_cmd) * 4, True)
                    except Exception:
                        latency = time.time() - req_start
                        self.modbus_metrics.record_result(latency, 0, False)
                    
                    if (i + 1) % 10 == 0:
                        print(f"    Write progress: {i+1}/{burst_size}")
                    time.sleep(0.005)  # Small delay between writes
            
            write_total_time = time.time() - write_start_time
            write_rate = burst_size / write_total_time
            print(f"  ✅ Write burst completed in {write_total_time:.2f}s ({write_rate:.1f} writes/s)")
            
            # Brief pause between write and read phases
            await asyncio.sleep(1)
            
            # Part 2: Read burst test
            print(f"  📖 READ BURST: {burst_size} get_angle_actual commands")
            read_start_time = time.time()
            
            if interface == "serial":
                for i in range(burst_size):
                    req_start = time.time()
                    try:
                        result = await loop.run_in_executor(None, self.serial_hand.get_angle_actual)
                        latency = time.time() - req_start
                        data_size = len(result) * 4 if result is not None else 0
                        self.serial_metrics.record_result(latency, data_size, True)
                    except Exception:
                        latency = time.time() - req_start
                        self.serial_metrics.record_result(latency, 0, False)
                    
                    if (i + 1) % 10 == 0:
                        print(f"    Read progress: {i+1}/{burst_size}")
                    time.sleep(0.005)  # Small delay between reads
            
            elif interface == "modbus":
                for i in range(burst_size):
                    req_start = time.time()
                    try:
                        result = await loop.run_in_executor(None, self.modbus_hand.get_angle_actual)
                        latency = time.time() - req_start
                        data_size = len(result) * 4 if result is not None else 0
                        self.modbus_metrics.record_result(latency, data_size, True)
                    except Exception:
                        latency = time.time() - req_start
                        self.modbus_metrics.record_result(latency, 0, False)
                    
                    if (i + 1) % 10 == 0:
                        print(f"    Read progress: {i+1}/{burst_size}")
                    time.sleep(0.005)  # Small delay between reads
            
            read_total_time = time.time() - read_start_time
            read_rate = burst_size / read_total_time
            print(f"  ✅ Read burst completed in {read_total_time:.2f}s ({read_rate:.1f} reads/s)")
            
            total_time = write_total_time + read_total_time + 1  # +1 for pause
            combined_rate = (burst_size * 2) / total_time
            print(f"  🔍 Combined burst: {total_time:.2f}s total ({combined_rate:.1f} operations/s)")
            
            return combined_rate
        
        finally:
            # Always disconnect after test
            if interface == "serial":
                print("  🔌 Disconnecting Serial interface...")
                await loop.run_in_executor(None, self.serial_hand.disconnect)
                print("  ✅ Serial interface disconnected")
            elif interface == "modbus":
                print("  🔌 Disconnecting Modbus interface...")
                await loop.run_in_executor(None, self.modbus_hand.disconnect)
                print("  ✅ Modbus interface disconnected")
    
    async def sustained_load_test(self, duration: int = 30, target_rate: int = 10):
        """Test sustained load on both interfaces sequentially"""
        print(f"\n⚡ Sustained Load Test ({duration}s at {target_rate} ops/s per interface)")
        print("  Running interfaces sequentially to avoid interference...")
        
        # Run Serial interface first
        print(f"\n  Phase 1: Serial Interface ({duration}s)")
        try:
            await self._sustained_serial_worker(duration, target_rate)
            print("  ✅ Serial sustained load test completed")
        except Exception as e:
            print(f"  ❌ Serial worker error: {e}")
        
        # Brief pause between tests
        print("  📄 Pausing 3 seconds between interface tests...")
        await asyncio.sleep(3)
        
        # Run Modbus interface second
        print(f"\n  Phase 2: Modbus Interface ({duration}s)")
        try:
            await self._sustained_modbus_worker(duration, target_rate)
            print("  ✅ Modbus sustained load test completed")
        except Exception as e:
            print(f"  ❌ Modbus worker error: {e}")
        
        print("  🏁 Sequential sustained load testing finished")
    
    async def _sustained_serial_worker(self, duration: int, rate: int):
        """Sustained load worker for Serial (runs independently)"""
        print("    🔌 Connecting Serial interface...")
        loop = asyncio.get_event_loop()
        
        # Connect for this sustained test
        serial_connected = await loop.run_in_executor(None, self.serial_hand.connect)
        if not serial_connected:
            print("    ❌ Failed to connect Serial interface!")
            return
        
        print("    ✅ Serial interface connected")
        
        try:
            interval = 1.0 / rate
            end_time = time.time() + duration
            cmd_idx = 0
            
            print(f"    🔄 Serial worker: targeting {rate} ops/s for {duration}s")
            
            operations_completed = 0
            while time.time() < end_time:
                cycle_start = time.time()
                
                try:
                    command = self.test_commands[cmd_idx]
                    await loop.run_in_executor(None, self.serial_hand.set_angle, command)
                    
                    latency = time.time() - cycle_start
                    self.serial_metrics.record_result(latency, len(command) * 4, True)
                    operations_completed += 1
                    
                    # Progress indicator every 10 operations
                    if operations_completed % 10 == 0:
                        elapsed = time.time() - (end_time - duration)
                        current_rate = operations_completed / elapsed if elapsed > 0 else 0
                        print(f"    📊 Serial: {operations_completed} ops, {current_rate:.1f} ops/s")
                    
                except Exception as e:
                    latency = time.time() - cycle_start
                    self.serial_metrics.record_result(latency, 0, False)
                    print(f"    ❌ Serial error: {e}")
                
                cmd_idx = (cmd_idx + 1) % len(self.test_commands)
                
                # Rate limiting
                elapsed = time.time() - cycle_start
                if elapsed < interval:
                    await asyncio.sleep(interval - elapsed)
        
        finally:
            # Always disconnect after sustained test
            print("    🔌 Disconnecting Serial interface...")
            await loop.run_in_executor(None, self.serial_hand.disconnect)
            print("    ✅ Serial interface disconnected")
    
    async def _sustained_modbus_worker(self, duration: int, rate: int):
        """Sustained load worker for Modbus (runs independently)"""
        print("    🔌 Connecting Modbus interface...")
        loop = asyncio.get_event_loop()
        
        # Connect for this sustained test
        modbus_connected = await loop.run_in_executor(None, self.modbus_hand.connect)
        if not modbus_connected:
            print("    ❌ Failed to connect Modbus interface!")
            return
        
        print("    ✅ Modbus interface connected")
        
        try:
            interval = 1.0 / rate
            end_time = time.time() + duration
            cmd_idx = 0
            
            print(f"    🔄 Modbus worker: targeting {rate} ops/s for {duration}s")
            
            operations_completed = 0
            while time.time() < end_time:
                cycle_start = time.time()
                
                try:
                    command = self.test_commands[cmd_idx]
                    await loop.run_in_executor(None, self.modbus_hand.set_angle, command)
                    
                    latency = time.time() - cycle_start
                    self.modbus_metrics.record_result(latency, len(command) * 4, True)
                    operations_completed += 1
                    
                    # Progress indicator every 10 operations
                    if operations_completed % 10 == 0:
                        elapsed = time.time() - (end_time - duration)
                        current_rate = operations_completed / elapsed if elapsed > 0 else 0
                        print(f"    📊 Modbus: {operations_completed} ops, {current_rate:.1f} ops/s")
                    
                except Exception as e:
                    latency = time.time() - cycle_start
                    self.modbus_metrics.record_result(latency, 0, False)
                    print(f"    ❌ Modbus error: {e}")
                
                cmd_idx = (cmd_idx + 1) % len(self.test_commands)
                
                # Rate limiting
                elapsed = time.time() - cycle_start
                if elapsed < interval:
                    await asyncio.sleep(interval - elapsed)
        
        finally:
            # Always disconnect after sustained test
            print("    🔌 Disconnecting Modbus interface...")
            await loop.run_in_executor(None, self.modbus_hand.disconnect)
            print("    ✅ Modbus interface disconnected")
    
    def print_comprehensive_report(self):
        """Generate and print detailed performance report"""
        print("\n" + "="*70)
        print("COMMUNICATION THROUGHPUT STRESS TEST REPORT")
        print("="*70)
        
        # Serial Interface Results
        print(f"\n📈 SERIAL INTERFACE PERFORMANCE:")
        print(f"  Total Operations:     {self.serial_metrics.total_operations}")
        print(f"  Success Rate:         {self.serial_metrics.success_rate*100:.1f}%")
        print(f"  Average Latency:      {self.serial_metrics.avg_latency_ms:.2f} ms")
        print(f"  Min Latency:          {self.serial_metrics.min_latency_ms:.2f} ms")
        print(f"  Max Latency:          {self.serial_metrics.max_latency_ms:.2f} ms")
        print(f"  Average Throughput:   {self.serial_metrics.avg_throughput:.0f} bytes/s")
        print(f"  Operations/Second:    {self.serial_metrics.operations_per_second:.1f} ops/s")
        
        if len(self.serial_metrics.latencies) > 1:
            latency_std = statistics.stdev(self.serial_metrics.latencies) * 1000
            percentile_95 = np.percentile(self.serial_metrics.latencies, 95) * 1000
            print(f"  Latency Std Dev:      {latency_std:.2f} ms")
            print(f"  95th Percentile:      {percentile_95:.2f} ms")
        
        # Modbus Interface Results
        print(f"\n📈 MODBUS INTERFACE PERFORMANCE:")
        print(f"  Total Operations:     {self.modbus_metrics.total_operations}")
        print(f"  Success Rate:         {self.modbus_metrics.success_rate*100:.1f}%")
        print(f"  Average Latency:      {self.modbus_metrics.avg_latency_ms:.2f} ms")
        print(f"  Min Latency:          {self.modbus_metrics.min_latency_ms:.2f} ms")
        print(f"  Max Latency:          {self.modbus_metrics.max_latency_ms:.2f} ms")
        print(f"  Average Throughput:   {self.modbus_metrics.avg_throughput:.0f} bytes/s")
        print(f"  Operations/Second:    {self.modbus_metrics.operations_per_second:.1f} ops/s")
        
        if len(self.modbus_metrics.latencies) > 1:
            latency_std = statistics.stdev(self.modbus_metrics.latencies) * 1000
            percentile_95 = np.percentile(self.modbus_metrics.latencies, 95) * 1000
            print(f"  Latency Std Dev:      {latency_std:.2f} ms")
            print(f"  95th Percentile:      {percentile_95:.2f} ms")
        
        # Comparison
        print(f"\n🔍 INTERFACE COMPARISON:")
        if self.serial_metrics.latencies and self.modbus_metrics.latencies:
            serial_faster = self.serial_metrics.avg_latency_ms < self.modbus_metrics.avg_latency_ms
            faster_interface = "Serial" if serial_faster else "Modbus"
            latency_diff = abs(self.serial_metrics.avg_latency_ms - self.modbus_metrics.avg_latency_ms)
            print(f"  Faster Interface:     {faster_interface} (by Diff: {latency_diff:.1f}ms)")
            
            throughput_winner = "Serial" if self.serial_metrics.avg_throughput > self.modbus_metrics.avg_throughput else "Modbus"
            print(f"  Higher Throughput:    {throughput_winner}")
        
        # Test Quality Assessment
        print(f"\n🎯 TEST QUALITY ASSESSMENT:")
        total_ops = self.serial_metrics.total_operations + self.modbus_metrics.total_operations
        total_errors = self.serial_metrics.error_count + self.modbus_metrics.error_count
        overall_success = (total_ops - total_errors) / total_ops if total_ops > 0 else 0
        
        print(f"  Total Operations:     {total_ops}")
        print(f"  Overall Success Rate: {overall_success*100:.1f}%")
        print(f"  Test Duration:        ~{max(len(self.serial_metrics.timestamps), len(self.modbus_metrics.timestamps)) * 0.01:.1f}s")
        
        if overall_success > 0.95:
            print("  Assessment: ✅ Excellent - Both interfaces stable")
        elif overall_success > 0.90:
            print("  Assessment: ⚠️  Good - Minor issues detected")
        else:
            print("  Assessment: ❌ Poor - Significant reliability issues")
    
    def plot_results(self, save_file: bool = True, show_plot: bool = True):
        """
        Generate comprehensive matplotlib plots of test results
        
        Args:
            save_file: Whether to save the plot as a PNG file
            show_plot: Whether to display the interactive plot
        """
        if not MATPLOTLIB_AVAILABLE:
            print("\n❌ Matplotlib not available! Install with: pip install matplotlib")
            print("   Falling back to text-based visualizations...")
            return False
        
        if not (self.serial_metrics.latencies or self.modbus_metrics.latencies):
            print("\n⚠️  No data available for plotting!")
            return False
        
        # Create figure with subplots
        fig, axes = plt.subplots(2, 3, figsize=(16, 10))
        fig.suptitle('SimpleThroughputTester - Communication Performance Analysis', 
                     fontsize=16, fontweight='bold')
        
        # 1. Latency Distribution (Histogram)
        self._plot_latency_distribution(axes[0, 0])
        
        # 2. Latency Over Time (Line Plot)
        self._plot_latency_over_time(axes[0, 1])
        
        # 3. Throughput Over Time (Scatter Plot)
        self._plot_throughput_over_time(axes[0, 2])
        
        # 4. Box Plot Comparison
        self._plot_latency_boxplot(axes[1, 0])
        
        # 5. Performance Summary (Bar Chart)
        self._plot_performance_summary(axes[1, 1])
        
        # 6. Success Rate Comparison
        self._plot_success_rates(axes[1, 2])
        
        # Adjust layout
        plt.tight_layout()
        
        # Save plot if requested
        if save_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"simple_stress_test_results_{timestamp}.png"
            plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
            print(f"\n📈 Plots saved as: {filename}")
        
        # Show plot if requested
        if show_plot:
            plt.show()
        else:
            plt.close()
        
        return True
    
    def _plot_latency_distribution(self, ax):
        """Plot latency distribution histogram"""
        if self.serial_metrics.latencies:
            serial_latencies_ms = [l * 1000 for l in self.serial_metrics.latencies]
            ax.hist(serial_latencies_ms, bins=30, alpha=0.7, label='Serial', 
                   color='steelblue', edgecolor='black', linewidth=0.5)
        
        if self.modbus_metrics.latencies:
            modbus_latencies_ms = [l * 1000 for l in self.modbus_metrics.latencies]
            ax.hist(modbus_latencies_ms, bins=30, alpha=0.7, label='Modbus', 
                   color='orange', edgecolor='black', linewidth=0.5)
        
        ax.set_xlabel('Latency (ms)')
        ax.set_ylabel('Frequency')
        ax.set_title('Latency Distribution')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    def _plot_latency_over_time(self, ax):
        """Plot latency over time"""
        if self.serial_metrics.timestamps and self.serial_metrics.latencies:
            serial_times = [(t - min(self.serial_metrics.timestamps)) 
                          for t in self.serial_metrics.timestamps]
            serial_latencies_ms = [l * 1000 for l in self.serial_metrics.latencies]
            ax.plot(serial_times, serial_latencies_ms, 'o-', alpha=0.7, 
                   label='Serial', color='steelblue', linewidth=1, markersize=2)
        
        if self.modbus_metrics.timestamps and self.modbus_metrics.latencies:
            modbus_times = [(t - min(self.modbus_metrics.timestamps)) 
                          for t in self.modbus_metrics.timestamps]
            modbus_latencies_ms = [l * 1000 for l in self.modbus_metrics.latencies]
            ax.plot(modbus_times, modbus_latencies_ms, 'o-', alpha=0.7, 
                   label='Modbus', color='orange', linewidth=1, markersize=2)
        
        ax.set_xlabel('Time (seconds)')
        ax.set_ylabel('Latency (ms)')
        ax.set_title('Latency Over Time')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    def _plot_throughput_over_time(self, ax):
        """Plot throughput over time"""
        if self.serial_metrics.timestamps and self.serial_metrics.throughput_bps:
            serial_times = [(t - min(self.serial_metrics.timestamps)) 
                          for t in self.serial_metrics.timestamps]
            ax.scatter(serial_times, self.serial_metrics.throughput_bps, 
                      alpha=0.6, label='Serial', color='steelblue', s=10)
        
        if self.modbus_metrics.timestamps and self.modbus_metrics.throughput_bps:
            modbus_times = [(t - min(self.modbus_metrics.timestamps)) 
                          for t in self.modbus_metrics.timestamps]
            ax.scatter(modbus_times, self.modbus_metrics.throughput_bps, 
                      alpha=0.6, label='Modbus', color='orange', s=10)
        
        ax.set_xlabel('Time (seconds)')
        ax.set_ylabel('Throughput (bytes/s)')
        ax.set_title('Throughput Over Time')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    def _plot_latency_boxplot(self, ax):
        """Plot latency comparison boxplot"""
        data_to_plot = []
        labels = []
        colors = []
        
        if self.serial_metrics.latencies:
            serial_latencies_ms = [l * 1000 for l in self.serial_metrics.latencies]
            data_to_plot.append(serial_latencies_ms)
            labels.append('Serial')
            colors.append('steelblue')
        
        if self.modbus_metrics.latencies:
            modbus_latencies_ms = [l * 1000 for l in self.modbus_metrics.latencies]
            data_to_plot.append(modbus_latencies_ms)
            labels.append('Modbus')
            colors.append('orange')
        
        if data_to_plot:
            box_plot = ax.boxplot(data_to_plot, labels=labels, patch_artist=True)
            for patch, color in zip(box_plot['boxes'], colors):
                patch.set_facecolor(color)
                patch.set_alpha(0.7)
        
        ax.set_ylabel('Latency (ms)')
        ax.set_title('Latency Distribution Comparison')
        ax.grid(True, alpha=0.3)
    
    def _plot_performance_summary(self, ax):
        """Plot performance summary bar chart"""
        interfaces = []
        avg_latencies = []
        colors = []
        
        if self.serial_metrics.latencies:
            interfaces.append('Serial')
            avg_latencies.append(self.serial_metrics.avg_latency_ms)
            colors.append('steelblue')
        
        if self.modbus_metrics.latencies:
            interfaces.append('Modbus')
            avg_latencies.append(self.modbus_metrics.avg_latency_ms)
            colors.append('orange')
        
        if interfaces:
            bars = ax.bar(interfaces, avg_latencies, color=colors, alpha=0.7, 
                         edgecolor='black', linewidth=1)
            
            # Add value labels on bars
            for bar, value in zip(bars, avg_latencies):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{value:.1f}ms', ha='center', va='bottom', fontweight='bold')
        
        ax.set_ylabel('Average Latency (ms)')
        ax.set_title('Average Performance Comparison')
        ax.grid(True, alpha=0.3, axis='y')
    
    def _plot_success_rates(self, ax):
        """Plot success rate comparison"""
        interfaces = []
        success_rates = []
        colors = []
        
        if self.serial_metrics.total_operations > 0:
            interfaces.append('Serial')
            success_rates.append(self.serial_metrics.success_rate * 100)
            colors.append('steelblue')
        
        if self.modbus_metrics.total_operations > 0:
            interfaces.append('Modbus')
            success_rates.append(self.modbus_metrics.success_rate * 100)
            colors.append('orange')
        
        if interfaces:
            bars = ax.bar(interfaces, success_rates, color=colors, alpha=0.7, 
                         edgecolor='black', linewidth=1)
            
            # Add value labels on bars
            for bar, value in zip(bars, success_rates):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{value:.1f}%', ha='center', va='bottom', fontweight='bold')
        
        ax.set_ylabel('Success Rate (%)')
        ax.set_title('Operation Success Rate')
        ax.set_ylim(0, 105)  # Set y-limit slightly above 100%
        ax.grid(True, alpha=0.3, axis='y')
    
    def export_data_csv(self, filename: Optional[str] = None):
        """Export test data to CSV for external analysis"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"stress_test_data_{timestamp}.csv"
        
        try:
            import csv
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header
                writer.writerow(['interface', 'timestamp', 'latency_ms', 'latency_seconds', 
                               'throughput_bps', 'success', 'operation_number'])
                
                # Write serial data
                for i, (timestamp, latency, throughput) in enumerate(zip(
                    self.serial_metrics.timestamps, 
                    self.serial_metrics.latencies, 
                    self.serial_metrics.throughput_bps)):
                    writer.writerow(['Serial', timestamp, latency * 1000, latency, 
                                   throughput, True, i + 1])
                
                # Write modbus data
                for i, (timestamp, latency, throughput) in enumerate(zip(
                    self.modbus_metrics.timestamps, 
                    self.modbus_metrics.latencies, 
                    self.modbus_metrics.throughput_bps)):
                    writer.writerow(['Modbus', timestamp, latency * 1000, latency, 
                                   throughput, True, i + 1])
            
            print(f"\n📊 Data exported to: {filename}")
            return True
            
        except Exception as e:
            print(f"\n❌ Failed to export data: {e}")
            return False
    
    def plot_latency_comparison_only(self, save_file: bool = True, show_plot: bool = True):
        """
        Generate a simple latency comparison plot (single chart)
        
        Args:
            save_file: Whether to save the plot as a PNG file
            show_plot: Whether to display the interactive plot
        """
        if not MATPLOTLIB_AVAILABLE:
            print("\n❌ Matplotlib not available! Install with: pip install matplotlib")
            return False
        
        if not (self.serial_metrics.latencies or self.modbus_metrics.latencies):
            print("\n⚠️  No latency data available for plotting!")
            return False
        
        # Create a simple single plot
        fig, ax = plt.subplots(1, 1, figsize=(10, 6))
        fig.suptitle('Communication Latency Comparison', fontsize=14, fontweight='bold')
        
        # Plot latency distribution
        if self.serial_metrics.latencies:
            serial_latencies_ms = [l * 1000 for l in self.serial_metrics.latencies]
            ax.hist(serial_latencies_ms, bins=20, alpha=0.7, label=f'Serial (avg: {self.serial_metrics.avg_latency_ms:.1f}ms)', 
                   color='steelblue', edgecolor='black', linewidth=0.5)
        
        if self.modbus_metrics.latencies:
            modbus_latencies_ms = [l * 1000 for l in self.modbus_metrics.latencies]
            ax.hist(modbus_latencies_ms, bins=20, alpha=0.7, label=f'Modbus (avg: {self.modbus_metrics.avg_latency_ms:.1f}ms)', 
                   color='orange', edgecolor='black', linewidth=0.5)
        
        ax.set_xlabel('Latency (ms)')
        ax.set_ylabel('Frequency')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Add statistics text box
        stats_text = ""
        if self.serial_metrics.latencies:
            stats_text += f"Serial: {len(self.serial_metrics.latencies)} samples\n"
            stats_text += f"  Avg: {self.serial_metrics.avg_latency_ms:.1f}ms\n"
            stats_text += f"  Min: {self.serial_metrics.min_latency_ms:.1f}ms\n"
            stats_text += f"  Max: {self.serial_metrics.max_latency_ms:.1f}ms\n"
        
        if self.modbus_metrics.latencies:
            stats_text += f"\nModbus: {len(self.modbus_metrics.latencies)} samples\n"
            stats_text += f"  Avg: {self.modbus_metrics.avg_latency_ms:.1f}ms\n"
            stats_text += f"  Min: {self.modbus_metrics.min_latency_ms:.1f}ms\n"
            stats_text += f"  Max: {self.modbus_metrics.max_latency_ms:.1f}ms"
        
        # Add text box with statistics
        ax.text(0.98, 0.98, stats_text, transform=ax.transAxes, fontsize=9,
                verticalalignment='top', horizontalalignment='right',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        plt.tight_layout()
        
        # Save plot if requested
        if save_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"latency_comparison_{timestamp}.png"
            plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
            print(f"\n📈 Latency comparison plot saved as: {filename}")
        
        # Show plot if requested
        if show_plot:
            plt.show()
        else:
            plt.close()
        
        return True
    
    def print_plotting_help(self):
        """Display available plotting options and requirements"""
        print("\n📊 PLOTTING CAPABILITIES")
        print("=" * 50)
        
        if MATPLOTLIB_AVAILABLE:
            print("✅ Matplotlib is available - Full plotting functionality enabled!")
            print("\nAvailable plotting methods:")
            print("  📈 plot_results()              - Comprehensive 6-panel dashboard")
            print("  📊 plot_latency_comparison_only() - Simple latency histogram")
            print("  📋 export_data_csv()           - Export data for external tools")
            print("\nPlot types included in dashboard:")
            print("  • Latency distribution (histogram)")
            print("  • Latency over time (line plot)")
            print("  • Throughput over time (scatter plot)")
            print("  • Latency comparison (box plot)")
            print("  • Performance summary (bar chart)")
            print("  • Success rate comparison (bar chart)")
        else:
            print("❌ Matplotlib not available")
            print("   Install with: pip install matplotlib")
            print("   Fallback: Text-based charts and CSV export available")
        
        print(f"\nData export:")
        print(f"  📄 CSV export always available (no dependencies)")
        print(f"  📊 Compatible with Excel, R, Python pandas, etc.")
        
        if VISUALIZATION_AVAILABLE:
            print(f"\n📝 Text-based visualizations available via simple_visualizer")
        else:
            print(f"\n💡 Optional: Text-based charts available in simple_visualizer.py")
        
        print("\nExample usage:")
        print("  tester = SimpleThroughputTester()")
        print("  # ... run tests ...")
        print("  tester.plot_results()                    # Full dashboard")
        print("  tester.plot_latency_comparison_only()    # Simple plot")
        print("  tester.export_data_csv()                 # Export data")

async def main():
    """Main test execution"""
    # Create tester (adjust COM port and IP as needed)
    tester = SimpleThroughputTester(serial_port="COM3", modbus_ip="192.168.11.210")
    
    try:
        print("\n🧪 Starting stress test sequence...")
        print("Each test will connect and disconnect independently for clean isolation\n")
        
        # Test 1: Basic latency measurement
        print("=" * 60)
        print("PHASE 1: BASIC LATENCY MEASUREMENT")
        print("=" * 60)
        
        # Test Serial interface
        await tester.test_serial_latency(iterations=50)
        
        # Pause between interface tests
        print("\n⏸️  Pausing 2 seconds between interface tests...")
        await asyncio.sleep(2)
        
        # Test Modbus interface
        await tester.test_modbus_latency(iterations=50)
        
        # Pause between test phases
        print("\n⏸️  Pausing 3 seconds between test phases...")
        await asyncio.sleep(3)
        
        # Test 2: Burst capacity
        print("\n" + "=" * 60)
        print("PHASE 2: BURST CAPACITY TESTING")
        print("=" * 60)
        
        await tester.burst_test("serial", burst_size=50)
        
        print("⏸️  Brief pause between burst tests...")
        await asyncio.sleep(2)
        
        await tester.burst_test("modbus", burst_size=50)
        
        # Test 3: Sustained load
        print("\n⏸️  Pausing 3 seconds before sustained load test...")
        await asyncio.sleep(3)
        
        print("\n" + "=" * 60)
        print("PHASE 3: SUSTAINED LOAD TESTING")
        print("=" * 60)
        await tester.sustained_load_test(duration=20, target_rate=5)
        
        # Generate comprehensive report
        tester.print_comprehensive_report()
        
        # Export data to CSV
        tester.export_data_csv()
        
        # Generate plots if matplotlib is available
        if MATPLOTLIB_AVAILABLE:
            print("\n🎨 Generating matplotlib plots...")
            plot_success = tester.plot_results(save_file=True, show_plot=True)
            if plot_success:
                print("✅ Plotting completed successfully!")
            else:
                print("⚠️  Plotting failed, but test data is still available")
        else:
            print("\n💡 Install matplotlib for advanced plotting: pip install matplotlib")
        
        # Generate visual report if available
        if VISUALIZATION_AVAILABLE:
            print("\n🎨 Generating text-based visual report...")
            reporter = EnhancedReporter(tester.serial_metrics, tester.modbus_metrics)
            reporter.generate_visual_report()
        else:
            print("\n💡 Tip: The simple_visualizer module provides additional text-based charts!")
        
        print(f"\n✅ Stress test completed successfully!")
        
    except KeyboardInterrupt:
        print("\n⏹️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Simple Communication Throughput Stress Test")
    print("============================================")
    print("Adjust COM port and IP address in the code as needed!")
    print()
    asyncio.run(main())
