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
    # Create the recordings directory if it doesn't exist
    recording_path = Path("./recordings") / session_dir
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

        print("=== Collecting Tactile Data for 5 Seconds ===")
        import time

        # Define collection duration
        duration = 5  # seconds
        start_time = time.time()
        collection_count = 0
        tactile_data: TactileData | None = None

        # Collect data for the specified duration
        while time.time() - start_time < duration:
            # Get all tactile data using the TactileData class
            tactile_data = hand.get_all_tactile_data()

            # Save data to JSONL file
            save_tactile_data_to_jsonl(tactile_data, session_dir)
            collection_count += 1

            # Small delay to prevent overwhelming the system
            time.sleep(0.01)

        end_time = time.time()
        actual_duration = end_time - start_time

        print(f"\n=== Data Collection Complete ===")
        print(f"Collection duration: {actual_duration:.2f} seconds")
        print(f"Samples collected: {collection_count}")
        print(f"Average sampling rate: {collection_count/actual_duration:.2f} Hz")
        print(f"Data saved to: ./recordings/{session_dir}/tactile_data.jsonl")

        if tactile_data is None:
            print("No tactile data collected.")
            return

        # Display the most recent data
        print("\n=== Most Recent Tactile Data ===")
        print(f"Timestamp: {tactile_data.timestamp}")

        # Print summary of sensor data
        print("\n=== Sensor Data Summary ===")
        # Access finger sensors using the structured data class
        fingers = [
            ("Pinky", tactile_data.pinky),
            ("Ring", tactile_data.ring),
            ("Middle", tactile_data.middle),
            ("Index", tactile_data.index),
            ("Thumb", tactile_data.thumb),
        ]

        for name, finger_data in fingers:
            if name == "Thumb":
                positions = ["top", "tip", "mid", "base"]
            else:
                positions = ["top", "tip", "base"]

            print(f"  {name} finger:")
            for position in positions:
                sensor_data = getattr(finger_data, position)
                if sensor_data.size > 0:
                    mean_val = np.mean(sensor_data)
                    max_val = np.max(sensor_data)
                    print(f"    {position}: avg={mean_val:.2f}, max={max_val:.2f}")

        # Palm analysis
        if tactile_data.palm.size > 0:
            palm_mean = np.mean(tactile_data.palm)
            palm_max = np.max(tactile_data.palm)
            print(f"  Palm: avg={palm_mean:.2f}, max={palm_max:.2f}")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        # Clean up
        hand.disconnect()
        print("\nDisconnected from device")

if __name__ == "__main__":
    main()
