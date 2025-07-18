#!/usr/bin/env python3
"""
Communication Stress Test Suite
Consolidated implementation with interactive demo interface
"""

import asyncio
import time
import statistics
import numpy as np
import os
import csv
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from datetime import datetime

from inspire_demos.inspire_modbus import InspireHandModbus
from inspire_demos.inspire_serial import InspireHandSerial

# Optional matplotlib for plotting
try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

SERIAL_PORT = "COM3"  # Adjust for your system
MODBUS_IP = "192.168.11.210"  # Adjust for your system

@dataclass
class TestMetrics:
    """Container for test performance metrics"""
    latencies: List[float] = field(default_factory=list)
    throughput_bps: List[float] = field(default_factory=list)
    error_count: int = 0
    success_count: int = 0
    timestamps: List[float] = field(default_factory=list)
    
    def record_result(self, latency: float, data_size: int, success: bool):
        """Record a single test result"""
        if success:
            self.latencies.append(latency)
            self.throughput_bps.append(data_size / latency if latency > 0 else 0)
            self.success_count += 1
        else:
            self.error_count += 1
        self.timestamps.append(time.time())
    
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
    def min_latency_ms(self) -> float:
        return min(self.latencies) * 1000 if self.latencies else 0
    
    @property
    def max_latency_ms(self) -> float:
        return max(self.latencies) * 1000 if self.latencies else 0
    
    @property
    def avg_throughput(self) -> float:
        return statistics.mean(self.throughput_bps) if self.throughput_bps else 0
    
    @property
    def operations_per_second(self) -> float:
        if len(self.timestamps) < 2:
            return 0
        duration = max(self.timestamps) - min(self.timestamps)
        return self.success_count / duration if duration > 0 else 0

