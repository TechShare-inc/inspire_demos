#!/usr/bin/env python3
"""
Inspire Hand Modbus Communication Demo Suite
Interactive demonstration of Modbus communication and sensor reading capabilities
"""
import time
import asyncio
import traceback
import numpy as np
from loguru import logger
from inspire_demos.inspire_modbus import InspireHandModbus

# Optional matplotlib for heatmap visualization
try:
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation
    from matplotlib.colors import LinearSegmentedColormap
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


class ModbusDemo:
    """Interactive demonstration of Modbus communication and sensor features"""
    
    def __init__(self, generation=4):
        self.api = None
        self.ip = "192.168.11.210"  # Default IP
        self.port = 6000
        self.generation = generation
    
    def configure_connection(self):
        """Allow user to configure connection settings."""
        print(f"Current settings:")
        print(f"  IP Address: {self.ip}")
        print(f"  Port: {self.port}")
        print(f"  Generation: {self.generation}")
        
        while True:
            print("\nWhat would you like to configure?")
            print("1. Change IP Address")
            print("2. Change Port")
            print("3. Change Generation")
            print("4. Test Current Settings")
            print("5. Continue with current settings")
            
            choice = input("\nEnter your choice (1-5): ").strip()
            
            if choice == "1":
                new_ip = input(f"Enter new IP address (current: {self.ip}): ").strip()
                if new_ip:
                    self.ip = new_ip
                    print(f"IP address set to {self.ip}")
            elif choice == "2":
                try:
                    new_port = int(input(f"Enter new port (current: {self.port}): "))
                    self.port = new_port
                    print(f"Port set to {self.port}")
                except ValueError:
                    print("Invalid port. Please enter a number.")
            elif choice == "3":
                try:
                    new_gen = int(input(f"Enter generation (current: {self.generation}): "))
                    if new_gen in [3, 4]:
                        self.generation = new_gen
                        print(f"Generation set to {self.generation}")
                    else:
                        print("Invalid generation. Please enter 3 or 4.")
                except ValueError:
                    print("Invalid generation. Please enter a number.")
            elif choice == "4":
                print("Testing connection with current settings...")
                if self.connect_to_hand():
                    print("Connection test successful!")
                    self.disconnect_from_hand()
                else:
                    print("Connection test failed!")
            elif choice == "5":
                break
            else:
                print("Invalid choice. Please select 1-5.")
    
    def connect_to_hand(self):
        """Connect to the hand with current settings."""
        print(f"\nConnecting to {self.ip}:{self.port} (Gen {self.generation})...")
        
        try:
            self.api = InspireHandModbus(ip=self.ip, port=self.port, generation=self.generation)
            if self.api.connect():
                print(f"Successfully connected to the Gen {self.generation} hand!")
                return True
            else:
                print("Failed to connect. Please check your network settings.")
                self.api = None
                return False
            
        except Exception as e:
            print(f"Failed to connect: {e}")
            print("You can change settings using the configuration menu.")
            self.api = None
            return False
    
    def disconnect_from_hand(self):
        """Safely disconnect from the hand."""
        if self.api:
            try:
                self.api.disconnect()
                print("Disconnected from the hand.")
            except Exception as e:
                print(f"Error during disconnect: {e}")
            finally:
                self.api = None
    
    def demo_basic_sensor_reading(self):
        """Demonstrate basic sensor reading functionality."""
        print("\nDEMO: Basic Sensor Reading")
        print("="*50)
        print("This demo shows basic sensor reading capabilities:")
        print("- Hand position sensors")
        print("- Temperature sensors")
        print("- Error status monitoring")
        print(f"Using connection: {self.ip}:{self.port}")
        
        if not self.api:
            if not self.connect_to_hand():
                return
        
        try:
            print("\n--- Reading Basic Sensors ---")
            
            # Read actual angles
            print("1. Reading actual finger angles...")
            actual_angles = self.api.get_angle_actual()
            print(f"   Finger positions: {actual_angles}")
            
            # Read temperatures
            print("2. Reading temperature sensors...")
            temps = self.api.get_temperature()
            print(f"   Temperatures: {temps}")
            
            # Read error status
            print("3. Reading error status...")
            errors = self.api.get_error()
            print(f"   Error codes: {errors}")
            
            # Read target angles for comparison
            print("4. Reading target finger angles...")
            target_angles = self.api.get_angle_set()
            print(f"   Target positions: {target_angles}")
            
            print("\n✓ Basic sensor reading completed successfully!")
            
        except Exception as e:
            print(f"Error during sensor reading: {e}")
    
    def demo_tactile_sensor_overview(self):
        """Demonstrate tactile sensor overview."""
        print("\nDEMO: Tactile Sensor Overview")
        print("="*50)
        print("This demo provides an overview of all tactile sensors:")
        print("- Sensor identification")
        print("- Data dimensions")
        print("- Signal range analysis")
        print(f"Using connection: {self.ip}:{self.port}")
        
        if not self.api:
            if not self.connect_to_hand():
                return
        
        try:
            if self.generation < 4:
                print("Tactile sensors are only available on Gen 4 hardware.")
                print("Please configure the generation setting to 4 if you have Gen 4 hardware.")
                return
            
            print("\n--- Tactile Sensor Overview ---")
            
            # Get all tactile data
            tactile_data = self.api.get_tactile_data()
            
            print(f"Successfully detected {len(tactile_data)} tactile sensors:")
            
            # Display summary for each sensor
            for sensor_name, data in tactile_data.items():
                rows, cols = data.shape
                data_min, data_max = data.min(), data.max()
                data_mean = data.mean()
                
                print(f"  {sensor_name:15} | Shape: {rows:2}x{cols:2} | "
                      f"Range: [{data_min:4}, {data_max:4}] | Mean: {data_mean:6.1f}")
            
            print("\n✓ Tactile sensor overview completed successfully!")
            
        except Exception as e:
            print(f"Error during tactile sensor overview: {e}")
    
    def demo_specific_sensor_reading(self):
        """Demonstrate reading specific tactile sensors in detail."""
        print("\nDEMO: Specific Sensor Reading")
        print("="*50)
        print("This demo reads specific tactile sensors in detail:")
        print("- Palm sensor (largest)")
        print("- Thumb tip sensor")
        print("- Finger tip sensors")
        print(f"Using connection: {self.ip}:{self.port}")
        
        if not self.api:
            if not self.connect_to_hand():
                return
        
        try:
            if self.generation < 4:
                print("Tactile sensors are only available on Gen 4 hardware.")
                return
            
            print("\n--- Detailed Sensor Data ---")
            
            # Palm sensor (largest)
            print("1. Palm sensor (8x14 matrix):")
            palm_data = self.api.get_tactile_sensor_data('palm')
            print(f"   Shape: {palm_data.shape}")
            print(f"   Data preview:\n{palm_data[:4, :7]}  # (showing first 4x7 section)")
            print(f"   Full range: [{palm_data.min()}, {palm_data.max()}], Mean: {palm_data.mean():.1f}")
            
            # Thumb tip sensor
            print("\n2. Thumb tip sensor (12x8 matrix):")
            thumb_tip_data = self.api.get_tactile_sensor_data('thumb_tip')
            print(f"   Shape: {thumb_tip_data.shape}")
            print(f"   Data preview:\n{thumb_tip_data[:4, :4]}  # (showing first 4x4 section)")
            print(f"   Full range: [{thumb_tip_data.min()}, {thumb_tip_data.max()}], Mean: {thumb_tip_data.mean():.1f}")
            
            # Index finger tip
            print("\n3. Index finger tip sensor:")
            try:
                index_tip_data = self.api.get_tactile_sensor_data('index_tip')
                print(f"   Shape: {index_tip_data.shape}")
                print(f"   Data:\n{index_tip_data}")
                print(f"   Range: [{index_tip_data.min()}, {index_tip_data.max()}], Mean: {index_tip_data.mean():.1f}")
            except Exception as e:
                print(f"   Could not read index tip sensor: {e}")
            
            # Pinky top (small sensor)
            print("\n4. Pinky top sensor (small, 3x3 matrix):")
            try:
                pinky_top_data = self.api.get_tactile_sensor_data('pinky_top')
                print(f"   Shape: {pinky_top_data.shape}")
                print(f"   Data:\n{pinky_top_data}")
                print(f"   Range: [{pinky_top_data.min()}, {pinky_top_data.max()}], Mean: {pinky_top_data.mean():.1f}")
            except Exception as e:
                print(f"   Could not read pinky top sensor: {e}")
            
            print("\n✓ Specific sensor reading completed successfully!")
            
        except Exception as e:
            print(f"Error during specific sensor reading: {e}")
    
    def demo_continuous_sensor_monitoring(self):
        """Demonstrate continuous sensor monitoring with heatmap visualization."""
        print("\nDEMO: Continuous Sensor Monitoring")
        print("="*50)
        print("This demo continuously monitors sensors in real-time:")
        print("- Updates every 0.5 seconds")
        print("- Shows live tactile sensor data")
        print("- Displays heatmaps for all available sensors")
        print("- Press Ctrl+C to stop")
        print(f"Using connection: {self.ip}:{self.port}")
        
        if not self.api:
            if not self.connect_to_hand():
                return
        
        try:
            if self.generation < 4:
                print("Tactile sensors are only available on Gen 4 hardware.")
                return
            
            # Check if matplotlib is available for heatmaps
            if not MATPLOTLIB_AVAILABLE:
                print("Matplotlib not available. Install with: pip install matplotlib")
                print("Falling back to text-only display...")
                self._continuous_monitoring_text_only()
                return
            
            print("\n--- Starting Continuous Monitoring with All Sensor Heatmaps ---")
            print("Data will be refreshed every 0.5 seconds")
            print("Close the matplotlib window or press Ctrl+C to stop\n")
            
            # Get initial tactile data to set up the plots
            tactile_data = self.api.get_tactile_data()
            num_sensors = len(tactile_data)
            
            if num_sensors == 0:
                print("No tactile sensors detected!")
                return
            
            print(f"Setting up heatmaps for {num_sensors} sensors...")
            
            # Calculate optimal grid layout
            import math
            if num_sensors <= 4:
                rows, cols = 2, 2
            elif num_sensors <= 6:
                rows, cols = 2, 3
            elif num_sensors <= 9:
                rows, cols = 3, 3
            elif num_sensors <= 12:
                rows, cols = 3, 4
            elif num_sensors <= 16:
                rows, cols = 4, 4
            elif num_sensors <= 20:
                rows, cols = 4, 5
            else:
                # For very large number of sensors, use a square-ish layout
                cols = math.ceil(math.sqrt(num_sensors))
                rows = math.ceil(num_sensors / cols)
            
            # Set up matplotlib figures with dynamic sizing
            plt.ion()  # Interactive mode
            fig_width = max(16, cols * 4)
            fig_height = max(12, rows * 3)
            fig, axes = plt.subplots(rows, cols, figsize=(fig_width, fig_height))
            fig.suptitle(f'Real-time Tactile Sensor Heatmaps ({num_sensors} sensors)', 
                        fontsize=16, fontweight='bold')
            
            # Ensure axes is always 2D array
            if rows == 1 and cols == 1:
                axes = np.array([[axes]])
            elif rows == 1 or cols == 1:
                axes = axes.reshape(rows, cols)
            
            # Create custom colormap (blue to red)
            colors = ['#000080', '#0000FF', '#00FFFF', '#FFFF00', '#FF8000', '#FF0000']
            n_bins = 256
            cmap = LinearSegmentedColormap.from_list('tactile', colors, N=n_bins)
            
            # Initialize heatmap plots for all sensors
            heatmaps = []
            sensor_names = list(tactile_data.keys())
            
            for i, (sensor_name, data) in enumerate(tactile_data.items()):
                row = i // cols
                col = i % cols
                ax = axes[row, col]
                
                # Calculate appropriate vmax based on data range
                data_max = max(4095, data.max() * 1.2)  # Allow some headroom
                
                im = ax.imshow(data, cmap=cmap, interpolation='nearest', vmin=0, vmax=data_max)
                ax.set_title(f'{sensor_name}\n({data.shape[0]}x{data.shape[1]})', fontsize=9)
                ax.set_xlabel('Col', fontsize=8)
                ax.set_ylabel('Row', fontsize=8)
                
                # Make ticks smaller for better readability
                ax.tick_params(axis='both', which='major', labelsize=7)
                
                # Add compact colorbar
                plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04, shrink=0.8)
                
                heatmaps.append(im)
            
            # Hide unused subplots
            total_plots = rows * cols
            for i in range(num_sensors, total_plots):
                row = i // cols
                col = i % cols
                axes[row, col].set_visible(False)
            
            plt.tight_layout()
            plt.show(block=False)
            
            loop_count = 0
            start_time = time.time()
            
            try:
                while True:
                    loop_count += 1
                    current_time = time.time()
                    
                    # Get fresh tactile data
                    tactile_data = self.api.get_tactile_data()
                    
                    # Update console display (compact format)
                    elapsed = current_time - start_time
                    print(f"\r--- Reading #{loop_count} (t={elapsed:.1f}s) - {num_sensors} sensors ---", end="")
                    
                    # Update heatmaps
                    for i, sensor_name in enumerate(sensor_names):
                        if sensor_name in tactile_data and i < len(heatmaps):
                            data = tactile_data[sensor_name]
                            heatmaps[i].set_array(data)
                            
                            # Update title with current stats (compact format)
                            data_min, data_max = data.min(), data.max()
                            data_mean = data.mean()
                            title = f'{sensor_name}\n({data.shape[0]}x{data.shape[1]}) | [{data_min}-{data_max}] | μ={data_mean:.0f}'
                            
                            row = i // cols
                            col = i % cols
                            axes[row, col].set_title(title, fontsize=9)
                    
                    # Force matplotlib to update
                    plt.pause(0.01)
                    
                    # Print detailed stats every 20th loop (less frequent for all sensors)
                    if loop_count % 20 == 0:
                        print(f"\n--- Detailed Stats (Reading #{loop_count}) ---")
                        for sensor_name, data in tactile_data.items():
                            rows_data, cols_data = data.shape
                            data_min, data_max = data.min(), data.max()
                            data_mean = data.mean()
                            print(f"  {sensor_name:15} | {rows_data:2}x{cols_data:2} | [{data_min:4}, {data_max:4}] | Mean: {data_mean:6.1f}")
                    
                    time.sleep(0.5)  # Wait 0.5 seconds before next reading
                    
            except KeyboardInterrupt:
                print("\nStopping continuous monitoring...")
            except Exception as e:
                print(f"\nError in monitoring loop: {e}")
            finally:
                plt.close('all')
            
            print("✓ Continuous monitoring stopped.")
                    
        except KeyboardInterrupt:
            print("\nContinuous monitoring interrupted.")
        except Exception as e:
            print(f"Error during continuous monitoring: {e}")
    
    def _continuous_monitoring_text_only(self):
        """Fallback continuous monitoring without heatmaps."""
        print("\n--- Starting Text-Only Continuous Monitoring ---")
        print("Data will be refreshed every 0.5 seconds")
        print("Press Ctrl+C to stop\n")
        
        loop_count = 0
        
        while True:
            try:
                loop_count += 1
                print(f"--- Reading #{loop_count} ---")
                
                # Get all tactile data
                tactile_data = self.api.get_tactile_data()
                
                # Display summary for each sensor
                for sensor_name, data in tactile_data.items():
                    rows, cols = data.shape
                    data_min, data_max = data.min(), data.max()
                    data_mean = data.mean()
                    
                    print(f"  {sensor_name:15} | Shape: {rows:2}x{cols:2} | "
                          f"Range: [{data_min:4}, {data_max:4}] | Mean: {data_mean:6.1f}")
                
                # Show detailed data for key sensors every 5th loop
                if loop_count % 5 == 0:
                    print("\n--- Detailed Data (every 5th reading) ---")
                    
                    # Palm sensor preview
                    try:
                        palm_data = self.api.get_tactile_sensor_data('palm')
                        print(f"Palm sensor preview (first 3x6):\n{palm_data[:3, :6]}")
                    except:
                        pass
                    
                    # Thumb tip sensor preview
                    try:
                        thumb_tip_data = self.api.get_tactile_sensor_data('thumb_tip')
                        print(f"Thumb tip preview (first 3x4):\n{thumb_tip_data[:3, :4]}")
                    except:
                        pass
                
                time.sleep(0.5)  # Wait 0.5 seconds before next reading
                
            except KeyboardInterrupt:
                print("\nStopping continuous monitoring...")
                break
            except Exception as e:
                print(f"Error in monitoring loop: {e}")
                time.sleep(1)  # Brief pause before retrying
    
    def demo_sensor_validation(self):
        """Demonstrate sensor validation and diagnostics."""
        print("\nDEMO: Sensor Validation")
        print("="*50)
        print("This demo validates sensor functionality:")
        print("- Register address validation")
        print("- Sensor connectivity check")
        print("- Data integrity verification")
        print(f"Using connection: {self.ip}:{self.port}")
        
        if not self.api:
            if not self.connect_to_hand():
                return
        
        try:
            print("\n--- Sensor Validation ---")
            
            # Validate register addresses
            print("1. Validating register addresses...")
            try:
                validation_results = self.api.validate_register_addresses()
                successful_validations = sum(validation_results.values())
                total_validations = len(validation_results)
                print(f"   Register validation: {successful_validations}/{total_validations} successful")
                
                # Show detailed results
                for register, success in validation_results.items():
                    status = "✓" if success else "✗"
                    print(f"   {status} {register}")
                    
            except Exception as e:
                print(f"   Register validation failed: {e}")
            
            # Test basic connectivity
            print("\n2. Testing basic sensor connectivity...")
            try:
                # Test basic position reading
                angles = self.api.get_angle_actual()
                print(f"   ✓ Position sensors: {len(angles)} readings")
                
                # Test temperature sensors
                temps = self.api.get_temperature()
                print(f"   ✓ Temperature sensors: {len(temps)} readings")
                
                # Test error status
                errors = self.api.get_error()
                print(f"   ✓ Error sensors: {len(errors)} readings")
                
            except Exception as e:
                print(f"   ✗ Basic sensor connectivity failed: {e}")
            
            # Test tactile sensors if available
            if self.generation >= 4:
                print("\n3. Testing tactile sensor connectivity...")
                try:
                    tactile_data = self.api.get_tactile_data()
                    print(f"   ✓ Tactile sensors: {len(tactile_data)} sensors detected")
                    
                    # Check for reasonable data ranges
                    for sensor_name, data in tactile_data.items():
                        if data.max() > 10000 or data.min() < -1000:
                            print(f"   ⚠ {sensor_name}: Unusual data range [{data.min()}, {data.max()}]")
                        else:
                            print(f"   ✓ {sensor_name}: Normal data range [{data.min()}, {data.max()}]")
                            
                except Exception as e:
                    print(f"   ✗ Tactile sensor connectivity failed: {e}")
            else:
                print("\n3. Tactile sensors not available on Gen 3 hardware.")
            
            print("\n✓ Sensor validation completed!")
            
        except Exception as e:
            print(f"Error during sensor validation: {e}")
    
    def demo_connection_test(self):
        """Test connection reliability and basic functionality."""
        print("\nDEMO: Connection Test")
        print("="*50)
        print("This demo tests the Modbus connection:")
        print("- Connection establishment")
        print("- Basic communication")
        print("- Error handling")
        print("- Disconnection")
        print(f"Using connection: {self.ip}:{self.port}")
        
        # Test connection
        if not self.connect_to_hand():
            print("Connection test failed!")
            return
        
        try:
            print("\n--- Testing Connection ---")
            
            print("1. Testing basic communication...")
            try:
                # Simple read operation
                angles = self.api.get_angle_actual()
                print(f"   ✓ Communication successful: {len(angles)} values read")
            except Exception as e:
                print(f"   ✗ Communication failed: {e}")
            
            print("2. Testing multiple read operations...")
            success_count = 0
            for i in range(5):
                try:
                    self.api.get_angle_actual()
                    success_count += 1
                except:
                    pass
            print(f"   ✓ Multiple reads: {success_count}/5 successful")
            
            print("3. Testing different sensor types...")
            sensor_tests = [
                ("Position", lambda: self.api.get_angle_actual()),
                ("Temperature", lambda: self.api.get_temperature()),
                ("Error Status", lambda: self.api.get_error()),
            ]
            
            for sensor_name, test_func in sensor_tests:
                try:
                    test_func()
                    print(f"   ✓ {sensor_name} sensors: Working")
                except Exception as e:
                    print(f"   ✗ {sensor_name} sensors: {e}")
            
            print("\n✓ Connection test completed successfully!")
            
        except Exception as e:
            print(f"Connection test failed: {e}")
        
        finally:
            self.disconnect_from_hand()


