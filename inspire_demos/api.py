from abc import ABC, abstractmethod
import os
from typing import Any, Union, List
import serial
import time
import asyncio
from loguru import logger
import logging

try:
    import numpy as np
    import numpy.typing as npt
    NUMPY_AVAILABLE = True
except ImportError:
    raise ImportError("NumPy is required for this API. Please install it with: pip install numpy")

import serial.tools

if os.name == "posix":
    import serial.tools.list_ports_posix
elif os.name == "nt":
    import serial.tools.list_ports_windows
elif os.name == "linux":
    import serial.tools.list_ports_linux

# Register addresses verified through reverse engineering - use validation methods for manufacturer verification
# Use validate_register_addresses() and export_register_verification_report() to identify potential issues
regdict = {
    "HAND_ID": 1000,
    "REDU_RATIO": 1001,
    # "baudrate": 1002, # This is the manual's baudrate register, but it seems unused in actual code
    "CLEAR_ERROR": 1004,
    "SAVE": 1005,
    "RESET_PARA": 1006,
    "GESTURE_FORCE_CLB": 1009,
    "CURRENT_LIMIT": 1020,
    "DEFAULT_SPEED_SET": 1032,
    "DEFAULT_FORCE_SET": 1044,
    "VLTAGE": 1472,
    "POS_SET": 1474,
    "ANGLE_SET": 1486,
    "FORCE_SET": 1498,
    "SPEED_SET": 1522,
    "POS_ACT": 1534,
    "ANGLE_ACT": 1546,
    "FORCE_ACT": 1582,
    "CURRENT": 1594,
    "ERROR": 1606,
    "STATUS": 1612,
    "TEMP": 1618,
    "ACTION_SEQ_CHECKDATA1": 2000,
    "ACTION_SEQ_CHECKDATA2": 2001,
    "ACTION_SEQ_STEPNUM": 2002,
    "ACTION_SEQ_STEP0": 2016,
    "ACTION_SEQ_STEP1": 2054,
    "ACTION_SEQ_STEP2": 2092,
    "ACTION_SEQ_STEP3": 2130,
    "ACTION_SEQ_STEP4": 2168,
    "ACTION_SEQ_STEP5": 2206,
    "ACTION_SEQ_STEP6": 2244,
    "ACTION_SEQ_STEP7": 2282,
    "ACTION_SEQ_INDEX": 2320,
    "SAVE_ACTION_SEQ": 2321,
    "ACTION_SEQ_RUN": 2322,
    "ACTION_ADJUST_FORCE_SET": 2334,
}

regdict_gen4 = {
    "HAND_ID": 1000,
    "REDU_RATIO": 1001,
    # "baudrate": 1002, # This is the manual's baudrate register, but it seems unused in actual code
    "CLEAR_ERROR": 1004,
    "SAVE": 1005,
    "RESET_PARA": 1006,
    "GESTURE_FORCE_CLB": 1009,
    "DEFAULT_SPEED_SET": 1032,
    "DEFAULT_FORCE_SET": 1044,
    "POS_SET": 1474,
    "ANGLE_SET": 1486,
    "FORCE_SET": 1498,
    "SPEED_SET": 1522,
    "POS_ACT": 1534,
    "ANGLE_ACT": 1546,
    "FORCE_ACT": 1582,
    "CURRENT": 1594,
    "ERROR": 1606,
    "STATUS": 1612,
    "TEMP": 1618,
    "IP_PART1": 1700,
    "IP_PART2": 1701,
    "IP_PART3": 1702,
    "IP_PART4": 1703,

    "FINGERONE_TOUCH": 3000, # Pinky
    "FINGERTWO_TOUCH": 3370, # Ring
    "FINGERTHE_TOUCH": 3740, # Middle
    "FINGERFOR_TOUCH": 4110, # Index
    "FINGERFIV_TOUCH": 4480, # Thumb
    "FINGERPALM_TOUCH": 4900, # Palm
}