class StressTester:
    """Core stress testing functionality"""
    
    def __init__(self, serial_port: str = SERIAL_PORT, modbus_ip: str = MODBUS_IP):
        self.serial_hand = InspireHandSerial(port=serial_port, generation=4)
        self.modbus_hand = InspireHandModbus(ip=modbus_ip, generation=4)
        
        self.serial_metrics = TestMetrics()
        self.modbus_metrics = TestMetrics()
        
        # Test configurations
        self.test_commands = [
            np.array([0, 0, 0, 0, 200, 1000], dtype=np.int32),      # Close without collision
            np.array([1000, 1000, 1000, 1000, 1000, 1000], dtype=np.int32),  # Open
            np.array([500, 500, 500, 500, 600, 900], dtype=np.int32),  # Half
        ]
        
        # Set up output directory (root folder)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.output_dir = os.path.dirname(current_dir)
    
    async def test_serial_latency(self, iterations: int = 100):
        """Test Serial interface latency and throughput"""
        print(f"\nTesting Serial Interface ({iterations} iterations)")
        
        loop = asyncio.get_event_loop()
        print("  Connecting Serial interface...")
        serial_connected = await loop.run_in_executor(None, self.serial_hand.connect)
        
        if not serial_connected:
            print("  Failed to connect Serial interface!")
            return
        
        print("  Serial interface connected")
        
        try:
            cmd_idx = 0
            for i in range(iterations):
                start_time = time.time()
                
                try:
                    command = self.test_commands[cmd_idx]
                    await loop.run_in_executor(None, self.serial_hand.set_angle, command)
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
                await asyncio.sleep(0.01)  # Small delay
        
        finally:
            print("  Disconnecting Serial interface...")
            await loop.run_in_executor(None, self.serial_hand.disconnect)
            print("  Serial interface disconnected")
    
    async def test_modbus_latency(self, iterations: int = 100):
        """Test Modbus interface latency and throughput"""
        print(f"\nTesting Modbus Interface ({iterations} iterations)")
        
        loop = asyncio.get_event_loop()
        print("  Connecting Modbus interface...")
        modbus_connected = await loop.run_in_executor(None, self.modbus_hand.connect)
        
        if not modbus_connected:
            print("  Failed to connect Modbus interface!")
            return
        
        print("  Modbus interface connected")
        
        try:
            # Phase 1: Set and Get Angle (same as Serial)
            print("  Phase 1: Set/Get Angle operations")
            cmd_idx = 0
            for i in range(iterations):
                start_time = time.time()
                
                try:
                    command = self.test_commands[cmd_idx]
                    await loop.run_in_executor(None, self.modbus_hand.set_angle, command)
                    response = await loop.run_in_executor(None, self.modbus_hand.get_angle_actual)
                    
                    latency = time.time() - start_time
                    data_size = len(command) * 4 + len(response) * 4  # Estimated bytes
                    self.modbus_metrics.record_result(latency, data_size, True)
                    
                    if (i + 1) % 10 == 0:
                        print(f"  Progress: {i+1}/{iterations} | Last latency: {latency*1000:.1f}ms")
                    
                except Exception as e:
                    latency = time.time() - start_time
                    self.modbus_metrics.record_result(latency, 0, False)
                    print(f"  Error {i+1}: {e}")
                
                cmd_idx = (cmd_idx + 1) % len(self.test_commands)
                await asyncio.sleep(0.01)  # Small delay
            
            # Phase 2: Get Tactile Data (Modbus only feature)
            print("  Phase 2: Get Tactile Data operations (Modbus only)")
            for i in range(iterations):
                start_time = time.time()
                
                try:
                    tactile_data = await loop.run_in_executor(None, self.modbus_hand.get_tactile_data)
                    
                    latency = time.time() - start_time
                    
                    # Estimate data size for tactile data
                    if tactile_data:
                        data_size = sum(sensor.nbytes for sensor in tactile_data.values())
                    else:
                        data_size = 0
                    
                    self.modbus_metrics.record_result(latency, data_size, True)
                    
                    if (i + 1) % 10 == 0:
                        print(f"  Progress: {i+1}/{iterations} | Last latency: {latency*1000:.1f}ms | Tactile")
                    
                except Exception as e:
                    latency = time.time() - start_time
                    self.modbus_metrics.record_result(latency, 0, False)
                    print(f"  Error {i+1}: {e}")
                
                await asyncio.sleep(0.01)  # Small delay
        
        finally:
            print("  Disconnecting Modbus interface...")
            await loop.run_in_executor(None, self.modbus_hand.disconnect)
            print("  Modbus interface disconnected")
    
    async def burst_test(self, interface: str, burst_size: int = 50) -> float:
        """Test maximum burst capacity"""
        print(f"\nBurst Test - {interface.upper()} ({burst_size} rapid requests)")
        
        loop = asyncio.get_event_loop()
        
        # Connect the specific interface
        if interface == "serial":
            print("  Connecting Serial interface...")
            connected = await loop.run_in_executor(None, self.serial_hand.connect)
            if not connected:
                print("  Failed to connect Serial interface!")
                return 0
            print("  Serial interface connected")
            
            # Reset position
            reset_cmd = np.array([1000, 1000, 1000, 1000, 1000, 1000], dtype=np.int32)
            await loop.run_in_executor(None, self.serial_hand.set_angle, reset_cmd)
            
        elif interface == "modbus":
            print("  Connecting Modbus interface...")
            connected = await loop.run_in_executor(None, self.modbus_hand.connect)
            if not connected:
                print("  Failed to connect Modbus interface!")
                return 0
            print("  Modbus interface connected")
            
            # Reset position
            reset_cmd = np.array([1000, 1000, 1000, 1000, 1000, 1000], dtype=np.int32)
            await loop.run_in_executor(None, self.modbus_hand.set_angle, reset_cmd)
        
        time.sleep(2)  # Wait for reset
        
        try:
            # Burst test
            start_time = time.time()
            test_cmd = np.array([500, 500, 500, 500, 700, 1000], dtype=np.int32)
            
            for i in range(burst_size):
                req_start = time.time()
                try:
                    if interface == "serial":
                        await loop.run_in_executor(None, self.serial_hand.set_angle, test_cmd)
                        latency = time.time() - req_start
                        self.serial_metrics.record_result(latency, len(test_cmd) * 4, True)
                    elif interface == "modbus":
                        await loop.run_in_executor(None, self.modbus_hand.set_angle, test_cmd)
                        latency = time.time() - req_start
                        self.modbus_metrics.record_result(latency, len(test_cmd) * 4, True)
                except Exception:
                    latency = time.time() - req_start
                    if interface == "serial":
                        self.serial_metrics.record_result(latency, 0, False)
                    elif interface == "modbus":
                        self.modbus_metrics.record_result(latency, 0, False)
                
                if (i + 1) % 10 == 0:
                    print(f"    Progress: {i+1}/{burst_size}")
                time.sleep(0.005)  # Small delay
            
            total_time = time.time() - start_time
            rate = burst_size / total_time
            print(f"  Burst completed in {total_time:.2f}s ({rate:.1f} ops/s)")
            return rate
            
        finally:
            # Disconnect
            if interface == "serial":
                print("  Disconnecting Serial interface...")
                await loop.run_in_executor(None, self.serial_hand.disconnect)
                print("  Serial interface disconnected")
            elif interface == "modbus":
                print("  Disconnecting Modbus interface...")
                await loop.run_in_executor(None, self.modbus_hand.disconnect)
                print("  Modbus interface disconnected")
    
    async def sustained_load_test(self, duration: int = 30, target_rate: int = 10):
        """Test sustained load on both interfaces sequentially"""
        print(f"\nSustained Load Test ({duration}s at {target_rate} ops/s per interface)")
        print("  Running interfaces sequentially to avoid interference...")
        
        # Serial test
        print(f"\n  Phase 1: Serial Interface ({duration}s)")
        await self._sustained_worker("serial", duration, target_rate)
        
        # Brief pause
        print("  Pausing 3 seconds between interface tests...")
        await asyncio.sleep(3)
        
        # Modbus test
        print(f"\n  Phase 2: Modbus Interface ({duration}s)")
        await self._sustained_worker("modbus", duration, target_rate)
        
        print("  Sequential sustained load testing finished")
    
    async def _sustained_worker(self, interface: str, duration: int, rate: int):
        """Sustained load worker for either interface"""
        loop = asyncio.get_event_loop()
        
        # Connect
        if interface == "serial":
            print("    Connecting Serial interface...")
            connected = await loop.run_in_executor(None, self.serial_hand.connect)
            if not connected:
                print("    Failed to connect Serial interface!")
                return
        else:
            print("    Connecting Modbus interface...")
            connected = await loop.run_in_executor(None, self.modbus_hand.connect)
            if not connected:
                print("    Failed to connect Modbus interface!")
                return
        
        print(f"    {interface.title()} interface connected")
        
        try:
            interval = 1.0 / rate
            end_time = time.time() + duration
            cmd_idx = 0
            operations_completed = 0
            
            print(f"    {interface.title()} worker: targeting {rate} ops/s for {duration}s")
            
            while time.time() < end_time:
                cycle_start = time.time()
                
                try:
                    command = self.test_commands[cmd_idx]
                    if interface == "serial":
                        await loop.run_in_executor(None, self.serial_hand.set_angle, command)
                        latency = time.time() - cycle_start
                        self.serial_metrics.record_result(latency, len(command) * 4, True)
                    else:
                        await loop.run_in_executor(None, self.modbus_hand.set_angle, command)
                        latency = time.time() - cycle_start
                        self.modbus_metrics.record_result(latency, len(command) * 4, True)
                    
                    operations_completed += 1
                    
                    if operations_completed % 10 == 0:
                        elapsed = time.time() - (end_time - duration)
                        current_rate = operations_completed / elapsed if elapsed > 0 else 0
                        print(f"    {interface.title()}: {operations_completed} ops, {current_rate:.1f} ops/s")
                    
                except Exception as e:
                    latency = time.time() - cycle_start
                    if interface == "serial":
                        self.serial_metrics.record_result(latency, 0, False)
                    else:
                        self.modbus_metrics.record_result(latency, 0, False)
                    print(f"    {interface.title()} error: {e}")
                
                cmd_idx = (cmd_idx + 1) % len(self.test_commands)
                
                # Rate limiting
                elapsed = time.time() - cycle_start
                if elapsed < interval:
                    await asyncio.sleep(interval - elapsed)
        
        finally:
            # Disconnect
            print(f"    Disconnecting {interface.title()} interface...")
            if interface == "serial":
                await loop.run_in_executor(None, self.serial_hand.disconnect)
            else:
                await loop.run_in_executor(None, self.modbus_hand.disconnect)
            print(f"    {interface.title()} interface disconnected")
    
    def print_comprehensive_report(self, save_to_file: bool = True):
        """Generate and print detailed performance report"""
        report_lines = []
        
        def add_line(line=""):
            print(line)
            report_lines.append(line)
        
        add_line("="*70)
        add_line("COMMUNICATION THROUGHPUT STRESS TEST REPORT")
        add_line("="*70)
        add_line(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Serial Interface Results
        add_line(f"\nSERIAL INTERFACE PERFORMANCE:")
        add_line(f"  Total Operations:     {self.serial_metrics.total_operations}")
        add_line(f"  Success Rate:         {self.serial_metrics.success_rate*100:.1f}%")
        add_line(f"  Average Latency:      {self.serial_metrics.avg_latency_ms:.2f} ms")
        add_line(f"  Min Latency:          {self.serial_metrics.min_latency_ms:.2f} ms")
        add_line(f"  Max Latency:          {self.serial_metrics.max_latency_ms:.2f} ms")
        add_line(f"  Average Throughput:   {self.serial_metrics.avg_throughput:.0f} bytes/s")
        add_line(f"  Operations/Second:    {self.serial_metrics.operations_per_second:.1f} ops/s")
        
        if len(self.serial_metrics.latencies) > 1:
            latency_std = statistics.stdev(self.serial_metrics.latencies) * 1000
            percentile_95 = np.percentile(self.serial_metrics.latencies, 95) * 1000
            add_line(f"  Latency Std Dev:      {latency_std:.2f} ms")
            add_line(f"  95th Percentile:      {percentile_95:.2f} ms")
        
        # Modbus Interface Results
        add_line(f"\nMODBUS INTERFACE PERFORMANCE:")
        add_line(f"  Total Operations:     {self.modbus_metrics.total_operations}")
        add_line(f"  Success Rate:         {self.modbus_metrics.success_rate*100:.1f}%")
        add_line(f"  Average Latency:      {self.modbus_metrics.avg_latency_ms:.2f} ms")
        add_line(f"  Min Latency:          {self.modbus_metrics.min_latency_ms:.2f} ms")
        add_line(f"  Max Latency:          {self.modbus_metrics.max_latency_ms:.2f} ms")
        add_line(f"  Average Throughput:   {self.modbus_metrics.avg_throughput:.0f} bytes/s")
        add_line(f"  Operations/Second:    {self.modbus_metrics.operations_per_second:.1f} ops/s")
        
        if len(self.modbus_metrics.latencies) > 1:
            latency_std = statistics.stdev(self.modbus_metrics.latencies) * 1000
            percentile_95 = np.percentile(self.modbus_metrics.latencies, 95) * 1000
            add_line(f"  Latency Std Dev:      {latency_std:.2f} ms")
            add_line(f"  95th Percentile:      {percentile_95:.2f} ms")
        
        # Comparison
        add_line(f"\nINTERFACE COMPARISON:")
        if self.serial_metrics.latencies and self.modbus_metrics.latencies:
            serial_faster = self.serial_metrics.avg_latency_ms < self.modbus_metrics.avg_latency_ms
            faster_interface = "Serial" if serial_faster else "Modbus"
            latency_diff = abs(self.serial_metrics.avg_latency_ms - self.modbus_metrics.avg_latency_ms)
            add_line(f"  Faster Interface:     {faster_interface} (by {latency_diff:.1f}ms)")
            
            throughput_winner = "Serial" if self.serial_metrics.avg_throughput > self.modbus_metrics.avg_throughput else "Modbus"
            add_line(f"  Higher Throughput:    {throughput_winner}")
        
        # Overall Assessment
        add_line(f"\nTEST QUALITY ASSESSMENT:")
        total_ops = self.serial_metrics.total_operations + self.modbus_metrics.total_operations
        total_errors = self.serial_metrics.error_count + self.modbus_metrics.error_count
        overall_success = (total_ops - total_errors) / total_ops if total_ops > 0 else 0
        
        add_line(f"  Total Operations:     {total_ops}")
        add_line(f"  Overall Success Rate: {overall_success*100:.1f}%")
        
        if overall_success > 0.95:
            add_line("  Assessment: Excellent - Both interfaces stable")
        elif overall_success > 0.90:
            add_line("  Assessment: Good - Minor issues detected")
        else:
            add_line("  Assessment: Poor - Significant reliability issues")
        
        # Save to file if requested
        if save_to_file:
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"stress_test_report_{timestamp}.txt"
                filepath = os.path.join(self.output_dir, filename)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(report_lines))
                
                print(f"\nReport saved to: {filepath}")
                
            except Exception as e:
                print(f"\nFailed to save report: {e}")
    
    def export_data_csv(self, filename: Optional[str] = None):
        """Export test data to CSV for external analysis"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"stress_test_data_{timestamp}.csv"
        
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            with open(filepath, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Interface', 'Timestamp', 'Latency_ms', 'Latency_s', 
                               'Throughput_bps', 'Success', 'Test_Number'])
                
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
            
            print(f"\nData exported to: {filepath}")
            return True
            
        except Exception as e:
            print(f"\nFailed to export data: {e}")
            return False
    
    def plot_results(self, save_file: bool = True, show_plot: bool = True):
        """Generate matplotlib plots if available"""
        if not MATPLOTLIB_AVAILABLE:
            print("\nMatplotlib not available. Install with: pip install matplotlib")
            return False
        
        if not (self.serial_metrics.latencies or self.modbus_metrics.latencies):
            print("\nNo data available for plotting")
            return False
        
        # Create subplots
        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
        fig.suptitle('Communication Stress Test Results', fontsize=14, fontweight='bold')
        
        # Latency distribution
        ax = axes[0, 0]
        if self.serial_metrics.latencies:
            serial_latencies_ms = [l * 1000 for l in self.serial_metrics.latencies]
            ax.hist(serial_latencies_ms, bins=20, alpha=0.7, label='Serial', 
                   color='steelblue', edgecolor='black', linewidth=0.5)
        
        if self.modbus_metrics.latencies:
            modbus_latencies_ms = [l * 1000 for l in self.modbus_metrics.latencies]
            ax.hist(modbus_latencies_ms, bins=20, alpha=0.7, label='Modbus', 
                   color='orange', edgecolor='black', linewidth=0.5)
        
        ax.set_xlabel('Latency (ms)')
        ax.set_ylabel('Frequency')
        ax.set_title('Latency Distribution')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Success rates
        ax = axes[0, 1]
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
            bars = ax.bar(interfaces, success_rates, color=colors, alpha=0.7)
            for bar, rate in zip(bars, success_rates):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                       f'{rate:.1f}%', ha='center', va='bottom')
        
        ax.set_ylabel('Success Rate (%)')
        ax.set_title('Operation Success Rate')
        ax.set_ylim(0, 105)
        ax.grid(True, alpha=0.3, axis='y')
        
        # Performance comparison
        ax = axes[1, 0]
        if interfaces:
            avg_latencies = [self.serial_metrics.avg_latency_ms if 'Serial' in interfaces else 0,
                           self.modbus_metrics.avg_latency_ms if 'Modbus' in interfaces else 0]
            avg_latencies = [x for x in avg_latencies if x > 0]
            
            if avg_latencies:
                bars = ax.bar(interfaces, avg_latencies, color=colors, alpha=0.7)
                for bar, latency in zip(bars, avg_latencies):
                    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(avg_latencies)*0.01,
                           f'{latency:.1f}ms', ha='center', va='bottom')
        
        ax.set_ylabel('Average Latency (ms)')
        ax.set_title('Average Performance Comparison')
        ax.grid(True, alpha=0.3, axis='y')
        
        # Throughput comparison
        ax = axes[1, 1]
        if interfaces:
            avg_throughputs = [self.serial_metrics.avg_throughput if 'Serial' in interfaces else 0,
                             self.modbus_metrics.avg_throughput if 'Modbus' in interfaces else 0]
            avg_throughputs = [x for x in avg_throughputs if x > 0]
            
            if avg_throughputs:
                bars = ax.bar(interfaces, avg_throughputs, color=colors, alpha=0.7)
                for bar, throughput in zip(bars, avg_throughputs):
                    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(avg_throughputs)*0.01,
                           f'{throughput:.0f}', ha='center', va='bottom')
        
        ax.set_ylabel('Average Throughput (bytes/s)')
        ax.set_title('Average Throughput Comparison')
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        
        # Save plot if requested
        if save_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"stress_test_results_{timestamp}.png"
            filepath = os.path.join(self.output_dir, filename)
            plt.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white')
            print(f"\nResults plotted and saved as: {filepath}")
        
        # Show plot if requested
        if show_plot:
            plt.show()
        else:
            plt.close()
        
        return True

class StressTestDemo:
    """Interactive demonstration of stress test scenarios"""
    
    def __init__(self):
        self.tester = None
    
    async def demo_basic_stress_test(self):
        """Demonstrate basic stress testing functionality"""
        print("DEMO 1: Basic Stress Test")
        print("="*50)
        
        self.tester = StressTester(serial_port=SERIAL_PORT, modbus_ip=MODBUS_IP)
        
        print("Running basic latency tests...")
        print("Each test will manage its own connections for clean isolation")
        
        # Test each interface separately
        await self.tester.test_serial_latency(iterations=50)
        
        print("\nBrief pause between interface tests...")
        await asyncio.sleep(5)
        
        await self.tester.test_modbus_latency(iterations=50)
        
        # Generate report
        self.tester.print_comprehensive_report()

    async def demo_burst_testing(self):
        """Demonstrate burst testing scenarios"""
        print("\nDEMO 2: Burst Testing")
        print("="*50)
        
        if not self.tester:
            self.tester = StressTester(serial_port=SERIAL_PORT, modbus_ip=MODBUS_IP)
        
        print("Testing burst capacity...")
        print("Each test manages its own connection for isolation")
        
        # Test burst capacity
        rate = await self.tester.burst_test("serial", burst_size=30)
        print(f"Serial burst rate: {rate:.1f} ops/sec")
        
        print("Brief pause between burst tests...")
        await asyncio.sleep(5)
        
        rate = await self.tester.burst_test("modbus", burst_size=30)
        print(f"Modbus burst rate: {rate:.1f} ops/sec")
    
    async def demo_sustained_load(self):
        """Demonstrate sustained load testing"""
        print("\nDEMO 3: Sustained Load Testing")
        print("="*50)
        
        if not self.tester:
            self.tester = StressTester(serial_port=SERIAL_PORT, modbus_ip=MODBUS_IP)
        
        print("Running sustained load test (15 seconds)...")
        print("Both Serial and Modbus will be tested sequentially")
        
        # Sustained load test
        await self.tester.sustained_load_test(duration=15, target_rate=3)
        
        print("Sustained load test completed")
        self.tester.print_comprehensive_report()
    
    async def demo_comprehensive_test(self):
        """Run all tests and generate comprehensive analysis"""
        print("\nDEMO 4: Comprehensive Test Suite")
        print("="*50)
        
        self.tester = StressTester(serial_port=SERIAL_PORT, modbus_ip=MODBUS_IP)
        
        # Run all test types
        await self.demo_basic_stress_test()
        await self.demo_burst_testing() 
        await self.demo_sustained_load()
        
        # Generate outputs
        self.tester.export_data_csv()
        
        if MATPLOTLIB_AVAILABLE:
            print("\nGenerating matplotlib plots...")
            self.tester.plot_results(save_file=True, show_plot=True)
        else:
            print("\nInstall matplotlib for advanced plotting: pip install matplotlib")

async def interactive_demo():
    """Interactive demonstration menu"""
    demo = StressTestDemo()
    
    print("COMMUNICATION THROUGHPUT STRESS TEST DEMO")
    print("=" * 60)
    print("This demo shows different stress testing scenarios.")
    print("Ensure your hardware is properly configured before running tests.")
    print()
    
    while True:
        print("\nSelect a demo scenario:")
        print("1. Basic Stress Test (latency measurement)")
        print("2. Burst Testing (maximum short-term throughput)")
        print("3. Sustained Load Test (long-term stability)")
        print("4. Comprehensive Test Suite (all tests + analysis)")
        print("5. Exit")
        
        try:
            choice = input("\nEnter your choice (1-5): ").strip()
            
            if choice == "1":
                await demo.demo_basic_stress_test()
            elif choice == "2":
                await demo.demo_burst_testing()
            elif choice == "3":
                await demo.demo_sustained_load()
            elif choice == "4":
                await demo.demo_comprehensive_test()
            elif choice == "5":
                print("Demo completed!")
                break
            else:
                print("Invalid choice. Please enter 1-5.")
                
        except KeyboardInterrupt:
            print("\nDemo interrupted.")
            break
        except Exception as e:
            print(f"Demo error: {e}")

def print_stress_test_concepts():
    """Print educational content about stress testing"""
    print("\nSTRESS TESTING CONCEPTS")
    print("=" * 60)
    print("""
