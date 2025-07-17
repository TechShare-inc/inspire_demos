# Inspire Hand Control Library

A Python library for controlling the Inspire Hand robotic hand via serial communication. This package provides a simple and intuitive API for connecting to and controlling the Inspire Hand through various motion commands and sensor readings.

## Features

- **Simple API**: Easy-to-use Python interface for hand control
- **Motion Control**: Set individual finger angles, perform predefined gestures
- **Sensor Reading**: Read current angles, forces, and temperature data
- **Error Handling**: Built-in error detection and recovery
- **Cross-Platform**: Works on Windows, Linux, and macOS
- **Configurable**: Customizable communication parameters

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

```python
from inspire_demos import InspireHandAPI
import time

# Create API instance
api = InspireHandAPI(port="COM7", baudrate=115200)

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

## Examples

The `examples/` directory contains demonstration scripts:

- `basic_demo.py`: Basic motion sequence demonstration
- `advanced_demo.py`: Advanced features including sensor reading and custom gestures

### Running Examples

```bash
# Basic demo
python examples/basic_demo.py

# Advanced demo with custom port
python examples/advanced_demo.py --port COM5 --baudrate 9600
```

## API Reference

### InspireHandAPI

Main class for controlling the Inspire Hand.

#### Connection Methods
- `connect()`: Establish connection to the hand
- `disconnect()`: Close connection

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

## Hardware Setup

1. Connect the Inspire Hand to your computer via USB
2. Install appropriate drivers if needed
3. Note the serial port:
   - Windows: Usually `COM3`, `COM7`, etc.
   - Linux: Usually `/dev/ttyUSB0`, `/dev/ttyACM0`, etc.
   - macOS: Usually `/dev/tty.usbserial-*`

## Configuration

### Default Settings
- **Port**: `COM3` (Windows) or `/dev/ttyUSB0` (Linux/macOS)
- **Baudrate**: `115200`

### Custom Configuration

```python
# Custom port and baudrate
api = InspireHandAPI(port="/dev/ttyUSB1", baudrate=9600)

# Check available ports
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
- pyserial library
- Serial connection to Inspire Hand device

## Troubleshooting

### Common Issues

1. **Connection Failed**: 
   - Check if the device is properly connected
   - Verify the correct COM port
   - Ensure no other applications are using the port

2. **Permission Denied (Linux/macOS)**:
   ```bash
   sudo chmod 666 /dev/ttyUSB0
   # Or add user to dialout group
   sudo usermod -a -G dialout $USER
   ```

3. **Import Errors**:
   - Make sure the package is installed: `pip install -e .`
   - Check Python path includes the src directory

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, please open an issue on the [GitHub repository](https://github.com/TechShare-inc/inspire_demos/issues).

## Changelog

### v0.1.0
- Initial release
- Basic API for hand control
- Example scripts
- Unit tests
- Documentation
```

## API Features

The `InspireHandAPI` class provides the following main functionalities:
- Connect/disconnect to the hand
- Reset errors
- Set finger angles
- Set finger positions
- Set movement speed
- Set force limits
- Read current angles, positions, and other sensor data
- Perform predefined actions (open/close)

## Error Handling

The API includes built-in error handling for:
- Connection issues
- Invalid COM ports
- Communication errors
- Graceful shutdown on keyboard interrupt

## Notes

- Make sure the hand is properly connected before running the scripts
- The default baudrate is 115200
- The API supports both Windows and Linux systems
- All angle values are in the range of 0-1000 