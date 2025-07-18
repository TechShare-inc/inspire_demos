# InspireHandModbus Implementation

This document describes the new `InspireHandModbus` class that provides Modbus TCP communication for the Inspire Hand robotic hand.

## Features

The `InspireHandModbus` class provides the same interface as `InspireHandSerial` but uses Modbus TCP communication instead of serial communication. This is particularly useful for:

- Network-based control
- Remote operation
- Integration with industrial automation systems
- Multi-device control scenarios

## Key Features

### Connection Management
- TCP connection with configurable IP and port
- Connection status monitoring
- Graceful disconnect handling
- Connection validation

### Hand Control
- Joint angle control (0-1000 range)
- Speed and force parameter setting
- Support for numpy arrays as input
- Special value handling (-1 as placeholder)

### Data Reading
- Real-time joint position feedback
- Force and speed monitoring
- Temperature and error status reading
- 16-bit and 8-bit register reading support

### Hardware Compatibility
- Generation 3 and 4 hardware support
- Register address validation
- Debug output for troubleshooting

## Usage Examples

### Basic Connection and Control

```python
import numpy as np
from inspire_demos.api import InspireHandModbus

# Initialize connection
hand = InspireHandModbus(ip="192.168.11.210", port=6000, generation=3, debug=True)

# Connect to the hand
if hand.connect():
    # Set movement parameters
    speeds = np.array([800, 800, 800, 800, 800, 800], dtype=np.int32)
    forces = np.array([500, 500, 500, 500, 500, 500], dtype=np.int32)
    
    hand.set_speed(speeds)
    hand.set_force(forces)
    
    # Move to position
    angles = np.array([1000, 1000, 1000, 1000, 1000, 1000], dtype=np.int32)
    hand.set_angle(angles)
    
    # Read feedback
    actual_angles = hand.get_angle_actual()
    print(f"Current angles: {actual_angles}")
    
    # Disconnect when done
    hand.disconnect()
```

### Action Sequences

```python
# Set and run predefined action sequence
hand.set_action_sequence(2)
hand.run_action_sequence()
```

### Error Monitoring

```python
# Check system status
errors = hand.get_error()
temps = hand.get_temp()
status = hand.get_status()

print(f"Errors: {errors}")
print(f"Temperatures: {temps}")
print(f"Status: {status}")
```

## Register Mapping

The class uses the same register dictionary as the serial interface but communicates via Modbus TCP:

- **16-bit registers**: Angle, force, speed values (6 registers each)
- **8-bit registers**: Error codes, temperature, status (3 registers split into high/low bytes)
- **Action sequences**: Predefined movement patterns

## Comparison with Serial Interface

| Feature | InspireHandSerial | InspireHandModbus |
|---------|-------------------|-------------------|
| Connection | COM port | TCP/IP |
| Protocol | Custom serial | Modbus TCP |
| Network Support | No | Yes |
| Multi-device | Limited | Excellent |
| Industrial Integration | Basic | Advanced |
| Latency | Very Low | Low |
| Setup Complexity | Simple | Moderate |

## Technical Details

### Data Format Differences

**Serial Interface:**
- Uses custom byte protocol
- 12-byte values for 6 joints (2 bytes per joint)
- Direct byte manipulation

**Modbus Interface:**
- Uses standard Modbus TCP protocol
- 6 register values for 6 joints (1 register per joint)
- 16-bit register format

### Error Handling

The Modbus implementation includes:
- Connection status validation
- Modbus response error checking
- Register address validation
- Graceful error recovery

### Debug Support

Enable debug mode for detailed logging:
```python
hand = InspireHandModbus(debug=True)
hand.set_debug(True)  # Can also enable later
```

## Dependencies

The Modbus implementation requires:
- `pymodbus>=3.0` - Modbus TCP communication
- `numpy>=1.20` - Array handling
- `loguru>=0.6` - Logging

## Network Configuration

Default network settings:
- **IP Address**: 192.168.11.210
- **Port**: 6000
- **Protocol**: Modbus TCP

These can be configured during initialization:
```python
hand = InspireHandModbus(ip="10.0.0.100", port=502)
```

## Error Codes and Troubleshooting

Common issues and solutions:

1. **Connection Failed**: Check IP address, port, and network connectivity
2. **Register Read Errors**: Validate register addresses with `validate_register_addresses()`
3. **Invalid Data**: Check numpy array format and value ranges
4. **Timeout Issues**: Increase network timeout or check network latency

## Future Enhancements

Potential improvements:
- Async/await support for non-blocking operations
- Connection pooling for multiple devices
- Advanced error recovery mechanisms
- Performance optimization for high-frequency control
