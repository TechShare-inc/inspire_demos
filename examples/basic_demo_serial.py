#!/usr/bin/env python3
"""
Inspire Hand Serial Communication Demo Suite
Interactive demonstration of serial communication capabilities
"""
import time
import asyncio
import traceback
import serial.tools.list_ports
import numpy as np
from inspire_demos import InspireHandSerial


# Predefined motion patterns
BASIC_MOTION = np.array([
    [1000, 1000, 1000, 1000, 1000, 1000],  # Open
    [1000, 1000, 1000, 1000, 1000, 0],     # Close thumb
    [1000, 1000, 1000, 1000, 1000, 1000],  # Open
    [1000, 1000, 1000, 1000, 200, 1000],   # Close ring finger
    [1000, 1000, 1000, 0, 200, 1000],      # Close middle finger
    [1000, 1000, 0, 0, 200, 1000],         # Close index finger
    [1000, 0, 0, 0, 200, 1000],            # Close pinky
    [0, 0, 0, 0, 200, 1000],               # Close all
])

PRECISION_GRIP = np.array([
    [1000, 1000, 1000, 1000, 1000, 1000],  # Open
    [800, 1000, 1000, 1000, 1000, 300],    # Precision grip position
    [600, 1000, 1000, 1000, 1000, 100],    # Tighter grip
    [800, 1000, 1000, 1000, 1000, 300],    # Release slightly
    [1000, 1000, 1000, 1000, 1000, 1000],  # Open
])

POWER_GRIP = np.array([
    [1000, 1000, 1000, 1000, 1000, 1000],  # Open
    [500, 500, 500, 500, 500, 1000],       # Power grip all fingers
    [200, 200, 200, 200, 200, 1000],       # Tight power grip
    [500, 500, 500, 500, 500, 1000],       # Loosen
    [1000, 1000, 1000, 1000, 1000, 1000],  # Open
])

FINGER_WAVE = np.array([
    [1000, 1000, 1000, 1000, 1000, 1000],  # All open
    [0, 1000, 1000, 1000, 1000, 1000],     # Close pinky
    [1000, 0, 1000, 1000, 1000, 1000],     # Close ring finger
    [1000, 1000, 0, 1000, 1000, 1000],     # Close middle finger
    [1000, 1000, 1000, 0, 1000, 1000],     # Close index finger
    [1000, 1000, 1000, 1000, 0, 1000],     # Close thumb flexion
    [1000, 1000, 1000, 1000, 1000, 0],     # Close thumb
    [1000, 1000, 1000, 1000, 1000, 1000],  # All open
])


