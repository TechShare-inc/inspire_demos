# Inspire Hand Examples

This directory contains example scripts for testing and demonstrating the Inspire robotic hand functionality. These examples are designed to help engineers quickly understand and test different aspects of the robotic hand system.

## 🖥️ Platform Support

✅ **Windows** (Primary development platform - PowerShell)  
✅ **Ubuntu/Linux** (Fully supported - bash)  

> **Note**: This project was developed on Windows but works seamlessly on Ubuntu/Linux systems. All commands are provided for both platforms.

## 🚀 Quick Start

### Prerequisites
1. **Hardware Setup**: Ensure your Inspire robotic hand is properly connected
2. **Python Environment**: Install the inspire_demos package and dependencies
3. **Communication**: Configure either Serial (USB) or Modbus (Ethernet) connection

### Installation

**Windows (PowerShell):**
```powershell
pip install -r requirements.txt
# or if using the package locally:
pip install -e .
```

**Ubuntu/Linux (bash):**
```bash
pip install -r requirements.txt
# or if using the package locally:
pip install -e .
```

> **Note**: This project works on both Windows and Ubuntu/Linux systems. Examples below show both PowerShell and bash commands where applicable.

## 📋 Example Files Overview

### 1. `basic_serial_demo.py` - Serial Communication Basics
**Purpose**: Learn serial communication fundamentals with the robotic hand.

**What it does**:
- Interactive serial communication demo
- Basic hand movements (open/close)
- Precision grip demonstrations
- Real-time position feedback

**When to use**: 
- First time testing the hand
- Learning serial communication
- Debugging connection issues

**Hardware required**: USB connection to the hand

**How to run**:

**Windows (PowerShell):**
```powershell
python basic_serial_demo.py
```

**Ubuntu/Linux (bash):**
```bash
python3 basic_serial_demo.py
```

**Configuration**: Update the COM port in the script (default: COM3)

---

### 2. `modbus_demo.py` - Modbus Communication & Sensors
**Purpose**: Explore advanced Modbus features including tactile sensor reading.

**What it does**:
- Modbus TCP communication
- Real-time tactile sensor data reading
- Hand position monitoring
- Optional sensor heatmap visualization

**When to use**:
- Testing Generation 4 hands with tactile sensors
- Advanced sensor data analysis
- Network-based communication testing

**Hardware required**: Ethernet connection to the hand

**How to run**:

**Windows (PowerShell):**
```powershell
python modbus_demo.py
```

**Ubuntu/Linux (bash):**
```bash
python3 modbus_demo.py
```

**Configuration**: Update IP address in the script (default: 192.168.11.210)

---

### 3. `dual_interface_demo.py` - Simultaneous Serial + Modbus
**Purpose**: Demonstrate using both communication methods simultaneously.

**What it does**:
- Controls hand via Serial (reliable command sending)
- Monitors position via Modbus (real-time feedback)
- Reads tactile data via Modbus
- Continuous operation loop

**When to use**:
- Production applications requiring dual redundancy
- Real-time monitoring while controlling
- Testing communication reliability

**Hardware required**: Both USB and Ethernet connections

**How to run**:

**Windows (PowerShell):**
```powershell
python dual_interface_demo.py
```

**Ubuntu/Linux (bash):**
```bash
python3 dual_interface_demo.py
```

**Configuration**: Update both COM port and IP address in the script

---

### 4. `stress_test_demo.py` - Communication Performance Testing
**Purpose**: Test communication reliability and performance under stress.

**What it does**:
- Automated stress testing of both Serial and Modbus
- Performance metrics collection
- Error rate analysis
- Data logging and visualization

**When to use**:
- System integration testing
- Performance validation
- Troubleshooting communication issues
- Quality assurance testing

**Hardware required**: Either USB or Ethernet connection (or both)

**How to run**:

**Windows (PowerShell):**
```powershell
python stress_test_demo.py
```

**Ubuntu/Linux (bash):**
```bash
python3 stress_test_demo.py
```

**Output**: Generates CSV files and performance reports

---

### 5. `tactile_data_demo.py` - Simple Tactile Data Collection & Trend Visualization
**Purpose**: Collect tactile sensor data for 10 seconds and visualize trends.

**What it does**:
- Connects to Gen4 hand via Modbus
- Collects tactile data from all sensors for 10 seconds
- Plots trends showing how sensor values change over time
- Displays summary statistics for each sensor
- Simple, single-function approach

**When to use**:
- Quick tactile sensor validation
- Understanding baseline sensor behavior
- Checking for sensor drift or anomalies
- Simple data collection for analysis

**Hardware required**: Generation 4 hand with Ethernet connection

**How to run**:

**Windows (PowerShell):**
```powershell
python tactile_data_demo.py
```

**Ubuntu/Linux (bash):**
```bash
python3 tactile_data_demo.py
```

