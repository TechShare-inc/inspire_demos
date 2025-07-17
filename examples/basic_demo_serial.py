import time
import serial.tools.list_ports
import numpy as np
from inspire_demos import InspireHandSerial


motion = np.array([
    [1000, 1000, 1000, 1000, 1000, 1000],
    [1000, 1000, 1000, 1000, 1000, 0],
    [1000, 1000, 1000, 1000, 1000, 1000],
    [1000, 1000, 1000, 1000, 200, 1000],
    [1000, 1000, 1000, 0, 200, 1000],
    [1000, 1000, 0, 0, 200, 1000],
    [1000, 0, 0, 0, 200, 1000],
    [0, 0, 0, 0, 200, 1000],
])


def list_serial_ports():
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


def select_port():
    """Allow user to select a serial port from available options."""
    available_ports = list_serial_ports()
    
    if not available_ports:
        print("No serial ports available. Please check your connections.")
        return None
    
    while True:
        try:
            choice = input(f"Select a port (1-{len(available_ports)}) or 'q' to quit: ").strip()
            
            if choice.lower() == 'q':
                print("Exiting...")
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
            print("\nExiting...")
            return None


def main(port: str = None, baudrate: int = 115200):
    """
    Main function to control the Inspire Hand.
    
    Args:
        port: Serial port to connect to. If None, user will be prompted to select.
        baudrate: Communication baudrate (default: 115200)
    """
    # If no port is specified, let the user select one
    if port is None:
        port = select_port()
        if port is None:
            return  # User cancelled or no ports available
    
    print(f"Connecting to {port} at {baudrate} baud...")
    
    try:
        api = InspireHandSerial(port, baudrate, generation=4)
        api.connect()
        print(f"Successfully connected to the Gen 4 hand!")

        api.reset_error()
        time.sleep(0.1)
        api.perform_open()
        time.sleep(0.8)

        try:
            print("Starting motion sequence... (Press Ctrl+C to stop)")
            while True:
                for i in range(len(motion)):
                    print(f"Executing motion step {i + 1}/{len(motion)}")
                    api.set_angle(motion[i], 1)
                    time.sleep(0.8)
        except KeyboardInterrupt:
            api.perform_open()
            time.sleep(0.8)
            print("Keyboard interrupt. Exiting...")
        finally:
            api.disconnect()
            print("Disconnected from the hand.")
            
    except Exception as e:
        print(f"Error connecting to or controlling the hand: {e}")
        print("Please check your connection and try again.")


if __name__ == "__main__":
    # You can still specify a port directly, or let the user choose
    main()  # Let user select port
    # main(port="COM7", baudrate=115200)  # Or specify port directly