class SerialDemo:
    """Interactive demonstration of serial communication features"""
    
    def __init__(self):
        self.api = None
        self.port = None
        self.baudrate = 115200
        self.generation = 4
    
    def list_serial_ports(self):
        """List all available serial ports and return them as a list."""
        ports = serial.tools.list_ports.comports()
        available_ports = []
        
        print("\nAvailable Serial Ports:")
        print("-" * 50)
        
        if not ports:
            print("No serial ports found!")
            return available_ports
        
        for i, port in enumerate(ports, 1):
            available_ports.append(port.device)
            print(f"{i}. {port.device} - {port.description}")
            if port.manufacturer:
                print(f"   Manufacturer: {port.manufacturer}")
            if port.serial_number:
                print(f"   Serial Number: {port.serial_number}")
            print()
        
        return available_ports
    
    def select_port(self):
        """Allow user to select a serial port from available options."""
        available_ports = self.list_serial_ports()
        
        if not available_ports:
            print("No serial ports available. Please check your connections.")
            return None
        
        while True:
            try:
                choice = input(f"Select a port (1-{len(available_ports)}) or 'q' to quit: ").strip()
                
                if choice.lower() == 'q':
                    print("Cancelled port selection.")
                    return None
                
                port_index = int(choice) - 1
                if 0 <= port_index < len(available_ports):
                    selected_port = available_ports[port_index]
                    print(f"Selected port: {selected_port}")
                    return selected_port
                else:
                    print(f"Invalid selection. Please choose a number between 1 and {len(available_ports)}")
            
            except ValueError:
                print("Invalid input. Please enter a number or 'q' to quit.")
            except KeyboardInterrupt:
                print("\nCancelled.")
                return None
    
    def connect_to_hand(self, port: str = None):
        """Connect to the hand with the specified or stored port."""
        if port is None:
            if self.port is None:
                port = self.select_port()
                if port is None:
                    return False
                self.port = port
            else:
                port = self.port
        
        print(f"\nConnecting to {port} at {self.baudrate} baud...")
        
        try:
            self.api = InspireHandSerial(port, self.baudrate, generation=self.generation)
            self.api.connect()
            print(f"Successfully connected to the Gen {self.generation} hand!")
            
            # Initialize hand
            self.api.reset_error()
            time.sleep(0.1)
            self.api.perform_open()
            time.sleep(0.8)
            
            return True
            
        except Exception as e:
            print(f"Failed to connect to {port}: {e}")
            print("You can try a different port using the configuration menu (option 8).")
            self.api = None
            return False
    
    def disconnect_from_hand(self):
        """Safely disconnect from the hand."""
        if self.api:
            try:
                print("Opening hand before disconnect...")
                self.api.perform_open()
                time.sleep(0.8)
                self.api.disconnect()
                print("Disconnected from the hand.")
            except Exception as e:
                print(f"Error during disconnect: {e}")
            finally:
                self.api = None
    
    def execute_motion_sequence(self, motion_sequence, sequence_name="motion", delay=0.8):
        """Execute a predefined motion sequence."""
        if not self.api:
            print("No connection to hand. Please connect first.")
            return False
        
        print(f"\nExecuting {sequence_name} sequence...")
        print("Press Ctrl+C to stop at any time")
        
        try:
            for i, position in enumerate(motion_sequence):
                print(f"Step {i + 1}/{len(motion_sequence)}: {position}")
                self.api.set_angle(position, 1)
                time.sleep(delay)
            
            print(f"{sequence_name} sequence completed!")
            return True
            
        except KeyboardInterrupt:
            print(f"\n{sequence_name} sequence interrupted!")
            return False
        except Exception as e:
            print(f"Error during {sequence_name} sequence: {e}")
            return False
    
    def demo_basic_motion(self):
        """Demonstrate basic finger movements."""
        print("\nDEMO: Basic Motion Sequence")
        print("="*50)
        print("This demo shows basic finger movements including:")
        print("- Opening all fingers")
        print("- Individual finger closures")
        print("- Full hand closure")
        print(f"Using port: {self.port}")
        
        if not self.api:
            if not self.connect_to_hand():
                return
        
        self.execute_motion_sequence(BASIC_MOTION, "Basic Motion")
    
    def demo_precision_grip(self):
        """Demonstrate precision grip patterns."""
        print("\nDEMO: Precision Grip")
        print("="*50)
        print("This demo shows precision grip movements:")
        print("- Thumb and index finger coordination")
        print("- Fine motor control")
        print("- Grip strength variation")
        print(f"Using port: {self.port}")
        
        if not self.api:
            if not self.connect_to_hand():
                return
        
        self.execute_motion_sequence(PRECISION_GRIP, "Precision Grip", delay=1.2)
    
    def demo_power_grip(self):
        """Demonstrate power grip patterns."""
        print("\nDEMO: Power Grip")
        print("="*50)
        print("This demo shows power grip movements:")
        print("- All fingers coordinated closure")
        print("- Strong grip patterns")
        print("- Grip strength control")
        print(f"Using port: {self.port}")
        
        if not self.api:
            if not self.connect_to_hand():
                return
        
        self.execute_motion_sequence(POWER_GRIP, "Power Grip", delay=1.0)
    
    def demo_finger_wave(self):
        """Demonstrate individual finger control."""
        print("\nDEMO: Finger Wave")
        print("="*50)
        print("This demo shows individual finger control:")
        print("- Sequential finger movements")
        print("- Independent finger control")
        print("- Coordination patterns")
        print(f"Using port: {self.port}")
        
        if not self.api:
            if not self.connect_to_hand():
                return
        
        self.execute_motion_sequence(FINGER_WAVE, "Finger Wave", delay=0.6)
    
    def demo_custom_motion(self):
        """Allow user to create custom motions."""
        print("\nDEMO: Custom Motion")
        print("="*50)
        print("Create your own motion sequence!")
        print("Enter finger positions (0-1000) for each finger:")
        print("Order: [Pinky, Ring, Middle, Index, Thumb, Extra]")
        print(f"Using port: {self.port}")
        
        if not self.api:
            if not self.connect_to_hand():
                return
        
        custom_sequence = []
        
        try:
            while True:
                print(f"\nStep {len(custom_sequence) + 1} (or 'done' to execute, 'quit' to cancel):")
                
                user_input = input("Enter 6 values (0-1000) separated by spaces: ").strip()
                
                if user_input.lower() == 'done':
                    if custom_sequence:
                        break
                    else:
                        print("No steps added yet. Add at least one step.")
                        continue
                elif user_input.lower() == 'quit':
                    print("Custom motion cancelled.")
                    return
                
                try:
                    values = [int(x) for x in user_input.split()]
                    if len(values) != 6:
                        print("Please enter exactly 6 values.")
                        continue
                    
                    if not all(0 <= v <= 1000 for v in values):
                        print("All values must be between 0 and 1000.")
                        continue
                    
                    position = np.array(values, dtype=np.int32)
                    custom_sequence.append(position)
                    print(f"Added step {len(custom_sequence)}: {position}")
                    
                except ValueError:
                    print("Invalid input. Please enter numbers only.")
                    continue
            
            # Execute the custom sequence
            custom_motion = np.array(custom_sequence)
            self.execute_motion_sequence(custom_motion, "Custom Motion", delay=1.0)
            
        except KeyboardInterrupt:
            print("\nCustom motion creation cancelled.")
    
    def demo_continuous_motion(self):
        """Demonstrate continuous motion patterns."""
        print("\nDEMO: Continuous Motion")
        print("="*50)
        print("This demo runs continuous motion patterns.")
        print("Press Ctrl+C to stop the demo.")
        print(f"Using port: {self.port}")
        
        if not self.api:
            if not self.connect_to_hand():
                return
        
        motions = [
            ("Basic Motion", BASIC_MOTION),
            ("Precision Grip", PRECISION_GRIP),
            ("Power Grip", POWER_GRIP),
            ("Finger Wave", FINGER_WAVE),
        ]
        
        try:
            cycle_count = 0
            while True:
                cycle_count += 1
                print(f"\n--- Cycle {cycle_count} ---")
                
                for motion_name, motion_sequence in motions:
                    print(f"Executing {motion_name}...")
                    for i, position in enumerate(motion_sequence):
                        print(f"  Step {i + 1}/{len(motion_sequence)}")
                        self.api.set_angle(position, 1)
                        time.sleep(0.8)
                    
                    time.sleep(1.0)  # Pause between motion types
                
                print("Cycle completed. Starting next cycle...")
                time.sleep(2.0)
                
        except KeyboardInterrupt:
            print("\nContinuous motion demo stopped.")
    
    def demo_connection_test(self):
        """Test connection reliability and basic functionality."""
        print("\nDEMO: Connection Test")
        print("="*50)
        print("This demo tests the connection and basic functionality:")
        print("- Connection establishment")
        print("- Basic command execution")
        print("- Error handling")
        print("- Disconnection")
        print(f"Using port: {self.port}")
        
        # Test connection
        if not self.connect_to_hand():
            print("Connection test failed!")
            return
        
        try:
            # Test basic commands
            print("\nTesting basic commands...")
            
            print("1. Reset error...")
            self.api.reset_error()
            time.sleep(0.1)
            
            print("2. Open hand...")
            self.api.perform_open()
            time.sleep(1.0)
            
            print("3. Close hand...")
            close_position = np.array([0, 0, 0, 0, 800, 1000], dtype=np.int32)
            self.api.set_angle(close_position, 1)
            time.sleep(1.0)
            
            print("4. Open hand again...")
            self.api.perform_open()
            time.sleep(1.0)
            
            print("5. Test individual finger control...")
            for finger in range(5):
                position = np.array([1000, 1000, 1000, 1000, 1000, 1000], dtype=np.int32)
                position[finger] = 0
                print(f"   Closing finger {finger + 1}...")
                self.api.set_angle(position, 1)
                time.sleep(0.5)
            
            print("6. Final open...")
            self.api.perform_open()
            time.sleep(1.0)
            
            print("\nConnection test completed successfully!")
            
        except Exception as e:
            print(f"Connection test failed: {e}")
        
        finally:
            self.disconnect_from_hand()