**Configuration**: Update IP address in the script (default: 192.168.11.210)
**Output**: Interactive plot showing sensor trends over time

## 🔧 Configuration Guide

### Serial Connection Setup
1. **Find COM Port**: 
   - **Windows**: Check Device Manager → Ports (COM & LPT)
   - **Ubuntu/Linux**: Check `/dev/ttyUSB*` or `/dev/ttyACM*`
2. **Update Script**: Modify the `port` parameter in the script
3. **Baudrate**: Usually 115200 (default in scripts)

**Windows:**
```python
serial_hand = InspireHandSerial(port="COM3", generation=4)
```

**Ubuntu/Linux:**
```python
serial_hand = InspireHandSerial(port="/dev/ttyUSB0", generation=4)
```

### Modbus Connection Setup
1. **Check IP Address**: Use network scanner or hand documentation
2. **Network**: Ensure PC and hand are on same network
3. **Update Script**: Modify the `ip` parameter

```python
modbus_hand = InspireHandModbus(ip="192.168.11.210", generation=4)
```

## 🎯 Testing Workflow for Dev Engineers

### Step 1: Basic Connectivity Test
Start with `basic_serial_demo.py`:
1. Connect hand via USB
2. Run the script
3. Verify basic movements work
4. Check position feedback

### Step 2: Advanced Features Test
Try `modbus_demo.py`:
1. Connect hand via Ethernet
2. Test sensor data reading
3. Verify tactile feedback (Gen 4 only)

### Step 3: Tactile Data Analysis (Gen4 only)
Use `tactile_data_demo.py`:
1. Connect Gen4 hand via Ethernet
2. Collect tactile data for 10 seconds
3. Analyze sensor heatmaps and time series
4. Export data for further analysis

### Step 4: Production Simulation
Use `dual_interface_demo.py`:
1. Connect both USB and Ethernet
2. Test simultaneous communication
3. Verify real-time monitoring

### Step 5: Performance Validation
Run `stress_test_demo.py`:
1. Choose communication method
2. Run stress tests
3. Analyze performance reports

## 📊 Understanding Output

### Position Data
- **Format**: Array of 6 integers [pinky, ring, middle, index, thumb, thumb_extend]
- **Range**: 0 (closed) to 1000 (open)
- **Units**: Motor encoder ticks

### Tactile Data (Generation 4 only)
- **Palm sensor**: 4x4 matrix of pressure values
- **Finger sensors**: Individual finger tip sensors
- **Units**: Pressure readings (0-4095)

### Error Messages
- **Connection errors**: Check cables and network settings
- **Timeout errors**: Hand may be busy or disconnected
- **Permission errors**: Check COM port permissions

## 🐛 Troubleshooting

### Common Issues

**"Port not found" error**:
- **Windows**: Check if COM port is correct in Device Manager
- **Ubuntu/Linux**: Check if `/dev/ttyUSB*` or `/dev/ttyACM*` exists
- Verify hand is powered on
- Try different USB cable

**"Connection timeout" error**:
- Check IP address and network connection
- Verify hand is on same subnet
- **Windows**: Check Windows Firewall settings
- **Ubuntu/Linux**: Check iptables/ufw firewall settings

**"Hand not responding"**:
- Power cycle the hand
- Check all connections
- Verify generation setting in code

**Permission denied (Ubuntu/Linux)**:
```bash
sudo usermod -a -G dialout $USER
# Then logout and login again
```

**Permission issues (Windows)**:
- Run PowerShell as Administrator if needed
- Check if another application is using the COM port

## 📝 Customization Tips

### Creating Your Own Example
1. Copy an existing example as template
2. Modify connection parameters
3. Add your specific test movements
4. Include proper error handling

### Adding New Movements
```python
# Define custom movement sequences
custom_movements = [
    [0, 0, 0, 0, 200, 1000],      # Your custom position
    [500, 500, 500, 500, 500, 500],  # Another position
]
```

### Logging and Data Collection
All examples include basic logging. For advanced logging:

**Windows (PowerShell):**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Ubuntu/Linux (bash):**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📚 Additional Resources

- **Main Documentation**: See `docs/` directory
- **API Reference**: Check the main `inspire_demos` module
- **Hardware Manual**: Refer to your hand's hardware documentation
- **Network Setup**: See `docs/MODBUS_IMPLEMENTATION.md`

## ⚠️ Safety Notes

1. **Power Management**: Always ensure proper power supply
2. **Movement Limits**: Respect hand movement limits
3. **Emergency Stop**: Keep hand power switch accessible
4. **Testing Environment**: Use in safe, controlled environment
5. **Gradual Testing**: Start with slow movements before high-speed tests

---

**Happy Testing! 🤖**

For questions or issues, refer to the main project documentation or contact the development team.
