#!/usr/bin/env python3
"""
Demo script showing usage of InspireHandModbus class for Gen 4 hardware
Includes comprehensive testing of tactile sensor functionality
"""

import numpy as np
import time
import sys
from loguru import logger
from inspire_demos.inspire_modbus import InspireHandModbus

def main():
    # Test Gen 4 hardware with Modbus support
    logger.info("="*50)
    logger.info("Testing Gen 4 (Modbus TCP with tactile sensors)")
    logger.info("="*50)
    
    # Initialize Modbus connection
    logger.info("Initializing Inspire Hand Modbus connection for Gen 4...")
    hand = InspireHandModbus(ip="192.168.11.210", port=6000, generation=4, debug=True)
    
    # Connect to the hand
    if not hand.connect():
        logger.error("Failed to connect to Gen 4 hardware. Please check IP address and network connection.")
        return
    
    try:
        logger.info("Connected to Gen 4 hardware")
        
        # Test basic functionality
        logger.info("Testing basic functionality...")
        
        # Set movement speed
        logger.info("Setting movement speeds...")
        speeds = np.array([1000, 1000, 1000, 1000, 1000, 1000], dtype=np.int32)
        hand.set_speed(speeds)
        time.sleep(1)
        
        # Set force parameters
        logger.info("Setting force parameters...")
        forces = np.array([500, 500, 500, 500, 500, 500], dtype=np.int32)
        hand.set_force(forces)
        time.sleep(1)
        
        # Read actual position
        actual_angles = hand.get_angle_actual()
        logger.info(f"Actual angles: {actual_angles}")
        
        # Check error status
        errors = hand.get_error()
        logger.info(f"Error codes: {errors}")
        
        # Check temperature
        temps = hand.get_temp()
        logger.info(f"Temperatures: {temps}")
        
        # Verify tactile sensors are available
        logger.info("Gen 4 hardware detected - verifying tactile sensors...")
        try:
            tactile_data = hand.get_tactile_data()
            logger.info(f"✓ Tactile sensors accessible: {len(tactile_data)} sensors detected")
        except Exception as e:
            logger.error(f"✗ Tactile sensor check failed: {e}")
        
        # Validate register addresses
        logger.info("Validating register addresses...")
        validation_results = hand.validate_register_addresses()
        successful_validations = sum(validation_results.values())
        total_validations = len(validation_results)
        logger.info(f"Register validation: {successful_validations}/{total_validations} successful")
        
    except Exception as e:
        logger.error(f"Error during operation: {e}")
    
    finally:
        # Disconnect
        logger.info("Disconnecting from Gen 4 hardware...")
        hand.disconnect()
    
    logger.info("\n" + "="*50)
    logger.info("Basic demo completed.")
    
    # Now run continuous tactile sensor testing for Gen 4
    logger.info("\n" + "="*60)
    logger.info("STARTING CONTINUOUS TACTILE SENSOR TESTING")
    logger.info("Press Ctrl+C to stop the tactile sensor loop")
    logger.info("="*60)
    
    test_tactile_continuous()

def demo_basic_movement(hand):
    """Demo basic hand movement for Gen 4 hardware"""
    logger.info("Demonstrating basic hand movements...")
    
    # Move to initial position
    logger.info("Moving to initial position...")
    angles = np.array([0, 0, 0, 0, 400, 0], dtype=np.int32)
    hand.set_angle(angles)
    time.sleep(3)
    
    # Read actual position
    actual_angles = hand.get_angle_actual()
    logger.info(f"Actual angles: {actual_angles}")
    
    # Move to grasp position
    logger.info("Moving to grasp position...")
    angles = np.array([1000, 1000, 1000, 1000, 1000, 0], dtype=np.int32)
    hand.set_angle(angles)
    time.sleep(3)
    
    # Read actual position again
    actual_angles = hand.get_angle_actual()
    logger.info(f"Actual angles: {actual_angles}")
    
    # Demo action sequence
    logger.info("Setting action sequence 2...")
    hand.set_action_sequence(2)
    time.sleep(1)
    
    logger.info("Running action sequence...")
    hand.run_action_sequence()
    time.sleep(3)

