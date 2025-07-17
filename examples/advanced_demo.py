"""
Advanced demonstration of the Inspire Hand API

This example shows how to:
- Read sensor data (angles, forces, temperature)
- Implement custom motion sequences
- Handle errors gracefully
- Use multiple control modes
"""

import time
import logging
from typing import List
from inspire_demos import InspireHandSerial


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def demonstrate_sensor_reading(api: InspireHandSerial, hand_id: int = 1):
    """Demonstrate reading various sensor values from the hand"""
    logger.info("Reading sensor data...")
    
    # Read current angles
    angles = api.getangleact(hand_id)
    if angles:
        logger.info(f"Current angles: {angles}")
    
    # Read current forces
    forces = api.getforceact(hand_id)
    if forces:
        logger.info(f"Current forces: {forces}")
    
    # Read temperature
    temperatures = api.gettemp(hand_id)
    if temperatures:
        logger.info(f"Temperatures: {temperatures}")
    
    # Check for errors
    errors = api.geterror(hand_id)
    if errors and any(error != 0 for error in errors):
        logger.warning(f"Errors detected: {errors}")
    else:
        logger.info("No errors detected")


def custom_gesture_sequence(api: InspireHandSerial):
    """Perform a custom gesture sequence"""
    logger.info("Starting custom gesture sequence...")
    
    gestures = [
        ("Point", [0, 1000, 1000, 1000, 1000, 1000]),
        ("Peace", [0, 0, 1000, 1000, 1000, 1000]),
        ("Thumbs up", [1000, 1000, 1000, 1000, 1000, 0]),
        ("Fist", [0, 0, 0, 0, 0, 1000]),
        ("Open", [1000, 1000, 1000, 1000, 1000, 1000]),
    ]
    
    for gesture_name, angles in gestures:
        logger.info(f"Performing gesture: {gesture_name}")
        api.set_angle(angles)
        time.sleep(1.5)  # Hold gesture for 1.5 seconds
        
        # Read actual angles to verify position
        actual_angles = api.getangleact()
        if actual_angles:
            logger.info(f"Target: {angles}, Actual: {actual_angles}")


def speed_control_demo(api: InspireHandSerial):
    """Demonstrate speed control"""
    logger.info("Demonstrating speed control...")
    
    # Set slower speeds
    slow_speeds = [200, 200, 200, 200, 200, 200]
    api.set_speed(1, slow_speeds)
    logger.info("Set slow speed for smooth motion")
    
    # Perform motion
    api.set_angle([0, 0, 0, 0, 0, 0])
    time.sleep(3)
    api.set_angle([1000, 1000, 1000, 1000, 1000, 1000])
    time.sleep(3)
    
    # Set faster speeds
    fast_speeds = [800, 800, 800, 800, 800, 800]
    api.set_speed(1, fast_speeds)
    logger.info("Set fast speed for quick motion")
    
    # Perform motion
    api.set_angle([0, 0, 0, 0, 0, 0])
    time.sleep(1)
    api.set_angle([1000, 1000, 1000, 1000, 1000, 1000])
    time.sleep(1)


def main(port: str = "COM7", baudrate: int = 115200):
    """Main demonstration function"""
    logger.info(f"Connecting to Inspire Hand on {port} at {baudrate} baud")
    
    api = InspireHandSerial(port, baudrate)
    
    try:
        # Connect to the hand
        if not api.connect():
            logger.error("Failed to connect to the hand")
            return
        
        logger.info("Connected successfully!")
        
        # Reset any errors and initialize
        api.reset_error()
        time.sleep(0.1)
        
        # Open hand to start
        api.perform_open()
        time.sleep(1)
        
        # Demonstrate sensor reading
        demonstrate_sensor_reading(api)
        
        # Demonstrate custom gestures
        custom_gesture_sequence(api)
        
        # Demonstrate speed control
        speed_control_demo(api)
        
        # Return to open position
        api.perform_open()
        time.sleep(1)
        
        logger.info("Demo completed successfully!")
        
    except KeyboardInterrupt:
        logger.info("Demo interrupted by user")
        api.perform_open()  # Safe position
        time.sleep(0.5)
    except Exception as e:
        logger.error(f"Error during demo: {e}")
        api.perform_open()  # Safe position
        time.sleep(0.5)
    finally:
        api.disconnect()
        logger.info("Disconnected from the hand")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Advanced Inspire Hand demo")
    parser.add_argument("--port", default="COM7", help="Serial port (default: COM7)")
    parser.add_argument("--baudrate", type=int, default=115200, help="Baud rate (default: 115200)")
    
    args = parser.parse_args()
    main(args.port, args.baudrate)
