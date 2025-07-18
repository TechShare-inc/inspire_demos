# Inspire Hand Control Library

A Python library for controlling the Inspire Hand robotic hand via serial communication and Modbus TCP. This package provides a simple and intuitive API for connecting to and controlling the Inspire Hand through various motion commands and sensor readings.

## Features

- **Dual Communication Protocols**: Support for both Serial and Modbus TCP communication
- **Simple API**: Easy-to-use Python interface for hand control
- **Motion Control**: Set individual finger angles, perform predefined gestures
- **Sensor Reading**: Read current angles, forces, and temperature data
- **Error Handling**: Built-in error detection and recovery
- **Cross-Platform**: Works on Windows, Linux, and macOS
- **Configurable**: Customizable communication parameters
- **Multi-Generation Support**: Compatible with Gen3 and Gen4 Inspire Hands
- **Stress Testing**: Built-in stress testing and performance monitoring

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/TechShare-inc/inspire_demos.git
cd inspire_demos

# Install in development mode
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

### Using pip (when published)

```bash
pip install inspire-demos
```

## Quick Start

### Serial Communication

```python
from inspire_demos import InspireHandSerial
import time

# Create API instance for serial communication
api = InspireHandSerial(port="COM7", baudrate=115200)

# Connect to the hand
api.connect()

# Reset errors and open hand
api.reset_error()
api.perform_open()
time.sleep(1)

# Set custom finger angles (0-1000 range)
api.set_angle([500, 800, 600, 400, 200, 1000])
time.sleep(2)

# Perform predefined gestures
api.perform_close()  # Close hand
time.sleep(1)
api.perform_open()   # Open hand

# Disconnect
api.disconnect()
```

### Modbus TCP Communication

```python
from inspire_demos import InspireHandModbus
import time

# Create API instance for Modbus TCP communication
api = InspireHandModbus(ip="192.168.11.210", port=6000, generation=3)

# Connect to the hand
api.connect()

# Set custom finger angles (0-1000 range)
api.set_angle([500, 800, 600, 400, 200, 1000])
time.sleep(2)

# Read current angles
current_angles = api.getangleact()
print(f"Current angles: {current_angles}")

# Disconnect
api.disconnect()
```

## Examples

The `examples/` directory contains demonstration scripts:

- `basic_serial_demo.py`: Basic serial communication and motion sequence demonstration
- `modbus_demo.py`: Modbus TCP communication demonstration
- `dual_interface_demo.py`: Demonstrates using both serial and Modbus interfaces
- `stress_test_demo.py`: Performance testing and stress testing capabilities

### Running Examples

```bash
# Basic serial demo
python examples/basic_serial_demo.py

# Modbus demo
python examples/modbus_demo.py

# Dual interface demo
python examples/dual_interface_demo.py

# Stress test demo
python examples/stress_test_demo.py
```

## API Reference

### InspireHandSerial

Main class for controlling the Inspire Hand via serial communication.

#### Connection Methods
- `connect()`: Establish serial connection to the hand
- `disconnect()`: Close serial connection

#### Motion Control
- `set_angle(angles, hand_id=1)`: Set finger angles (list of 6 integers, 0-1000)
- `perform_open()`: Open all fingers
- `perform_close()`: Close all fingers
- `return_to_zero()`: Return to zero position
- `set_speed(hand_id, speeds)`: Set motion speeds
- `set_force(hand_id, forces)`: Set force limits

#### Sensor Reading
- `getangleact(hand_id=1)`: Get current finger angles
- `getforceact(hand_id=1)`: Get current forces
- `gettemp(hand_id=1)`: Get temperature readings
- `geterror(hand_id=1)`: Get error codes

#### Error Handling
- `reset_error()`: Clear error conditions

### InspireHandModbus

Main class for controlling the Inspire Hand via Modbus TCP.

#### Constructor
- `InspireHandModbus(ip="192.168.11.210", port=6000, generation=3, debug=False)`

#### Connection Methods
- `connect()`: Establish Modbus TCP connection to the hand
- `disconnect()`: Close Modbus TCP connection

#### Motion Control
- `set_angle(angles)`: Set finger angles (list of 6 integers, 0-1000)
- `set_position(positions)`: Set finger positions
- `set_speed(speeds)`: Set motion speeds
- `set_force(forces)`: Set force limits

#### Sensor Reading
- `getangleact()`: Get current finger angles
- `getpositionact()`: Get current finger positions
- `getforceact()`: Get current forces
- `gettemp()`: Get temperature readings

## Hardware Setup

### Serial Communication
1. Connect the Inspire Hand to your computer via USB
2. Install appropriate drivers if needed
3. Note the serial port:
   - Windows: Usually `COM3`, `COM7`, etc.
   - Linux: Usually `/dev/ttyUSB0`, `/dev/ttyACM0`, etc.
   - macOS: Usually `/dev/tty.usbserial-*`

### Modbus TCP Communication
1. Connect the Inspire Hand to your network via Ethernet
2. Configure the hand's IP address (default: `192.168.11.210`)
3. Ensure network connectivity between your computer and the hand
4. Default Modbus port: `6000`

## Configuration

### Default Settings

