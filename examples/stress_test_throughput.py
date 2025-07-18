#!/usr/bin/env python3
"""
Communication Throughput Stress Test
Tests both Serial and Modbus interfaces under various load conditions
"""

import asyncio
import time
import threading
import statistics
import psutil
import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor
import matplotlib.pyplot as plt
from datetime import datetime

from inspire_demos.inspire_modbus import InspireHandModbus
from inspire_demos.inspire_serial import InspireHandSerial

@dataclass
class TestMetrics:
    """Container for test performance metrics"""
    latencies: List[float] = field(default_factory=list)
    throughput_bps: List[float] = field(default_factory=list)
    error_count: int = 0
    success_count: int = 0
    cpu_usage: List[float] = field(default_factory=list)
    memory_usage: List[float] = field(default_factory=list)
    timestamps: List[float] = field(default_factory=list)
    
    def add_measurement(self, latency: float, data_size: int, success: bool, timestamp: float):
        """Add a single measurement"""
        if success:
            self.latencies.append(latency)
            self.throughput_bps.append(data_size / latency if latency > 0 else 0)
            self.success_count += 1
        else:
            self.error_count += 1
        self.timestamps.append(timestamp)
    
    def add_system_metrics(self, cpu: float, memory: float):
        """Add system resource usage"""
        self.cpu_usage.append(cpu)
        self.memory_usage.append(memory)
    
    @property
    def total_requests(self) -> int:
        return self.success_count + self.error_count
    
    @property
    def error_rate(self) -> float:
        return self.error_count / self.total_requests if self.total_requests > 0 else 0
    
    @property
    def avg_latency(self) -> float:
        return statistics.mean(self.latencies) if self.latencies else 0
    
    @property
    def latency_std(self) -> float:
        return statistics.stdev(self.latencies) if len(self.latencies) > 1 else 0
    
    @property
    def avg_throughput(self) -> float:
        return statistics.mean(self.throughput_bps) if self.throughput_bps else 0