WHAT IS COMMUNICATION THROUGHPUT STRESS TESTING?

Stress testing evaluates how communication interfaces perform under various
load conditions, helping identify:
• Maximum sustainable data rates
• System bottlenecks and failure points  
• Performance consistency under load
• Resource utilization patterns

KEY TESTING SCENARIOS:

1. LATENCY CHARACTERIZATION
   • Measures baseline response times
   • Identifies network/protocol overhead
   • Purpose: Establish performance baseline

2. BURST TESTING
   • Maximum short-term throughput
   • Buffer overflow behavior
   • Purpose: Find peak capacity limits

3. SUSTAINED LOAD
   • Long-term performance stability
   • Memory leaks and degradation
   • Purpose: Validate production readiness

CRITICAL METRICS:

• Latency: Response time (milliseconds)
• Throughput: Data rate (bytes/second)
• Success Rate: Reliability percentage
• Operations/Second: Command rate

PRACTICAL APPLICATIONS:

For robotic hand control:
• Real-time control loops (10-100Hz)
• Tactile sensor data streaming
• Multi-axis coordination
• Safety-critical responsiveness
""")

async def main():
    """Main demo entry point"""
    print_stress_test_concepts()
    
    print("\nReady to run interactive demos?")
    response = input("Press Enter to start, or 'q' to quit: ").strip().lower()
    
    if response != 'q':
        await interactive_demo()
    else:
        print("See you next time!")

if __name__ == "__main__":
    print("Communication Throughput Stress Test Demo")
    print(f"Adjust COM port ({SERIAL_PORT}) and IP ({MODBUS_IP}) settings at the top of this file!")
    print()
    print("NOTE: For tactile data collection demo, see tactile_data_demo.py")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
    except ConnectionError as e:
        print(f"\n{e}")
        print("Check your hardware connections and settings!")
    except Exception as e:
        print(f"\nDemo failed: {e}")
        import traceback
        traceback.print_exc()