async def interactive_demo():
    """Interactive demonstration menu."""
    demo = ModbusDemo()
    
    print("INSPIRE HAND MODBUS COMMUNICATION DEMO")
    print("=" * 60)
    print("This demo showcases Modbus communication and sensor reading.")
    print("Ensure your Inspire Hand is properly connected via Ethernet.")
    print()
    
    # Configure connection at the beginning
    print("First, let's configure your connection settings...")
    demo.configure_connection()
    
    print(f"\nConnection configured: {demo.ip}:{demo.port} (Gen {demo.generation})")
    print("You can change settings later using option 7 in the menu.")
    
    while True:
        print("\nSelect a demo scenario:")
        print("1. Connection Test (verify basic functionality)")
        print("2. Basic Sensor Reading (positions, temperatures, errors)")
        print("3. Tactile Sensor Overview (all sensors summary)")
        print("4. Specific Sensor Reading (detailed sensor data)")
        print("5. Continuous Monitoring (real-time sensor updates)")
        print("6. Sensor Validation (diagnostics and connectivity)")
        print("7. Configure Connection Settings")
        print("8. Exit")
        
        try:
            choice = input("\nEnter your choice (1-8): ").strip()
            
            if choice == "1":
                await asyncio.sleep(0)  # Make it async-compatible
                demo.demo_connection_test()
            elif choice == "2":
                await asyncio.sleep(0)
                demo.demo_basic_sensor_reading()
            elif choice == "3":
                await asyncio.sleep(0)
                demo.demo_tactile_sensor_overview()
            elif choice == "4":
                await asyncio.sleep(0)
                demo.demo_specific_sensor_reading()
            elif choice == "5":
                await asyncio.sleep(0)
                demo.demo_continuous_sensor_monitoring()
            elif choice == "6":
                await asyncio.sleep(0)
                demo.demo_sensor_validation()
            elif choice == "7":
                await asyncio.sleep(0)
                demo.configure_connection()
            elif choice == "8":
                print("Exiting demo...")
                break
            else:
                print("Invalid choice. Please select 1-8.")
                
        except KeyboardInterrupt:
            print("\nDemo interrupted.")
            break
        except Exception as e:
            print(f"Demo error: {e}")
            traceback.print_exc()
        
        finally:
            # Ensure clean disconnect
            if demo.api:
                demo.disconnect_from_hand()