async def interactive_demo():
    """Interactive demonstration menu."""
    demo = SerialDemo()
    
    print("INSPIRE HAND SERIAL COMMUNICATION DEMO")
    print("=" * 60)
    print("This demo showcases various motions via serial communication.")
    print("Ensure your Inspire Hand is properly connected via serial port.")
    print()
    
    # Select COM port at the beginning
    print("First, let's configure your connection settings...")
    demo.port = demo.select_port()
    if demo.port is None:
        print("No port selected. Exiting demo.")
        return
    
    print(f"\nCOM port {demo.port} selected and will be used for all demos.")
    print("You can change settings later using option 8 in the menu.")
    
    while True:
        print("\nSelect a demo scenario:")
        print("1. Connection Test (verify basic functionality)")
        print("2. Basic Motion Sequence (finger movements)")
        print("3. Precision Grip Demo (thumb-finger coordination)")
        print("4. Power Grip Demo (full hand gripping)")
        print("5. Finger Wave Demo (individual finger control)")
        print("6. Custom Motion (create your own sequence)")
        print("7. Continuous Motion (run all patterns continuously)")
        print("8. Configure Connection Settings")
        print("9. Exit")
        
        try:
            choice = input("\nEnter your choice (1-9): ").strip()
            
            if choice == "1":
                await asyncio.sleep(0)  # Make it async-compatible
                demo.demo_connection_test()
            elif choice == "2":
                await asyncio.sleep(0)
                demo.demo_basic_motion()
            elif choice == "3":
                await asyncio.sleep(0)
                demo.demo_precision_grip()
            elif choice == "4":
                await asyncio.sleep(0)
                demo.demo_power_grip()
            elif choice == "5":
                await asyncio.sleep(0)
                demo.demo_finger_wave()
            elif choice == "6":
                await asyncio.sleep(0)
                demo.demo_custom_motion()
            elif choice == "7":
                await asyncio.sleep(0)
                demo.demo_continuous_motion()
            elif choice == "8":
                await asyncio.sleep(0)
                configure_connection_settings(demo)
            elif choice == "9":
                print("Exiting demo...")
                break
            else:
                print("Invalid choice. Please select 1-9.")
                
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