def test_tactile_continuous():
    """Continuous tactile sensor testing with keyboard interrupt handling"""
    # Connect to Gen 4 hardware
    hand = InspireHandModbus(ip="192.168.11.210", port=6000, generation=4, debug=True)
    
    if not hand.connect():
        logger.error("Failed to connect to Gen 4 hardware. Please check connection.")
        return
    
    try:
        logger.info("Starting continuous tactile sensor monitoring...")
        logger.info("Data will be refreshed every 2 seconds")
        logger.info("Press Ctrl+C to stop\n")
        
        loop_count = 0
        
        while True:
            try:
                loop_count += 1
                logger.info(f"--- Tactile Data Reading #{loop_count} ---")
                
                # Get all tactile data
                tactile_data = hand.get_tactile_data()
                
                # Display summary for each sensor
                for sensor_name, data in tactile_data.items():
                    rows, cols = data.shape
                    data_min, data_max = data.min(), data.max()
                    data_mean = data.mean()
                    
                    logger.info(f"  {sensor_name:15} | Shape: {rows:2}x{cols:2} | "
                               f"Range: [{data_min:4}, {data_max:4}] | Mean: {data_mean:6.1f}")
                
                # Show detailed data for key sensors every 5th loop
                if loop_count % 5 == 0:
                    logger.info("\n--- Detailed Data (every 5th reading) ---")
                    
                    # Palm sensor
                    palm_data = hand.get_tactile_sensor_data('palm')
                    logger.info(f"Palm sensor (8x14):\n{palm_data}")
                    
                    # Thumb tip sensor
                    thumb_tip_data = hand.get_tactile_sensor_data('thumb_tip')
                    logger.info(f"Thumb tip sensor (12x8):\n{thumb_tip_data}")
                
                time.sleep(2)  # Wait 2 seconds before next reading
                
            except KeyboardInterrupt:
                logger.info("\nKeyboard interrupt received. Stopping tactile sensor loop...")
                break
            except Exception as e:
                logger.error(f"Error in tactile sensor loop: {e}")
                time.sleep(1)  # Brief pause before retrying
                
    except KeyboardInterrupt:
        logger.info("\nKeyboard interrupt received during setup. Stopping...")
    except Exception as e:
        logger.error(f"Tactile sensor continuous test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        hand.disconnect()
        logger.info("Disconnected from hardware. Tactile sensor testing completed.")

def test_tactile_only():
    """Simple test function focused only on tactile sensor functionality - single run"""
    logger.info("="*60)
    logger.info("TACTILE SENSOR ONLY TEST (SINGLE RUN)")
    logger.info("="*60)
    
    # Connect to Gen 4 hardware
    hand = InspireHandModbus(ip="192.168.11.210", port=6000, generation=4, debug=True)
    
    if not hand.connect():
        logger.error("Failed to connect to Gen 4 hardware. Please check connection.")
        return
    
    try:
        logger.info("Testing tactile sensor data acquisition...")
        
        # Get all tactile data
        tactile_data = hand.get_tactile_data()
        
        logger.info(f"Successfully acquired data from {len(tactile_data)} sensors:")
        
        # Display summary for each sensor
        for sensor_name, data in tactile_data.items():
            rows, cols = data.shape
            data_min, data_max = data.min(), data.max()
            data_mean = data.mean()
            
            logger.info(f"  {sensor_name:15} | Shape: {rows:2}x{cols:2} | "
                       f"Range: [{data_min:4}, {data_max:4}] | Mean: {data_mean:6.1f}")
        
        # Test specific sensors with detailed output
        logger.info("\nDetailed sensor data:")
        
        # Test palm (largest sensor)
        palm_data = hand.get_tactile_sensor_data('palm')
        logger.info(f"\nPalm sensor (8x14 matrix):")
        logger.info(f"{palm_data}")
        
        # Test a finger tip sensor
        thumb_tip_data = hand.get_tactile_sensor_data('thumb_tip')
        logger.info(f"\nThumb tip sensor (12x8 matrix):")
        logger.info(f"{thumb_tip_data}")
        
        # Test a small sensor
        pinky_top_data = hand.get_tactile_sensor_data('pinky_top')
        logger.info(f"\nPinky top sensor (3x3 matrix):")
        logger.info(f"{pinky_top_data}")
        
        logger.info("\n✓ Tactile sensor test completed successfully!")
        
    except Exception as e:
        logger.error(f"Tactile sensor test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        hand.disconnect()
        logger.info("Disconnected from hardware.")

def test_tactile_loop():
    """Continuous tactile sensor testing - alternative entry point"""
    logger.info("="*60)
    logger.info("TACTILE SENSOR CONTINUOUS LOOP TEST")
    logger.info("="*60)
    
    test_tactile_continuous()

if __name__ == "__main__":
    # You can run different modes based on command line arguments
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--tactile-only":
            test_tactile_only()
        elif sys.argv[1] == "--tactile-loop":
            test_tactile_loop()
        elif sys.argv[1] == "--help":
            print("Usage:")
            print("  python modbus_demo.py              # Full Gen 4 demo with continuous tactile loop at end")
            print("  python modbus_demo.py --tactile-only    # Single tactile sensor test")
            print("  python modbus_demo.py --tactile-loop    # Continuous tactile sensor loop only")
            print("  python modbus_demo.py --help            # Show this help")
            print("\nNote: This demo is designed for Gen 4 hardware with Modbus TCP support only.")
        else:
            print(f"Unknown option: {sys.argv[1]}")
            print("Use --help to see available options")
    else:
        main()
