#!/usr/bin/env python3
"""
Example usage of the refactored tactile data methods using TactileData class.
Demonstrates the new structured approach with data classes.
"""

from inspire_demos.inspire_modbus import InspireHandModbus, TactileData
import numpy as np
import json
import os
from pathlib import Path
from datetime import datetime as date

def save_tactile_data_to_jsonl(tactile_data: TactileData, session_dir: str):
    """Save tactile data to JSONL format."""
    # Create the recording directory if it doesn't exist
    recording_path = Path("./recording") / session_dir
    recording_path.mkdir(parents=True, exist_ok=True)
    
    # Prepare the JSONL file path
    jsonl_file = recording_path / "tactile_data.jsonl"
    
    # Convert numpy arrays to lists for JSON serialization
    def convert_arrays_to_lists(data):
        if isinstance(data, np.ndarray):
            return data.tolist()
        elif hasattr(data, '__dict__'):
            return {key: convert_arrays_to_lists(value) for key, value in data.__dict__.items()}
        else:
            return data
    
    # Convert the tactile data to a JSON-serializable format
    json_data = convert_arrays_to_lists(tactile_data)
    
    # Append to JSONL file
    with open(jsonl_file, 'a', encoding='utf-8') as f:
        json.dump(json_data, f)
        f.write('\n')
    
    print(f"Tactile data saved to: {jsonl_file}")
    return jsonl_file

def main():
    # Create session directory based on current timestamp
    session_timestamp = date.now().strftime("%Y%m%d_%H%M%S")
    session_dir = f"session_{session_timestamp}"
    
    # Initialize the Modbus client for Gen 4 hardware
    hand = InspireHandModbus(ip="192.168.11.210", port=6000, generation=4, debug=True)
    
    try:
        # Connect to the device
        if not hand.connect():
            print("Failed to connect to the Inspire Hand")
            return
        
        print("=== New TactileData Class Structure ===")
        # Get all tactile data using the new TactileData class
        tactile_data: TactileData = hand.get_all_tactile_data()
        
        # Save data to JSONL file
        save_tactile_data_to_jsonl(tactile_data, session_dir)
        
        print(f"Timestamp: {tactile_data.timestamp}")
        print("Sensor data shapes:")
        
        # Access finger sensors using the structured data class
        print("Finger sensors:")
        fingers = [
            ("Pinky", tactile_data.pinky),
            ("Ring", tactile_data.ring), 
            ("Middle", tactile_data.middle),
            ("Index", tactile_data.index)
        ]
        
        for name, finger_data in fingers:
            print(f"  {name}:")
            print(f"    Top: {finger_data.top.shape}")
            print(f"    Tip: {finger_data.tip.shape}")
            print(f"    Base: {finger_data.base.shape}")
        
        # Thumb has an additional 'mid' sensor
        print("  Thumb:")
        print(f"    Top: {tactile_data.thumb.top.shape}")
        print(f"    Tip: {tactile_data.thumb.tip.shape}")
        print(f"    Mid: {tactile_data.thumb.mid.shape}")
        print(f"    Base: {tactile_data.thumb.base.shape}")
        
        # Palm is a direct array
        print(f"  Palm: {tactile_data.palm.shape}")
        
        print("\n=== Individual Sensor Access (New Method) ===")
        # Access individual sensors using the new get_tactile_data method
        try:
            pinky_top = hand.get_tactile_data("pinky", "top")
            print(f"Pinky top sensor shape: {pinky_top.shape}")
            
            thumb_mid = hand.get_tactile_data("thumb", "mid")
            print(f"Thumb mid sensor shape: {thumb_mid.shape}")
            
            palm = hand.get_tactile_data("palm")
            print(f"Palm sensor shape: {palm.shape}")
        except ValueError as e:
            print(f"Error accessing sensor: {e}")
        
        print("\n=== Data Analysis Example ===")
        # Example of analyzing the data using the structured approach
        pinky_top_data = tactile_data.pinky.top
        if pinky_top_data.size > 0:
            max_pressure = np.max(pinky_top_data)
            min_pressure = np.min(pinky_top_data)
            mean_pressure = np.mean(pinky_top_data)
            
            print(f"Pinky top sensor analysis:")
            print(f"  Max pressure: {max_pressure}")
            print(f"  Min pressure: {min_pressure}")
            print(f"  Mean pressure: {mean_pressure:.2f}")
            print(f"  Data shape: {pinky_top_data.shape}")
        
        print("\n=== Working with Multiple Sensors ===")
        # Example of iterating through all finger sensors
        all_fingers = [
            ("pinky", tactile_data.pinky),
            ("ring", tactile_data.ring),
            ("middle", tactile_data.middle),
            ("index", tactile_data.index)
        ]
        
        for finger_name, finger_data in all_fingers:
            positions = ["top", "tip", "base"]
            print(f"{finger_name.title()} finger pressure summary:")
            for position in positions:
                sensor_data = getattr(finger_data, position)
                if sensor_data.size > 0:
                    mean_val = np.mean(sensor_data)
                    print(f"  {position}: {mean_val:.2f} (avg)")
        
        # Special handling for thumb (has 'mid' sensor)
        print("Thumb finger pressure summary:")
        thumb_positions = ["top", "tip", "mid", "base"]
        for position in thumb_positions:
            sensor_data = getattr(tactile_data.thumb, position)
            if sensor_data.size > 0:
                mean_val = np.mean(sensor_data)
                print(f"  {position}: {mean_val:.2f} (avg)")
        
        # Palm analysis
        if tactile_data.palm.size > 0:
            palm_mean = np.mean(tactile_data.palm)
            print(f"Palm pressure summary: {palm_mean:.2f} (avg)")
        
        print("\n=== Timestamp Usage ===")
        print(f"Data collected at Unix timestamp: {tactile_data.timestamp}")
        import datetime
        dt = datetime.datetime.fromtimestamp(tactile_data.timestamp)
        print(f"Human readable time: {dt.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")
        
        print(f"\n=== Data Recording ===")
        print(f"Session directory: ./recording/{session_dir}")
        print("Data has been saved to tactile_data.jsonl")
        
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        # Clean up
        hand.disconnect()
        print("\nDisconnected from device")

if __name__ == "__main__":
    main()