def configure_connection_settings(demo):
    """Allow user to configure connection settings."""
    print("\nCONNECTION SETTINGS")
    print("="*50)
    print(f"Current settings:")
    print(f"  Port: {demo.port if demo.port else 'Not selected'}")
    print(f"  Baudrate: {demo.baudrate}")
    print(f"  Generation: {demo.generation}")
    
    while True:
        print("\nWhat would you like to configure?")
        print("1. Select Port")
        print("2. Change Baudrate")
        print("3. Change Generation")
        print("4. Test Current Settings")
        print("5. Back to Main Menu")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            new_port = demo.select_port()
            if new_port:
                demo.port = new_port
                print(f"Port changed to {demo.port}")
                # Disconnect current connection if active
                if demo.api:
                    demo.disconnect_from_hand()
        elif choice == "2":
            try:
                new_baudrate = int(input(f"Enter new baudrate (current: {demo.baudrate}): "))
                demo.baudrate = new_baudrate
                print(f"Baudrate set to {demo.baudrate}")
                # Disconnect current connection if active to apply new settings
                if demo.api:
                    print("Disconnecting to apply new baudrate settings...")
                    demo.disconnect_from_hand()
            except ValueError:
                print("Invalid baudrate. Please enter a number.")
        elif choice == "3":
            try:
                new_gen = int(input(f"Enter generation (current: {demo.generation}): "))
                if new_gen in [3, 4]:
                    demo.generation = new_gen
                    print(f"Generation set to {demo.generation}")
                    # Disconnect current connection if active to apply new settings
                    if demo.api:
                        print("Disconnecting to apply new generation settings...")
                        demo.disconnect_from_hand()
                else:
                    print("Invalid generation. Please enter 3 or 4.")
            except ValueError:
                print("Invalid generation. Please enter a number.")
        elif choice == "4":
            if demo.port:
                print("Testing connection with current settings...")
                if demo.connect_to_hand(demo.port):
                    print("Connection test successful!")
                    demo.disconnect_from_hand()
                else:
                    print("Connection test failed!")
            else:
                print("No port selected. Please select a port first.")
        elif choice == "5":
            break
        else:
            print("Invalid choice. Please select 1-5.")


def print_demo_concepts():
    """Print educational content about this demo."""
    print("\nSERIAL 485 CONCEPTS")
    print("=" * 60)
    print("""
KEY CONFIGURATION SETTINGS:

1. HAND GENERATIONS
   • Different hardware versions (Gen 3, Gen 4)
   • Each may have different command sets
   • Proper generation selection is crucial

MOTION CONTROL:

• Position values: 0 (closed) to 1000 (open)
• 6-DOF control: [Pinky, Ring, Middle, Index, Thumb, Extra]
• Real-time updates with minimal latency
• Safety features and error handling

PRACTICAL APPLICATIONS:

• Research and development
• Prosthetic device control
• Robotic manipulation tasks
• Human-machine interface studies
""")


async def main():
    """Main demo entry point."""
    print_demo_concepts()
    
    print("\nReady to run interactive demos?")
    response = input("Press Enter to start, or 'q' to quit: ").strip().lower()
    
    if response != 'q':
        await interactive_demo()
    else:
        print("See you next time!")


if __name__ == "__main__":
    print("Inspire Hand Serial Communication Demo")
    print("Configure your COM port settings in the demo menu!")
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
    except Exception as e:
        print(f"\nDemo failed: {e}")
        traceback.print_exc()