DEFAULT_PORT = "COM3" if os.name == "nt" else "/dev/ttyUSB0"
DEFAULT_BAUDRATE = 115200

class InspireHandAPI:
    _logger = logger
    _ser: serial.Serial
    _port: str
    _baudrate: int
    _generation: int  # 3 for Gen3, 4 for Gen4
    _debug: bool  # Enable debug output for Gen4 compatibility

    def __init__(self, port: str = DEFAULT_PORT, baudrate: int = DEFAULT_BAUDRATE, generation: int = 3, debug: bool = False):
        self._port = port
        self._baudrate = baudrate
        self._generation = generation
        self._debug = debug
        self._ser = None  # Initialize as None, will be created in connect()

    @property
    def _regdict(self) -> dict:
        """Get the appropriate register dictionary based on generation"""
        if self._generation == 4:
            return regdict_gen4
        else:
            return regdict

    def _validate_com_port(self) -> bool:
        if os.name == "nt":
            self._logger.debug(f"Checking COM port {self._port} on Windows")
            ports = list(serial.tools.list_ports_windows.comports())
            if self._port not in [p.device for p in ports]:
                self._logger.error(f"Port {self._port} not found")
                return False
            else:
                return True
        elif os.name == "posix":
            self._logger.debug(f"Checking Linux port {self._port}")
            ports = list(serial.tools.list_ports_posix.comports())
            if self._port not in [p.device for p in ports]:
                self._logger.error(f"Port {self._port} not found")
                return False
            else:
                return True
        else:
            self._logger.error(f"Unsupported OS: {os.name}")
            return False

    def connect(self) -> bool:
        try:
            self._ser = serial.Serial(self._port, self._baudrate)

        except Exception as e:
            self._logger.error(
                f"Failed to connect to {self._port} with baudrate {self._baudrate}: {e}"
            )
            return False
        return True

    def disconnect(self) -> bool:
        if self._ser:
            try:
                self._ser.close()
                return True
            except Exception as e:
                self._logger.error(f"Failed to disconnect from {self._ser.port}: {e}")
                return False
        return True

    def reset_error(self) -> bool:
        return self._write_register(1, self._regdict["CLEAR_ERROR"], 1, [0x01])

    def return_to_zero(self) -> bool:
        """Return all joints to zero position."""
        return self.set_angle(np.array([0, 0, 0, 0, 0, 0], dtype=np.int32))

    def perform_open(self) -> bool:
        """Open the hand (set all joints to maximum position)."""
        return self.set_angle(np.array([1000, 1000, 1000, 1000, 1000, 1000], dtype=np.int32))

    def perform_close(self) -> bool:
        """Close the hand (set all joints to zero position)."""
        return self.set_angle(np.array([0, 0, 0, 0, 0, 0], dtype=np.int32))

    def set_angle(self, angles: npt.NDArray[np.integer], hand_id: int = 1) -> bool:
        """Set joint angles. Accepts numpy arrays only."""
        if not isinstance(angles, np.ndarray):
            raise TypeError("angles must be a numpy.ndarray")
            
        # Ensure array is 1D and convert to list of integers for serial processing
        angles_flat = angles.flatten().astype(np.int32)
        
        if len(angles_flat) != 6:
            raise ValueError(f"Expected 6 angle values, got {len(angles_flat)}")
            
        angles_list = angles_flat.tolist()
        val_reg = []
        for angle in angles_list:
            val_reg.append(angle & 0xFF)
            val_reg.append((angle >> 8) & 0xFF)

        self._write_register(hand_id, self._regdict["ANGLE_SET"], 12, val_reg)
        return True

    def set_pos(self, positions: npt.NDArray[np.integer], hand_id: int = 1) -> bool:
        """Set joint positions. Accepts numpy arrays only."""
        if not isinstance(positions, np.ndarray):
            raise TypeError("positions must be a numpy.ndarray")
            
        # Ensure array is 1D and convert to list of integers for serial processing
        positions_flat = positions.flatten().astype(np.int32)
        
        if len(positions_flat) != 6:
            raise ValueError(f"Expected 6 position values, got {len(positions_flat)}")
            
        positions_list = positions_flat.tolist()
        val_reg = []
        for pos in positions_list:
            val_reg.append(pos & 0xFF)
            val_reg.append((pos >> 8) & 0xFF)

        self._write_register(hand_id, self._regdict["ANGLE_SET"], 12, val_reg)
        return True

    def set_speed(self, speeds: npt.NDArray[np.integer], hand_id: int = 1) -> bool:
        """Set joint speeds. Accepts numpy arrays only."""
        if not isinstance(speeds, np.ndarray):
            raise TypeError("speeds must be a numpy.ndarray")
            
        # Ensure array is 1D and convert to list of integers for serial processing
        speeds_flat = speeds.flatten().astype(np.int32)
        
        if len(speeds_flat) != 6:
            raise ValueError(f"Expected 6 speed values, got {len(speeds_flat)}")
            
        speeds_list = speeds_flat.tolist()
        val_reg = []
        for speed in speeds_list:
            val_reg.append(speed & 0xFF)
            val_reg.append((speed >> 8) & 0xFF)

        self._write_register(hand_id, self._regdict["SPEED_SET"], 12, val_reg)
        return True

    def set_force(self, forces: npt.NDArray[np.integer], hand_id: int = 1) -> bool:
        """Set joint forces. Accepts numpy arrays only."""
        if not isinstance(forces, np.ndarray):
            raise TypeError("forces must be a numpy.ndarray")
            
        # Ensure array is 1D and convert to list of integers for serial processing
        forces_flat = forces.flatten().astype(np.int32)
        
        if len(forces_flat) != 6:
            raise ValueError(f"Expected 6 force values, got {len(forces_flat)}")
            
        forces_list = forces_flat.tolist()
        val_reg = []
        for force in forces_list:
            val_reg.append(force & 0xFF)
            val_reg.append((force >> 8) & 0xFF)

        self._write_register(hand_id, self._regdict["FORCE_SET"], 12, val_reg)
        return True

    
    def _write_register(self, id: int, addr: int, num: int, val: list[int]) -> bool:
        """Write to a register with address validation"""
        if self._ser is None:
            self._logger.error("Serial connection not established. Call connect() first.")
            return False
            
        # Validate register address exists in current generation
        valid_addrs = set(self._regdict.values())
        if addr not in valid_addrs:
            raise ValueError(f"Register address {addr} not valid for generation {self._generation}")
            
        bytes = [0xEB, 0x90]
        bytes.append(id)  # id
        bytes.append(num + 3)  # len
        bytes.append(0x12)  # cmd
        bytes.append(addr & 0xFF)
        bytes.append((addr >> 8) & 0xFF)  # add
        for i in range(num):
            bytes.append(val[i])
        checksum = 0x00
        for i in range(2, len(bytes)):
            checksum += bytes[i]
        checksum &= 0xFF
        bytes.append(checksum)
        
        if self._debug:
            self._logger.debug(f"Writing to register {addr} for hand {id}: {val}")
            
        self._ser.write(bytearray(bytes))

        while self._ser.in_waiting > 0:
            self._ser.read_all()  # 把返回帧读掉，不处理
            time.sleep(0.01)

        return True

    def _read_register(self, id: int, addr: int, num: int) -> list[int]:
        """Read from a register with improved error handling"""
        if self._ser is None:
            self._logger.error("Serial connection not established. Call connect() first.")
            return []
            
        bytes = [0xEB, 0x90]
        bytes.append(id)  # id
        bytes.append(0x04)  # len
        bytes.append(0x11)  # cmd
        bytes.append(addr & 0xFF)
        bytes.append((addr >> 8) & 0xFF)  # add
        bytes.append(num)
        checksum = 0x00
        for i in range(2, len(bytes)):
            checksum += bytes[i]
        checksum &= 0xFF
        bytes.append(checksum)
        
        if self._debug:
            self._logger.debug(f"Reading {num} bytes from register {addr} for hand {id}")
            
        self._ser.write(bytearray(bytes))

        time.sleep(0.01)
        recv = self._ser.read_all()

        if recv is None or len(recv) == 0:
            if self._debug:
                self._logger.warning(f"Failed to fetch data from register {addr} for hand {id}")
            return []
            
        # Improved data validation
        if len(recv) < 7:  # Minimum frame size
            if self._debug:
                self._logger.warning(f"Fetched data is too short: {len(recv)} bytes")
            return []
            
        num_received = (recv[3] & 0xFF) - 3
        if num_received != num:
            if self._debug:
                self._logger.warning(f"Expected to have {num} bytes, but received {num_received} bytes")
                
        val = []
        actual_data_len = min(num_received, len(recv) - 7)
        for i in range(actual_data_len):
            val.append(recv[7 + i])

        if self._debug:
            self._logger.debug(f"Read {actual_data_len} values from register {addr}: {val}")

        return val

    def _read6(self, id: int, reg_name: str) -> list[int]:
        """Read 6 bytes from a named register"""
        if reg_name not in self._regdict:
            raise ValueError(f"Register '{reg_name}' not valid for generation {self._generation}")
            
        length = 6
        val_act = self._read_register(id, self._regdict[reg_name], length)
        
        if val_act is None or len(val_act) < length:
            if self._debug:
                self._logger.warning(f"Failed to fetch data from {reg_name} for hand {id}")
            return []
            
        if self._debug:
            self._logger.info(f"Read {reg_name}: {' '.join(map(str, val_act))}")

        return val_act

    def _read12(self, id: int, reg_name: str) -> list[int]:
        """Read 12 bytes from a named register and convert to 6 16-bit values"""
        if reg_name not in self._regdict:
            raise ValueError(f"Register '{reg_name}' not valid for generation {self._generation}")

        length = 12
        val = self._read_register(id, self._regdict[reg_name], length)
        
        if len(val) < length:
            if self._debug:
                self._logger.warning(f"Failed to fetch data from {reg_name} for hand {id}")
            return []
            
        # Convert pairs of bytes to 16-bit values
        val_act = []
        for i in range(length // 2):
            val_act.append((val[2 * i] & 0xFF) + (val[1 + 2 * i] << 8))
            
        if self._debug:
            self._logger.info(f"Read {reg_name}: {' '.join(map(str, val_act))}")

        return val_act

    def get_angle_actual(self, hand_id: int = 1) -> npt.NDArray[np.int32]:
        """Get actual joint angles as numpy array."""
        result = self._read12(hand_id, "ANGLE_ACT")
        return np.array(result, dtype=np.int32)

    def get_angle_set(self, hand_id: int = 1) -> npt.NDArray[np.int32]:
        """Get set joint angles as numpy array.""" 
        result = self._read12(hand_id, "ANGLE_SET")
        return np.array(result, dtype=np.int32)

    def get_pos_actual(self, hand_id: int = 1) -> npt.NDArray[np.int32]:
        """Get actual joint positions as numpy array."""
        result = self._read12(hand_id, "ANGLE_ACT")
        return np.array(result, dtype=np.int32)

    def get_pos_set(self, hand_id: int = 1) -> npt.NDArray[np.int32]:
        """Get set joint positions as numpy array."""
        result = self._read12(hand_id, "ANGLE_SET")
        return np.array(result, dtype=np.int32)

    def get_speed_set(self, hand_id: int = 1) -> npt.NDArray[np.int32]:
        """Get set joint speeds as numpy array."""
        result = self._read12(hand_id, "SPEED_SET")
        return np.array(result, dtype=np.int32)

    def get_force_actual(self, hand_id: int = 1) -> npt.NDArray[np.int32]:
        """Get actual joint forces as numpy array."""
        result = self._read12(hand_id, "FORCE_ACT")
        return np.array(result, dtype=np.int32)

    def get_force_set(self, hand_id: int = 1) -> npt.NDArray[np.int32]:
        """Get set joint forces as numpy array."""
        result = self._read12(hand_id, "FORCE_SET")
        return np.array(result, dtype=np.int32)

    def get_current_actual(self, hand_id: int = 1) -> npt.NDArray[np.int32]:
        """Get actual current values as numpy array."""
        result = self._read6(hand_id, "CURRENT")
        return np.array(result, dtype=np.int32)

    def get_error(self, hand_id: int = 1) -> npt.NDArray[np.int32]:
        """Get error codes as numpy array."""
        result = self._read6(hand_id, "ERROR")
        return np.array(result, dtype=np.int32)

    def get_temp(self, hand_id: int = 1) -> npt.NDArray[np.int32]:
        """Get temperature values as numpy array."""
        result = self._read6(hand_id, "TEMP")
        return np.array(result, dtype=np.int32)

    def get_pos(self, hand_id: int = 1) -> npt.NDArray[np.int32]:
        """Get current position as numpy array (alias for get_pos_actual)."""
        return self.get_pos_actual(hand_id)

    def set_action_sequence(self, hand_id: int, sequence_id: int) -> bool:
        """Set the action sequence for Gen4 compatibility"""
        return self._write_register(hand_id, self._regdict["ACTION_SEQ_INDEX"], 1, [sequence_id])

    def run_action_sequence(self, hand_id: int) -> bool:
        """Run the current action sequence for Gen4 compatibility"""
        return self._write_register(hand_id, self._regdict["ACTION_SEQ_RUN"], 1, [1])

    def get_generation(self) -> int:
        """Get the hardware generation (3 or 4)"""
        return self._generation

    def set_debug(self, debug: bool) -> None:
        """Enable or disable debug output"""
        self._debug = debug

    def validate_register_addresses(self, hand_id: int = 1) -> dict[str, bool]:
        """
        Validate register addresses by attempting to read from each one.
        This helps identify registers that may have incorrect addresses.
        
        Returns:
            dict: Mapping of register names to validation status (True if readable)
        """
        if self._ser is None:
            self._logger.error("Serial connection not established. Call connect() first.")
            return {}
            
        validation_results = {}
        test_registers = [
            "HAND_ID", "ANGLE_ACT", "POS_ACT", "FORCE_ACT", 
            "CURRENT", "ERROR", "STATUS", "TEMP"
        ]
        
        self._logger.info("Validating register addresses for hardware compatibility...")
        
        for reg_name in test_registers:
            if reg_name not in self._regdict:
                validation_results[reg_name] = False
                self._logger.warning(f"Register '{reg_name}' not found in generation {self._generation} dictionary")
                continue
                
            try:
                # Try to read a small amount of data from each register
                if reg_name in ["CURRENT", "ERROR", "STATUS", "TEMP"]:
                    result = self._read6(hand_id, reg_name)
                else:
                    result = self._read12(hand_id, reg_name)
                    
                validation_results[reg_name] = len(result) > 0
                
                if validation_results[reg_name]:
                    self._logger.debug(f"✓ Register '{reg_name}' (addr: {self._regdict[reg_name]}) is readable")
                else:
                    self._logger.warning(f"✗ Register '{reg_name}' (addr: {self._regdict[reg_name]}) failed to read")
                    
            except Exception as e:
                validation_results[reg_name] = False
                self._logger.error(f"✗ Register '{reg_name}' (addr: {self._regdict[reg_name]}) validation failed: {e}")
                
        successful_validations = sum(validation_results.values())
        total_validations = len(validation_results)
        
        self._logger.info(f"Register validation complete: {successful_validations}/{total_validations} registers accessible")
        
        if successful_validations < total_validations:
            self._logger.warning("Some registers failed validation. Consider verifying addresses with manufacturer.")
            
        return validation_results

    def get_register_info(self) -> dict[str, dict]:
        """
        Get comprehensive information about all registers for the current generation.
        Useful for debugging and manufacturer verification.
        
        Returns:
            dict: Detailed register information including addresses and descriptions
        """
        register_info = {}
        
        for reg_name, addr in self._regdict.items():
            register_info[reg_name] = {
                "address": addr,
                "hex_address": f"0x{addr:04X}",
                "generation": self._generation,
                "category": self._categorize_register(reg_name)
            }
            
        return register_info
        
    def _categorize_register(self, reg_name: str) -> str:
        """Categorize register by function for better organization"""
        if reg_name in ["HAND_ID", "REDU_RATIO", "CLEAR_ERROR", "SAVE", "RESET_PARA"]:
            return "system_control"
        elif reg_name in ["ANGLE_SET", "POS_SET", "FORCE_SET", "SPEED_SET"]:
            return "actuator_commands"
        elif reg_name in ["ANGLE_ACT", "POS_ACT", "FORCE_ACT", "CURRENT", "ERROR", "STATUS", "TEMP"]:
            return "sensor_readings"
        elif reg_name.startswith("ACTION_SEQ"):
            return "action_sequences"
        elif reg_name.startswith("FINGER") and reg_name.endswith("_TOUCH"):
            return "touch_sensors"
        elif reg_name.startswith("IP_"):
            return "network_config"
        else:
            return "other"

    def export_register_verification_report(self, hand_id: int = 1, filepath: str = None) -> str:
        """
        Export a comprehensive report for manufacturer verification of register addresses.
        
        Args:
            hand_id: Hand ID to test with
            filepath: Optional file path to save report
            
        Returns:
            str: Report content as string
        """
        validation_results = self.validate_register_addresses(hand_id)
        register_info = self.get_register_info()
        
        report_lines = [
            "=" * 80,
            "INSPIRE HAND API - REGISTER VERIFICATION REPORT",
            "=" * 80,
            f"Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"Hardware Generation: {self._generation}",
            f"Test Hand ID: {hand_id}",
            f"Port: {self._port}",
            f"Baudrate: {self._baudrate}",
            "",
            "VALIDATION SUMMARY:",
            f"Total registers tested: {len(validation_results)}",
            f"Successful validations: {sum(validation_results.values())}",
            f"Failed validations: {len(validation_results) - sum(validation_results.values())}",
            "",
            "DETAILED REGISTER INFORMATION:",
            "-" * 80,
        ]
        
        # Group registers by category
        categories = {}
        for reg_name, info in register_info.items():
            category = info["category"]
            if category not in categories:
                categories[category] = []
            categories[category].append((reg_name, info))
            
        for category, registers in sorted(categories.items()):
            report_lines.append(f"\n{category.upper().replace('_', ' ')}:")
            report_lines.append("-" * 40)
            
            for reg_name, info in sorted(registers):
                status = "✓ PASS" if validation_results.get(reg_name, False) else "✗ FAIL"
                report_lines.append(
                    f"  {reg_name:<25} | Addr: {info['address']:<6} | {info['hex_address']:<8} | {status}"
                )
        
        report_lines.extend([
            "",
            "NOTES FOR MANUFACTURER:",
            "- Registers marked as 'FAIL' may have incorrect addresses",
            "- Please verify against the official hardware manual",
            "- Some failures may be due to hardware state or permissions",
            "- This report can help identify discrepancies for correction",
            "",
            "END REPORT",
            "=" * 80
        ])
        
        report_content = "\n".join(report_lines)
        
        if filepath:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(report_content)
                self._logger.info(f"Register verification report saved to: {filepath}")
            except Exception as e:
                self._logger.error(f"Failed to save report to {filepath}: {e}")
                
        return report_content


if __name__ == "__main__":
    pass
