from inspire_demos.inspire_serial import MODBUS_AVAILABLE, regdict, regdict_gen4
from pymodbus.client import ModbusTcpClient

import numpy as np
import numpy.typing as npt
from loguru import logger


from typing import List


class InspireHandModbus:
    """Modbus TCP interface for Inspire Hand control"""

    _logger = logger
    _client: ModbusTcpClient
    _ip: str
    _port: int
    _generation: int  # 3 for Gen3, 4 for Gen4
    _debug: bool  # Enable debug output
    _connected: bool

    def __init__(self, ip: str = "192.168.11.210", port: int = 6000, generation: int = 3, debug: bool = False):
        if not MODBUS_AVAILABLE:
            raise ImportError("pymodbus is required for ModbusTCP communication. Please install it with: pip install pymodbus")

        self._ip = ip
        self._port = port
        self._generation = generation
        self._debug = debug
        self._client = None
        self._connected = False

    @property
    def _regdict(self) -> dict:
        """Get the appropriate register dictionary based on generation"""
        if self._generation == 4:
            return regdict_gen4
        else:
            return regdict

    def connect(self) -> bool:
        """Connect to the Modbus TCP server"""
        try:
            self._client = ModbusTcpClient(self._ip, port=self._port)
            result = self._client.connect()
            self._connected = result
            if result:
                self._logger.info(f"Connected to Modbus TCP server at {self._ip}:{self._port}")
            else:
                self._logger.error(f"Failed to connect to Modbus TCP server at {self._ip}:{self._port}")
            return result
        except Exception as e:
            self._logger.error(f"Failed to connect to Modbus TCP server: {e}")
            self._connected = False
            return False

    def disconnect(self) -> bool:
        """Disconnect from the Modbus TCP server"""
        if self._client and self._connected:
            try:
                self._client.close()
                self._connected = False
                self._logger.info("Disconnected from Modbus TCP server")
                return True
            except Exception as e:
                self._logger.error(f"Failed to disconnect from Modbus TCP server: {e}")
                return False
        return True

    def is_connected(self) -> bool:
        """Check if connected to the Modbus TCP server"""
        return self._connected and self._client is not None

    def reset_error(self) -> bool:
        """Reset error status"""
        return self._write_register(self._regdict["CLEAR_ERROR"], [1])

    def return_to_zero(self) -> bool:
        """Return all joints to zero position."""
        return self.set_angle(np.array([0, 0, 0, 0, 0, 0], dtype=np.int32))

    def perform_open(self) -> bool:
        """Open the hand (set all joints to maximum position)."""
        return self.set_angle(np.array([1000, 1000, 1000, 1000, 1000, 1000], dtype=np.int32))

    def perform_close(self) -> bool:
        """Close the hand (set all joints to zero position)."""
        return self.set_angle(np.array([0, 0, 0, 0, 0, 0], dtype=np.int32))

    def set_angle(self, angles: npt.NDArray[np.integer]) -> bool:
        """Set joint angles. Accepts numpy arrays only."""
        if not isinstance(angles, np.ndarray):
            raise TypeError("angles must be a numpy.ndarray")

        # Ensure array is 1D and convert to list of integers for Modbus processing
        angles_flat = angles.flatten().astype(np.int32)

        if len(angles_flat) != 6:
            raise ValueError(f"Expected 6 angle values, got {len(angles_flat)}")

        angles_list = angles_flat.tolist()

        # Convert to 16-bit values for Modbus (handle -1 as special case)
        val_reg = []
        for angle in angles_list:
            if angle == -1:
                val_reg.append(0xFFFF)  # Special placeholder value
            else:
                val_reg.append(angle & 0xFFFF)  # Take low 16 bits

        return self._write_register(self._regdict["ANGLE_SET"], val_reg)

    def set_pos(self, positions: npt.NDArray[np.integer]) -> bool:
        """Set joint positions. Accepts numpy arrays only."""
        if not isinstance(positions, np.ndarray):
            raise TypeError("positions must be a numpy.ndarray")

        # For Modbus, position and angle are the same register
        return self.set_angle(positions)

    def set_speed(self, speeds: npt.NDArray[np.integer]) -> bool:
        """Set joint speeds. Accepts numpy arrays only."""
        if not isinstance(speeds, np.ndarray):
            raise TypeError("speeds must be a numpy.ndarray")

        # Ensure array is 1D and convert to list of integers for Modbus processing
        speeds_flat = speeds.flatten().astype(np.int32)

        if len(speeds_flat) != 6:
            raise ValueError(f"Expected 6 speed values, got {len(speeds_flat)}")

        speeds_list = speeds_flat.tolist()

        # Convert to 16-bit values for Modbus
        val_reg = []
        for speed in speeds_list:
            if speed == -1:
                val_reg.append(0xFFFF)  # Special placeholder value
            else:
                val_reg.append(speed & 0xFFFF)  # Take low 16 bits

        return self._write_register(self._regdict["SPEED_SET"], val_reg)

    def set_force(self, forces: npt.NDArray[np.integer]) -> bool:
        """Set joint forces. Accepts numpy arrays only."""
        if not isinstance(forces, np.ndarray):
            raise TypeError("forces must be a numpy.ndarray")

        # Ensure array is 1D and convert to list of integers for Modbus processing
        forces_flat = forces.flatten().astype(np.int32)

        if len(forces_flat) != 6:
            raise ValueError(f"Expected 6 force values, got {len(forces_flat)}")

        forces_list = forces_flat.tolist()

        # Convert to 16-bit values for Modbus
        val_reg = []
        for force in forces_list:
            if force == -1:
                val_reg.append(0xFFFF)  # Special placeholder value
            else:
                val_reg.append(force & 0xFFFF)  # Take low 16 bits

        return self._write_register(self._regdict["FORCE_SET"], val_reg)

    def _write_register(self, address: int, values: List[int]) -> bool:
        """Write to Modbus registers"""
        if not self.is_connected():
            self._logger.error("Modbus connection not established. Call connect() first.")
            return False

        try:
            if self._debug:
                self._logger.debug(f"Writing to register {address}: {values}")

            self._client.write_registers(address, values)
            return True
        except Exception as e:
            self._logger.error(f"Failed to write to register {address}: {e}")
            return False

    def _read_register(self, address: int, count: int) -> List[int]:
        """Read from Modbus registers"""
        if not self.is_connected():
            self._logger.error("Modbus connection not established. Call connect() first.")
            return []

        try:
            if self._debug:
                self._logger.debug(f"Reading {count} registers from address {address}")

            response = self._client.read_holding_registers(address, count=count)
            if response.isError():
                self._logger.error(f"Modbus read error from address {address}")
                return []

            result = response.registers
            if self._debug:
                self._logger.debug(f"Read {len(result)} values from register {address}: {result}")

            return result
        except Exception as e:
            self._logger.error(f"Failed to read from register {address}: {e}")
            return []

    def _read6_16bit(self, reg_name: str) -> List[int]:
        """Read 6 16-bit values from a named register"""
        if reg_name not in self._regdict:
            raise ValueError(f"Register '{reg_name}' not valid for generation {self._generation}")

        val = self._read_register(self._regdict[reg_name], 6)

        if len(val) < 6:
            if self._debug:
                self._logger.warning(f"Failed to fetch 6 values from {reg_name}")
            return []

        if self._debug:
            self._logger.info(f"Read {reg_name}: {' '.join(map(str, val))}")

        return val

    def _read6_8bit(self, reg_name: str) -> List[int]:
        """Read 6 8-bit values from a named register (3 Modbus registers split into high/low bytes)"""
        if reg_name not in self._regdict:
            raise ValueError(f"Register '{reg_name}' not valid for generation {self._generation}")

        val_act = self._read_register(self._regdict[reg_name], 3)

        if len(val_act) < 3:
            if self._debug:
                self._logger.warning(f"Failed to fetch data from {reg_name}")
            return []

        # Split each 16-bit register into high and low bytes
        results = []
        for val in val_act:
            low_byte = val & 0xFF            # Low 8 bits
            high_byte = (val >> 8) & 0xFF    # High 8 bits
            results.append(low_byte)
            results.append(high_byte)

        if self._debug:
            self._logger.info(f"Read {reg_name}: {' '.join(map(str, results))}")

        return results

    def get_angle_actual(self) -> npt.NDArray[np.int32]:
        """Get actual joint angles as numpy array."""
        result = self._read6_16bit("ANGLE_ACT")
        return np.array(result, dtype=np.int32)

    def get_angle_set(self) -> npt.NDArray[np.int32]:
        """Get set joint angles as numpy array."""
        result = self._read6_16bit("ANGLE_SET")
        return np.array(result, dtype=np.int32)

    def get_pos_actual(self) -> npt.NDArray[np.int32]:
        """Get actual joint positions as numpy array."""
        result = self._read6_16bit("ANGLE_ACT")  # Position uses same register as angle
        return np.array(result, dtype=np.int32)

    def get_pos_set(self) -> npt.NDArray[np.int32]:
        """Get set joint positions as numpy array."""
        result = self._read6_16bit("ANGLE_SET")  # Position uses same register as angle
        return np.array(result, dtype=np.int32)

    def get_speed_set(self) -> npt.NDArray[np.int32]:
        """Get set joint speeds as numpy array."""
        result = self._read6_16bit("SPEED_SET")
        return np.array(result, dtype=np.int32)

    def get_force_actual(self) -> npt.NDArray[np.int32]:
        """Get actual joint forces as numpy array."""
        result = self._read6_16bit("FORCE_ACT")
        return np.array(result, dtype=np.int32)

    def get_force_set(self) -> npt.NDArray[np.int32]:
        """Get set joint forces as numpy array."""
        result = self._read6_16bit("FORCE_SET")
        return np.array(result, dtype=np.int32)

    def get_error(self) -> npt.NDArray[np.int32]:
        """Get error codes as numpy array."""
        result = self._read6_8bit("ERROR")
        return np.array(result, dtype=np.int32)

    def get_temperature(self) -> npt.NDArray[np.int32]:
        """Get temperature values as numpy array."""
        result = self._read6_8bit("TEMP")
        return np.array(result, dtype=np.int32)

    def get_status(self) -> npt.NDArray[np.int32]:
        """Get status codes as numpy array."""
        result = self._read6_8bit("STATUS")
        return np.array(result, dtype=np.int32)

    def get_pos(self) -> npt.NDArray[np.int32]:
        """Get current position as numpy array (alias for get_pos_actual)."""
        return self.get_pos_actual()

    def set_action_sequence(self, sequence_id: int) -> bool:
        """Set the action sequence ID"""
        return self._write_register(self._regdict["ACTION_SEQ_INDEX"], [sequence_id])

    def run_action_sequence(self) -> bool:
        """Run the current action sequence"""
        return self._write_register(self._regdict["ACTION_SEQ_RUN"], [1])

    def get_tactile_data(self) -> dict[str, npt.NDArray[np.int32]]:
        """Get tactile sensor data as dictionary of numpy arrays.
        
        Returns:
            dict: Dictionary with sensor names as keys and 2D numpy arrays as values.
                 For fingers: column-first ordering (data read sequentially fills columns first)
                 For palm: row-first ordering with reversed rows (bottom-to-top, left-to-right)
        """
        if self._generation != 4:
            self._logger.error("Tactile sensors are only available in Gen 4 hardware")
            raise NotImplementedError("Tactile sensors are only available in Gen 4 hardware")
        
        tactile_sensors = {
            "PINKY_TOP_TAC": "pinky_top",
            "PINKY_TIP_TAC": "pinky_tip", 
            "PINKY_BASE_TAC": "pinky_base",
            "RING_TOP_TAC": "ring_top",
            "RING_TIP_TAC": "ring_tip",
            "RING_BASE_TAC": "ring_base", 
            "MIDDLE_TOP_TAC": "middle_top",
            "MIDDLE_TIP_TAC": "middle_tip",
            "MIDDLE_BASE_TAC": "middle_base",
            "INDEX_TOP_TAC": "index_top",
            "INDEX_TIP_TAC": "index_tip",
            "INDEX_BASE_TAC": "index_base",
            "THUMB_TOP_TAC": "thumb_top",
            "THUMB_TIP_TAC": "thumb_tip",
            "THUMB_MID_TAC": "thumb_mid",
            "THUMB_BASE_TAC": "thumb_base",
            "PALM_TAC": "palm"
        }
        
        tactile_data = {}
        
        for reg_name, friendly_name in tactile_sensors.items():
            if reg_name not in self._regdict:
                self._logger.warning(f"Tactile sensor register '{reg_name}' not found")
                continue
                
            address, shape = self._regdict[reg_name]
            rows, cols = shape
            total_elements = rows * cols
            
            # Read raw 16-bit values from Modbus registers
            raw_data = self._read_register(address, total_elements)
            
            if len(raw_data) != total_elements:
                self._logger.error(f"Failed to read complete tactile data for {friendly_name}: expected {total_elements}, got {len(raw_data)}")
                continue
            
            # Convert to numpy array of int32 (16-bit values in little-endian are already handled by pymodbus)
            data_array = np.array(raw_data, dtype=np.int32)
            
            if friendly_name == "palm":
                # Palm: Custom mapping - data points fill column by column from bottom to top
                # Data point 1 -> row 8, col 1; Data point 2 -> row 7, col 1; etc.
                matrix = data_array.reshape(cols, rows, order='C')  # Reshape as (cols, rows) first
                matrix = matrix.T  # Transpose and flip to get correct orientation
                # matrix = np.flipud(matrix.T)  # Transpose and flip to get correct orientation
            else:
                # Fingers: row-first ordering (data fills row by row, left to right)
                matrix = data_array.reshape(rows, cols, order='C')  # Row-major (C-style)
            
            tactile_data[friendly_name] = matrix
            
            if self._debug:
                self._logger.debug(f"Read {friendly_name} tactile data: {shape} matrix from address {address}")
        
        return tactile_data

    def get_tactile_sensor_data(self, sensor_name: str) -> npt.NDArray[np.int32]:
        """Get tactile data for a specific sensor.
        
        Args:
            sensor_name: Name of the sensor (e.g., 'pinky_top', 'palm', 'thumb_tip')
        
        Returns:
            2D numpy array with tactile sensor data
        """
        all_data = self.get_tactile_data()
        if sensor_name not in all_data:
            available_sensors = list(all_data.keys())
            raise ValueError(f"Sensor '{sensor_name}' not found. Available sensors: {available_sensors}")
        return all_data[sensor_name]


    def get_generation(self) -> int:
        """Get the hardware generation (3 or 4)"""
        return self._generation
    
    def get_ip(self) -> str:
        """Get the IP address of the Modbus server"""
        return self._ip
    
    def get_port(self) -> int:
        """Get the port of the Modbus server"""
        return self._port

    def set_debug(self, debug: bool) -> None:
        """Enable or disable debug output"""
        self._debug = debug

    def validate_register_addresses(self) -> dict[str, bool]:
        """
        Validate register addresses by attempting to read from each one.
        This helps identify registers that may have incorrect addresses.

        Returns:
            dict: Mapping of register names to validation status (True if readable)
        """
        if not self.is_connected():
            self._logger.error("Modbus connection not established. Call connect() first.")
            return {}

        validation_results = {}
        test_registers = [
            "HAND_ID", "ANGLE_ACT", "FORCE_ACT",
            "ERROR", "STATUS", "TEMP"
        ]

        self._logger.info("Validating register addresses for hardware compatibility...")

        for reg_name in test_registers:
            if reg_name not in self._regdict:
                validation_results[reg_name] = False
                self._logger.warning(f"Register '{reg_name}' not found in generation {self._generation} dictionary")
                continue

            try:
                # Try to read a small amount of data from each register
                if reg_name in ["ERROR", "STATUS", "TEMP"]:
                    result = self._read6_8bit(reg_name)
                else:
                    result = self._read6_16bit(reg_name)

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