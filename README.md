# Inspire Hand Control Demo

This project provides a Python-based interface for controlling the Inspire Hand robotic hand. It includes demo scripts and an API for basic hand control operations.

## Demo Scripts

### demo1.py
A basic demonstration script that shows how to:
- Connect to the Inspire Hand
- Reset errors
- Perform a sequence of finger movements
- Handle graceful shutdown

The script demonstrates a predefined motion sequence that moves the fingers in a wave-like pattern.

## Environment Setup

### Using Conda

1. Create a new conda environment:
```bash
conda create -n inspire python=3.11
conda activate inspire
```

2. Install required packages:
```bash
conda install pyserial
```

## Required Packages

The project requires the following external Python packages:
- `pyserial`: For serial communication with the hand

## Usage

1. Connect the Inspire Hand to your computer via USB
2. Note the COM port (Windows) or device path (Linux) where the hand is connected
3. Run the demo script:
```bash
python demo1.py
```

By default, the script uses:
- Port: COM7 (Windows) or /dev/ttyUSB0 (Linux)
- Baudrate: 115200

You can modify these parameters in the script if needed.

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