class StressTester:
    """Main stress testing orchestrator"""
    
    def __init__(self, serial_port: str = "COM3", modbus_ip: str = "192.168.11.210"):
        self.serial_hand = InspireHandSerial(port=serial_port, generation=4)
        self.modbus_hand = InspireHandModbus(ip=modbus_ip, generation=4)
        
        self.serial_metrics = TestMetrics()
        self.modbus_metrics = TestMetrics()
        self.system_monitor_active = False
        
    async def setup(self) -> Tuple[bool, bool]:
        """Initialize connections"""
        print("=== Communication Throughput Stress Test ===")
        print("Connecting to devices...")
        
        loop = asyncio.get_event_loop()
        serial_ok = await loop.run_in_executor(None, self.serial_hand.connect)
        modbus_ok = await loop.run_in_executor(None, self.modbus_hand.connect)
        
        print(f"Serial interface: {'✓ Connected' if serial_ok else '✗ Failed'}")
        print(f"Modbus interface: {'✓ Connected' if modbus_ok else '✗ Failed'}")
        
        return serial_ok, modbus_ok
    
    async def cleanup(self):
        """Clean up connections"""
        print("\nCleaning up...")
        self.system_monitor_active = False
        
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.serial_hand.disconnect)
        await loop.run_in_executor(None, self.modbus_hand.disconnect)
    
    def monitor_system_resources(self):
        """Background thread to monitor CPU and memory usage"""
        while self.system_monitor_active:
            cpu = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory().percent
            
            self.serial_metrics.add_system_metrics(cpu, memory)
            self.modbus_metrics.add_system_metrics(cpu, memory)
            time.sleep(0.1)
    
    async def serial_stress_worker(self, duration: int, request_rate: int):
        """Stress test worker for Serial interface"""
        print(f"🔄 Serial stress test: {request_rate} req/s for {duration}s")
        
        loop = asyncio.get_event_loop()
        interval = 1.0 / request_rate
        end_time = time.time() + duration
        
        # Test data: various command types
        test_commands = [
            np.array([0, 0, 0, 0, 200, 1000], dtype=np.int32),      # Open
            np.array([1000, 1000, 1000, 1000, 1000, 1000], dtype=np.int32),  # Close
            np.array([500, 500, 500, 500, 600, 1000], dtype=np.int32),  # Half
        ]
        cmd_idx = 0
        
        while time.time() < end_time:
            start_time = time.time()
            
            try:
                # Send command
                await loop.run_in_executor(None, self.serial_hand.set_angle, test_commands[cmd_idx])
                
                # Get response (position feedback)
                position = await loop.run_in_executor(None, self.serial_hand.get_angle_actual)
                
                latency = time.time() - start_time
                data_size = len(test_commands[cmd_idx]) * 4 + len(position) * 4  # Approximate bytes
                
                self.serial_metrics.add_measurement(latency, data_size, True, start_time)
                
            except Exception as e:
                latency = time.time() - start_time
                self.serial_metrics.add_measurement(latency, 0, False, start_time)
                print(f"Serial error: {e}")
            
            cmd_idx = (cmd_idx + 1) % len(test_commands)
            
            # Rate limiting
            elapsed = time.time() - start_time
            if elapsed < interval:
                await asyncio.sleep(interval - elapsed)
    
    async def modbus_stress_worker(self, duration: int, request_rate: int):
        """Stress test worker for Modbus interface"""
        print(f"🔄 Modbus stress test: {request_rate} req/s for {duration}s")
        
        loop = asyncio.get_event_loop()
        interval = 1.0 / request_rate
        end_time = time.time() + duration
        
        # Test different data types
        operations = [
            ("position", lambda: loop.run_in_executor(None, self.modbus_hand.get_angle_actual)),
            ("tactile", lambda: loop.run_in_executor(None, self.modbus_hand.get_tactile_data)),
            ("temperature", lambda: loop.run_in_executor(None, self.modbus_hand.get_temperature)),
        ]
        op_idx = 0
        
        while time.time() < end_time:
            start_time = time.time()
            
            try:
                op_name, operation = operations[op_idx]
                data = await operation()
                
                latency = time.time() - start_time
                
                # Estimate data size
                if op_name == "position" and data is not None:
                    data_size = len(data) * 4  # 4 bytes per int32
                elif op_name == "tactile" and data:
                    data_size = sum(sensor.nbytes for sensor in data.values())
                elif op_name == "temperature" and data is not None:
                    data_size = len(data) * 4
                else:
                    data_size = 0
                
                self.modbus_metrics.add_measurement(latency, data_size, True, start_time)
                
            except Exception as e:
                latency = time.time() - start_time
                self.modbus_metrics.add_measurement(latency, 0, False, start_time)
                print(f"Modbus error: {e}")
            
            op_idx = (op_idx + 1) % len(operations)
            
            # Rate limiting
            elapsed = time.time() - start_time
            if elapsed < interval:
                await asyncio.sleep(interval - elapsed)
    
    async def burst_test(self, interface: str, burst_size: int = 100):
        """Test maximum burst throughput"""
        print(f"\n🚀 Burst Test ({interface}): {burst_size} rapid requests")
        
        loop = asyncio.get_event_loop()
        start_time = time.time()
        
        if interface == "serial":
            test_cmd = np.array([500, 500, 500, 500, 500, 500], dtype=np.int32)
            
            for i in range(burst_size):
                req_start = time.time()
                try:
                    await loop.run_in_executor(None, self.serial_hand.set_angle, test_cmd)
                    latency = time.time() - req_start
                    self.serial_metrics.add_measurement(latency, len(test_cmd) * 4, True, req_start)
                except Exception:
                    latency = time.time() - req_start
                    self.serial_metrics.add_measurement(latency, 0, False, req_start)
        
        elif interface == "modbus":
            for i in range(burst_size):
                req_start = time.time()
                try:
                    data = await loop.run_in_executor(None, self.modbus_hand.get_angle_actual)
                    latency = time.time() - req_start
                    data_size = len(data) * 4 if data is not None else 0
                    self.modbus_metrics.add_measurement(latency, data_size, True, req_start)
                except Exception:
                    latency = time.time() - req_start
                    self.modbus_metrics.add_measurement(latency, 0, False, req_start)
        
        total_time = time.time() - start_time
        print(f"Burst completed in {total_time:.2f}s ({burst_size/total_time:.1f} req/s)")
    
    async def concurrent_stress_test(self, duration: int = 30):
        """Run both interfaces concurrently under stress"""
        print(f"\n⚡ Concurrent Stress Test: {duration}s duration")
        
        # Start system monitoring
        self.system_monitor_active = True
        monitor_thread = threading.Thread(target=self.monitor_system_resources)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        # Run both interfaces concurrently
        tasks = [
            self.serial_stress_worker(duration, request_rate=10),  # 10 req/s
            self.modbus_stress_worker(duration, request_rate=20),  # 20 req/s
        ]
        
        await asyncio.gather(*tasks, return_exceptions=True)
        self.system_monitor_active = False
    
    def generate_report(self):
        """Generate comprehensive performance report"""
        print("\n" + "="*60)
        print("STRESS TEST PERFORMANCE REPORT")
        print("="*60)
        
        # Serial Interface Report
        print(f"\n📊 SERIAL INTERFACE METRICS:")
        print(f"Total Requests: {self.serial_metrics.total_requests}")
        print(f"Success Rate: {((1-self.serial_metrics.error_rate)*100):.1f}%")
        print(f"Average Latency: {self.serial_metrics.avg_latency*1000:.2f}ms")
        print(f"Latency Std Dev: {self.serial_metrics.latency_std*1000:.2f}ms")
        print(f"Average Throughput: {self.serial_metrics.avg_throughput:.0f} bytes/s")
        
        if self.serial_metrics.latencies:
            print(f"Min Latency: {min(self.serial_metrics.latencies)*1000:.2f}ms")
            print(f"Max Latency: {max(self.serial_metrics.latencies)*1000:.2f}ms")
            print(f"95th Percentile: {np.percentile(self.serial_metrics.latencies, 95)*1000:.2f}ms")
        
        # Modbus Interface Report
        print(f"\n📊 MODBUS INTERFACE METRICS:")
        print(f"Total Requests: {self.modbus_metrics.total_requests}")
        print(f"Success Rate: {((1-self.modbus_metrics.error_rate)*100):.1f}%")
        print(f"Average Latency: {self.modbus_metrics.avg_latency*1000:.2f}ms")
        print(f"Latency Std Dev: {self.modbus_metrics.latency_std*1000:.2f}ms")
        print(f"Average Throughput: {self.modbus_metrics.avg_throughput:.0f} bytes/s")
        
        if self.modbus_metrics.latencies:
            print(f"Min Latency: {min(self.modbus_metrics.latencies)*1000:.2f}ms")
            print(f"Max Latency: {max(self.modbus_metrics.latencies)*1000:.2f}ms")
            print(f"95th Percentile: {np.percentile(self.modbus_metrics.latencies, 95)*1000:.2f}ms")
        
        # System Resource Usage
        if self.serial_metrics.cpu_usage:
            print(f"\n💻 SYSTEM RESOURCE USAGE:")
            print(f"Average CPU: {statistics.mean(self.serial_metrics.cpu_usage):.1f}%")
            print(f"Peak CPU: {max(self.serial_metrics.cpu_usage):.1f}%")
            print(f"Average Memory: {statistics.mean(self.serial_metrics.memory_usage):.1f}%")
            print(f"Peak Memory: {max(self.serial_metrics.memory_usage):.1f}%")
    
    def plot_results(self):
        """Generate visualization plots"""
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        fig.suptitle('Communication Throughput Stress Test Results', fontsize=16)
        
        # Latency comparison
        axes[0, 0].hist([l*1000 for l in self.serial_metrics.latencies], 
                       alpha=0.7, label='Serial', bins=30)
        axes[0, 0].hist([l*1000 for l in self.modbus_metrics.latencies], 
                       alpha=0.7, label='Modbus', bins=30)
        axes[0, 0].set_xlabel('Latency (ms)')
        axes[0, 0].set_ylabel('Frequency')
        axes[0, 0].set_title('Latency Distribution')
        axes[0, 0].legend()
        
        # Throughput over time
        if self.serial_metrics.timestamps and self.modbus_metrics.timestamps:
            serial_times = [(t - min(self.serial_metrics.timestamps)) for t in self.serial_metrics.timestamps]
            modbus_times = [(t - min(self.modbus_metrics.timestamps)) for t in self.modbus_metrics.timestamps]
            
            axes[0, 1].scatter(serial_times, self.serial_metrics.throughput_bps, 
                             alpha=0.6, label='Serial', s=1)
            axes[0, 1].scatter(modbus_times, self.modbus_metrics.throughput_bps, 
                             alpha=0.6, label='Modbus', s=1)
            axes[0, 1].set_xlabel('Time (s)')
            axes[0, 1].set_ylabel('Throughput (bytes/s)')
            axes[0, 1].set_title('Throughput Over Time')
            axes[0, 1].legend()
        
        # Latency over time
        if self.serial_metrics.timestamps:
            serial_times = [(t - min(self.serial_metrics.timestamps)) for t in self.serial_metrics.timestamps]
            axes[0, 2].plot(serial_times, [l*1000 for l in self.serial_metrics.latencies], 
                           alpha=0.7, label='Serial', linewidth=0.5)
        if self.modbus_metrics.timestamps:
            modbus_times = [(t - min(self.modbus_metrics.timestamps)) for t in self.modbus_metrics.timestamps]
            axes[0, 2].plot(modbus_times, [l*1000 for l in self.modbus_metrics.latencies], 
                           alpha=0.7, label='Modbus', linewidth=0.5)
        axes[0, 2].set_xlabel('Time (s)')
        axes[0, 2].set_ylabel('Latency (ms)')
        axes[0, 2].set_title('Latency Over Time')
        axes[0, 2].legend()
        
        # System resources
        if self.serial_metrics.cpu_usage:
            time_points = range(len(self.serial_metrics.cpu_usage))
            axes[1, 0].plot(time_points, self.serial_metrics.cpu_usage, label='CPU %')
            axes[1, 0].plot(time_points, self.serial_metrics.memory_usage, label='Memory %')
            axes[1, 0].set_xlabel('Time (0.1s intervals)')
            axes[1, 0].set_ylabel('Usage (%)')
            axes[1, 0].set_title('System Resource Usage')
            axes[1, 0].legend()
        
        # Error rates
        interfaces = ['Serial', 'Modbus']
        error_rates = [self.serial_metrics.error_rate * 100, self.modbus_metrics.error_rate * 100]
        axes[1, 1].bar(interfaces, error_rates, color=['blue', 'orange'])
        axes[1, 1].set_ylabel('Error Rate (%)')
        axes[1, 1].set_title('Error Rate Comparison')
        
        # Throughput comparison
        avg_throughputs = [self.serial_metrics.avg_throughput, self.modbus_metrics.avg_throughput]
        axes[1, 2].bar(interfaces, avg_throughputs, color=['blue', 'orange'])
        axes[1, 2].set_ylabel('Average Throughput (bytes/s)')
        axes[1, 2].set_title('Average Throughput Comparison')
        
        plt.tight_layout()
        
        # Save plot
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"stress_test_results_{timestamp}.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"\n📈 Results plotted and saved as: {filename}")
        
        plt.show()

async def main():
    """Main stress test execution"""
    tester = StressTester()
    
    try:
        # Setup
        serial_ok, modbus_ok = await tester.setup()
        
        if not (serial_ok or modbus_ok):
            print("❌ No interfaces available for testing!")
            return
        
        # Test sequence
        print("\n🔬 Starting comprehensive stress test sequence...")
        
        # 1. Burst tests
        if serial_ok:
            await tester.burst_test("serial", burst_size=50)
        if modbus_ok:
            await tester.burst_test("modbus", burst_size=100)
        
        # 2. Concurrent stress test
        if serial_ok and modbus_ok:
            await tester.concurrent_stress_test(duration=60)  # 1 minute
        
        # 3. Generate comprehensive report
        tester.generate_report()
        
        # 4. Plot results
        tester.plot_results()
        
    except KeyboardInterrupt:
        print("\n⏹️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
    finally:
        await tester.cleanup()

if __name__ == "__main__":
    print("Communication Throughput Stress Test")
    print("Note: Adjust COM port and IP address in StressTester() constructor!")
    print("Required packages: matplotlib, psutil, numpy")
    asyncio.run(main())
