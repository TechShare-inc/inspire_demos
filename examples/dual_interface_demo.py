#!/usr/bin/env python3
"""
Dual Interface Communication Demo
- Send commands via Serial (reliable)
- Read tactile data via Modbus (Gen 4 feature)
- Demonstrates simultaneous communication methods
"""

import asyncio
import numpy as np
from inspire_demos.inspire_modbus import InspireHandModbus
from inspire_demos.inspire_serial import InspireHandSerial

async def main():
    print("=== Simple Control + Monitor Demo ===")
    
    # Setup: Serial for control, Modbus for monitoring
    serial_hand = InspireHandSerial(port="COM3", generation=4)  # Control
    modbus_hand = InspireHandModbus(ip="192.168.11.210", generation=4)  # Monitor
    
    # Connect
    print("Connecting...")
    loop = asyncio.get_event_loop()
    
    serial_ok = await loop.run_in_executor(None, serial_hand.connect)
    modbus_ok = await loop.run_in_executor(None, modbus_hand.connect)
    
    print(f"Serial (control): {'✓' if serial_ok else '✗'}")
    print(f"Modbus (monitor): {'✓' if modbus_ok else '✗'}")
    
    if not (serial_ok or modbus_ok):
        print("No connections! Check settings and try again.")
        return
    
    # Demo: Control via Serial, Monitor via Modbus
    movements = [
        [0, 0, 0, 0, 200, 1000],      # Open
        [1000, 1000, 1000, 1000, 1000, 1000],  # Close
        [0, 0, 0, 0, 200, 1000],      # Open again
    ]
    
    print("\n=== Starting continuous dual-interface demo ===")
    print("Press Ctrl+C to stop the loop")
    
    cycle_count = 0
    
    try:
        while True:
            cycle_count += 1
            print(f"\n🔄 === CYCLE {cycle_count} ===")
            
            for i, angles in enumerate(movements):
                print(f"\n--- Step {i+1}: Moving to {angles} ---")
                
                # Send command via Serial
                if serial_ok:
                    angles_array = np.array(angles, dtype=np.int32)
                    await loop.run_in_executor(None, serial_hand.set_angle, angles_array)
                    print("→ Command sent via Serial")
                
                # Wait for movement
                await asyncio.sleep(2)
                
                # Read position via Modbus
                if modbus_ok:
                    try:
                        position = await loop.run_in_executor(None, modbus_hand.get_angle_actual)
                        print(f"← Position from Modbus: {position.tolist()}")
                        
                        # Read tactile data
                        tactile = await loop.run_in_executor(None, modbus_hand.get_tactile_data)
                        if tactile:
                            print(f"← Tactile sensors: {len(tactile)} active")
                            # Example: Print palm sensor data shape and sample values
                            if 'palm' in tactile:
                                palm_shape = tactile['palm'].shape
                                palm_mean = tactile['palm'].mean()
                                palm_max = tactile['palm'].max()
                                print(f"← Palm sensor: {palm_shape[0]}x{palm_shape[1]} matrix | Mean: {palm_mean:.1f} | Max: {palm_max}")
                        
                    except Exception as e:
                        print(f"← Monitor error: {e}")
            
            # Brief pause between cycles
            print(f"--- End of cycle {cycle_count}, pausing... ---")
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        print(f"\n\n⏹️ Demo stopped by user after {cycle_count} cycles")
    except Exception as e:
        print(f"\n\n❌ Demo stopped due to error: {e}")
    
    # Cleanup
    print("\nDisconnecting...")
    if serial_ok:
        await loop.run_in_executor(None, serial_hand.disconnect)
    if modbus_ok:
        await loop.run_in_executor(None, modbus_hand.disconnect)
    
    print("Done!")

if __name__ == "__main__":
    # Note: Adjust COM port and IP address for your setup
    print("Make sure to set correct COM port and IP address in the code!")
    asyncio.run(main())