#### Serial Communication
- **Port**: `COM3` (Windows) or `/dev/ttyUSB0` (Linux/macOS)
- **Baudrate**: `115200`

#### Modbus TCP Communication  
- **IP Address**: `192.168.11.210`
- **Port**: `6000`
- **Generation**: `3` (use `4` for Gen4 hands)

### Custom Configuration

```python
# Custom serial configuration
from inspire_demos import InspireHandSerial
api = InspireHandSerial(port="/dev/ttyUSB1", baudrate=9600)

# Custom Modbus TCP configuration
from inspire_demos import InspireHandModbus
api = InspireHandModbus(ip="192.168.1.100", port=502, generation=4, debug=True)

# Check available serial ports
import serial.tools.list_ports
ports = list(serial.tools.list_ports.comports())
for port in ports:
        print(f"Port: {port.device}, Description: {port.description}")
```

## Development

### Setting up Development Environment

```bash
# Clone the repository
git clone https://github.com/TechShare-inc/inspire_demos.git
cd inspire_demos

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode with dev dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=inspire_demos --cov-report=html

# Run specific test file
pytest tests/test_api.py
```

### Stress Testing

The library includes built-in stress testing capabilities for performance evaluation:

```bash
# Run stress test demo
python examples/stress_test_demo.py

# This will generate:
# - CSV data files with performance metrics
# - PNG visualization plots  
# - TXT reports with statistics
```

Stress test outputs include:
- Response time measurements
- Success/failure rates
- Performance graphs and charts
- Detailed statistical reports

### Code Quality

This project uses several tools to maintain code quality:

- **Black**: Code formatting
- **Flake8**: Linting
- **MyPy**: Type checking
- **Pre-commit**: Git hooks for code quality

```bash
# Format code
black src/ examples/ tests/

# Check linting
flake8 src/ examples/ tests/

# Type checking
mypy src/
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Requirements

- Python 3.8 or higher
- **Core Dependencies**:
  - `pyserial>=3.4`: Serial communication
  - `pymodbus>=3.0`: Modbus TCP communication
  - `numpy>=1.20`: Numerical computations
  - `loguru>=0.6`: Logging
  - `matplotlib>=3.5`: Data visualization and plotting
- **Hardware**: Inspire Hand robotic device with serial or network connection

## Troubleshooting

### Common Issues

1. **Serial Connection Failed**: 
   - Check if the device is properly connected via USB
   - Verify the correct COM port
   - Ensure no other applications are using the port
   - Try different baudrate settings

2. **Modbus TCP Connection Failed**:
   - Verify network connectivity (`ping 192.168.11.210`)
   - Check if the hand's IP address is correct
   - Ensure the Modbus port (6000) is not blocked by firewall
   - Verify the hand is powered on and network-enabled

3. **Permission Denied (Linux/macOS)**:
   ```bash
   sudo chmod 666 /dev/ttyUSB0
   # Or add user to dialout group
   sudo usermod -a -G dialout $USER
   ```

4. **Import Errors**:
   - Make sure the package is installed: `pip install -e .`
   - Check Python path includes the src directory
   - Verify all dependencies are installed: `pip install -e ".[dev]"`

5. **Generation Compatibility**:
   - Use `generation=3` for Gen3 Inspire Hands
   - Use `generation=4` for Gen4 Inspire Hands
   - Check hand documentation for correct generation

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, please open an issue on the [GitHub repository](https://github.com/TechShare-inc/inspire_demos/issues).

## Changelog

### v0.2.0
- Added Modbus TCP communication support
- Enhanced API with dual protocol support (Serial + Modbus TCP)
- Added multi-generation support (Gen3/Gen4)
- Improved stress testing capabilities
- Updated documentation and examples
- Added debug mode for troubleshooting

### v0.1.0
- Initial release
- Basic API for hand control
- Example scripts
- Unit tests
- Documentation
```

## API Features

The library provides comprehensive functionality through two main classes:

### InspireHandSerial Features:
- Connect/disconnect via serial communication
- Reset errors and error handling
- Set finger angles and positions
- Set movement speed and force limits
- Read current angles, positions, forces, and sensor data
- Perform predefined actions (open/close)
- Support for multiple hand IDs

### InspireHandModbus Features:
- Connect/disconnect via Modbus TCP
- Set finger angles and positions  
- Set movement speed and force limits
- Read current angles, positions, forces, and sensor data
- Support for Gen3 and Gen4 hand generations
- Debug mode for troubleshooting
- Network-based communication

## Error Handling

The API includes built-in error handling for:
- Serial communication issues
- Modbus TCP connection problems
- Invalid COM ports and network addresses  
- Communication timeouts and retries
- Hardware error detection and reporting
- Graceful shutdown on keyboard interrupt

## Notes

- Make sure the hand is properly connected before running the scripts
- **Serial Communication**: Default baudrate is 115200
- **Modbus TCP**: Default IP is 192.168.11.210, port 6000
- The API supports both Windows and Linux systems
- All angle values are in the range of 0-1000
- Choose the appropriate communication method based on your hardware setup
- Use `generation=3` for Gen3 hands, `generation=4` for Gen4 hands
- Enable debug mode for troubleshooting network communication issues 