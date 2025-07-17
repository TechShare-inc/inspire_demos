#!/usr/bin/env python3
"""
Comparison demo showing InspireHandSerial and InspireHandModbus usage
"""

import numpy as np
import time
from inspire_demos.inspire_modbus import InspireHandModbus
from inspire_demos.inspire_serial import InspireHandSerial

def demo_serial_interface():
    """Demo using Serial interface"""
    print("=== InspireHandSerial Demo ===")
    
    # Initialize Serial connection
    hand = InspireHandSerial(port="COM3", baudrate=115200, generation=3, debug=True)
    
    if not hand.connect():
        print("Failed to connect via Serial. Please check COM port.")
        return
    
    try:
        # Set speeds and forces
        speeds = np.array([800, 800, 800, 800, 800, 800], dtype=np.int32)
        forces = np.array([400, 400, 400, 400, 400, 400], dtype=np.int32)
        
        hand.set_speed(speeds)
        hand.set_force(forces)
        
        # Perform open/close cycle
        print("Performing open...")
        hand.perform_open()
        time.sleep(3)
        
        actual = hand.get_angle_actual()
        print(f"Open position: {actual}")
        
        print("Performing close...")
        hand.perform_close()
        time.sleep(3)
        
        actual = hand.get_angle_actual()
        print(f"Close position: {actual}")
        
    except Exception as e:
        print(f"Serial demo error: {e}")
    finally:
        hand.disconnect()

def demo_modbus_interface():
    """Demo using Modbus interface"""
    print("\n=== InspireHandModbus Demo ===")
    
    # Initialize Modbus connection
    hand = InspireHandModbus(ip="192.168.11.210", port=6000, generation=3, debug=True)
    
    if not hand.connect():
        print("Failed to connect via Modbus. Please check IP address.")
        return
    
    try:
        # Set speeds and forces (same as serial)
        speeds = np.array([800, 800, 800, 800, 800, 800], dtype=np.int32)
        forces = np.array([400, 400, 400, 400, 400, 400], dtype=np.int32)
        
        hand.set_speed(speeds)
        hand.set_force(forces)
        
        # Perform open/close cycle
        print("Performing open...")
        hand.perform_open()
        time.sleep(3)
        
        actual = hand.get_angle_actual()
        print(f"Open position: {actual}")
        
        print("Performing close...")
        hand.perform_close()
        time.sleep(3)
        
        actual = hand.get_angle_actual()
        print(f"Close position: {actual}")
        
    except Exception as e:
        print(f"Modbus demo error: {e}")
    finally:
        hand.disconnect()

def compare_interfaces():
    """Compare common methods between interfaces"""
    print("\n=== Interface Comparison ===")
    
    # Create both instances
    serial_hand = InspireHandSerial(generation=3, debug=False)
    modbus_hand = InspireHandModbus(generation=3, debug=False)
    
    # Compare available methods
    serial_methods = [method for method in dir(serial_hand) if not method.startswith('_')]
    modbus_methods = [method for method in dir(modbus_hand) if not method.startswith('_')]
    
    common_methods = set(serial_methods) & set(modbus_methods)
    serial_only = set(serial_methods) - set(modbus_methods)
    modbus_only = set(modbus_methods) - set(serial_methods)
    
    print(f"Common methods ({len(common_methods)}):")
    for method in sorted(common_methods):
        print(f"  • {method}")
    
    if serial_only:
        print(f"\nSerial-only methods ({len(serial_only)}):")
        for method in sorted(serial_only):
            print(f"  • {method}")
    
    if modbus_only:
        print(f"\nModbus-only methods ({len(modbus_only)}):")
        for method in sorted(modbus_only):
            print(f"  • {method}")

def main():
    print("Inspire Hand Interface Comparison Demo")
    print("=====================================")
    
    # Show interface comparison
    compare_interfaces()
    
    # Note: Uncomment the lines below to test actual hardware connections
    # demo_serial_interface()
    demo_modbus_interface()
    
    print("\nDemo completed. Uncomment hardware demo calls to test with actual devices.")

if __name__ == "__main__":
    main()