def print_demo_concepts():
    """Print educational content about Modbus communication and sensors."""
    print("\nMODBUS COMMUNICATION & SENSOR CONCEPTS")
    print("=" * 60)
    print("""
WHAT IS MODBUS COMMUNICATION?

Modbus is an industrial communication protocol that provides:
• Network-based communication over Ethernet
• Real-time sensor data acquisition
• Robust error handling and diagnostics
• Support for multiple simultaneous connections

KEY CONCEPTS:

1. NETWORK CONFIGURATION
   • IP address and port settings
   • TCP/IP communication protocol
   • Generation-specific capabilities

2. SENSOR TYPES
   • Position sensors: Real-time finger angles
   • Temperature sensors: Thermal monitoring
   • Error sensors: System status and diagnostics
   • Tactile sensors: Touch/pressure data (Gen 4 only)

3. TACTILE SENSOR SYSTEM (GEN 4)
   • Multiple sensors across hand surface
   • Matrix-based pressure data
   • Real-time touch detection
   • High-resolution spatial information
   • Visual heatmap representation

SENSOR READING CAPABILITIES:

• Real-time position monitoring
• Temperature-based safety monitoring
• Comprehensive error diagnostics
• Advanced tactile feedback (Gen 4)
• Continuous data streaming
• Interactive heatmap visualization (with matplotlib)

VISUALIZATION FEATURES:

• Real-time heatmap display of tactile data
• Color-coded pressure visualization
• Multiple sensor simultaneous display
• 0.5-second update rate for responsive feedback
• Statistical overlays (min/max/mean values)

PRACTICAL APPLICATIONS:

• Advanced robotic manipulation
• Real-time feedback control
• Safety monitoring systems
• Research and development
• Human-robot interaction studies
• Touch-sensitive grasp control
""")

    if MATPLOTLIB_AVAILABLE:
        print("\n✓ Matplotlib available - Heatmap visualization enabled")
    else:
        print("\n⚠ Matplotlib not available - Install with: pip install matplotlib")
        print("  for enhanced heatmap visualization features")


async def main():
    """Main demo entry point."""
    print_demo_concepts()
    
    print("\nReady to run interactive sensor demos?")
    response = input("Press Enter to start, or 'q' to quit: ").strip().lower()
    
    if response != 'q':
        await interactive_demo()
    else:
        print("See you next time!")


if __name__ == "__main__":
    print("Inspire Hand Modbus Communication Demo")
    print("Configure your network settings in the demo menu!")
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
    except Exception as e:
        print(f"\nDemo failed: {e}")
        traceback.print_exc()
