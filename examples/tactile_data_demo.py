#!/usr/bin/env python3
"""
Simple Tactile Data Collection Demo
Collects tactile data for 10 seconds and plots the trends
"""

import asyncio
import time
import numpy as np

from inspire_demos.inspire_modbus import InspireHandModbus

# Import matplotlib for plotting
try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Warning: matplotlib not available. Install with: pip install matplotlib")

MODBUS_IP = "192.168.11.210"  # Adjust for your system

async def collect_and_plot_tactile_data():
    """
    Simple function to collect tactile data for 10 seconds and plot trends
    """
    print("Simple Tactile Data Collection Demo")
    print("=" * 40)
    print(f"Connecting to Gen4 hand at IP: {MODBUS_IP}")
    
    # Initialize the Modbus connection
    hand = InspireHandModbus(ip=MODBUS_IP, generation=4)
    
    # Connect
    print("Connecting to hand...")
    loop = asyncio.get_event_loop()
    connected = await loop.run_in_executor(None, hand.connect)
    
    if not connected:
        print("Failed to connect! Check IP address and connection.")
        return
    
    print("Connected! Starting data collection...")
    
    # Data storage
    timestamps = []
    sensor_means = {}  # Store mean values for each sensor over time
    
    try:
        # Collect data for 10 seconds
        start_time = time.time()
        duration = 5.0
        sample_count = 0
        
        while time.time() - start_time < duration:
            try:
                # Get tactile data
                tactile_data = await loop.run_in_executor(None, hand.get_tactile_data)
                
                if tactile_data:
                    current_time = time.time() - start_time  # Relative time
                    timestamps.append(current_time)
                    
                    # Calculate mean value for each sensor and store
                    for sensor_name, sensor_matrix in tactile_data.items():
                        mean_value = float(np.mean(sensor_matrix))
                        
                        if sensor_name not in sensor_means:
                            sensor_means[sensor_name] = []
                        sensor_means[sensor_name].append(mean_value)
                    
                    sample_count += 1
                    
                    # Progress update every 2 seconds
                    if sample_count % 20 == 0:
                        print(f"  Collected {sample_count} samples at {current_time:.1f}s")
                
                # Small delay to avoid overwhelming the system
                await asyncio.sleep(0.005)
                
            except Exception as e:
                print(f"Error collecting sample: {e}")
        
        print(f"Data collection complete! Collected {sample_count} samples over {duration} seconds")
        

        # Plot the data if matplotlib is available
        if MATPLOTLIB_AVAILABLE and timestamps:
            plot_tactile_trends(timestamps, sensor_means)
        else:
            print("Cannot plot: matplotlib not available or no data collected")
            
        # Print summary statistics
        print_data_summary(sensor_means)
        
    finally:
        # Always disconnect
        print("Disconnecting...")
        await loop.run_in_executor(None, hand.disconnect)
        print("Disconnected")

def plot_tactile_trends(timestamps, sensor_means):
    """
    Plot the trends of tactile sensor data over time
    """
    print("\nGenerating trend plots...")
    
    # Get list of sensors that have data
    sensors_with_data = [name for name, values in sensor_means.items() if values]
    
    if not sensors_with_data:
        print("No sensor data to plot!")
        return
    
    # Filter to only show pinky sensor for testing
    pinky_sensors = [name for name in sensors_with_data if 'pinky' in name.lower()]
    if not pinky_sensors:
        print("No pinky sensor data found!")
        return
    
    # Create subplot for pinky only
    fig, axes = plt.subplots(1, 1, figsize=(10, 4))
    axes = [axes]  # Make it a list for consistency with the rest of the code
    sensors_with_data = pinky_sensors[:1]  # Only take first pinky sensor
    
    fig.suptitle('Tactile Sensor Trends Over 10 Seconds', fontsize=14, fontweight='bold')
    
    # Convert timestamps from seconds to milliseconds
    timestamps_ms = [t * 1000 for t in timestamps]
    
    for i, sensor_name in enumerate(sensors_with_data[:4]):
        values = sensor_means[sensor_name]
        
        # Plot the trend dots
        axes[i].plot(timestamps_ms[:len(values)], values, 'bo', markersize=4, label=sensor_name)
        axes[i].set_title(f"{sensor_name.replace('_', ' ').title()}")
        axes[i].set_ylabel('Mean Value')
        axes[i].grid(True, alpha=0.3)
        
        # Add some statistics to the plot
        mean_val = np.mean(values)
        max_val = np.max(values)
        min_val = np.min(values)
        axes[i].axhline(y=mean_val, color='r', linestyle='--', alpha=0.7, label=f'Mean: {mean_val:.1f}')
        
        axes[i].legend()
    
    # Set x-label only for the bottom plot
    axes[-1].set_xlabel('Time (ms)')
    
    plt.tight_layout()
    plt.show()
    
    print("Plot displayed!")

def print_data_summary(sensor_means):
    """
    Print summary statistics of collected data
    """
    print("\nDATA SUMMARY:")
    print("-" * 30)
    
    for sensor_name, values in sensor_means.items():
        if values:
            mean_val = np.mean(values)
            std_val = np.std(values)
            min_val = np.min(values)
            max_val = np.max(values)
            
            print(f"{sensor_name}:")
            print(f"  Samples: {len(values)}")
            print(f"  Mean: {mean_val:.2f}")
            print(f"  Std Dev: {std_val:.2f}")
            print(f"  Range: {min_val:.1f} - {max_val:.1f}")
            print()

async def main():
    """
    Main function - just run the demo
    """
    if not MATPLOTLIB_AVAILABLE:
        response = input("Matplotlib not found. Continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Install matplotlib with: pip install matplotlib")
            return
    
    print("This demo will collect tactile data for 10 seconds and show trends.")
    print(f"Make sure your Gen4 hand is connected at: {MODBUS_IP}")
    
    input("Press Enter to start data collection...")
    
    await collect_and_plot_tactile_data()
    
    print("\nDemo completed!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
    except Exception as e:
        print(f"\nDemo failed: {e}")
        import traceback
        traceback.print_exc()
